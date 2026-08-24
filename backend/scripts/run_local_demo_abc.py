from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.demo_bundle import (
    DemoBundleSnapshot,
    demo_bundle_forbidden_roots,
    demo_official_fee_row_sha256,
    load_demo_bundle,
)
from app.models import *  # noqa: F401, F403 - register the complete ORM graph before seeding
from app.modules.auth.models import T_User
from app.modules.documents.models import DocTemplate
from app.modules.documents.official_notice_catalog import (
    seed_fee_reduction_approval_official_notice_catalog,
)
from app.modules.fees.models import FeeRate, OfficialRateBook
from app.modules.fees.official_rate_book import (
    ActivateOfficialRateBookCommand,
    activate_official_rate_book,
)
from app.modules.tasks.models import TaskTemplate
from scripts.seed_demo_abc import DemoIdentity, seed_demo_identities

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = _REPO_ROOT / "backend"
_FRONTEND_ROOT = _REPO_ROOT / "frontend"
_RUN_ID_RE = re.compile(r"[A-Za-z0-9._-]{1,96}")


@dataclass(frozen=True)
class DemoRun:
    run_id: str
    run_root: Path
    database_path: Path
    storage_path: Path
    bundle: DemoBundleSnapshot


def _required_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"required environment variable is missing: {name}")
    return value


def _validated_identity(username_key: str, password_key: str, display_name: str) -> DemoIdentity:
    username = _required_env(username_key)
    password = _required_env(password_key)
    if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", username) is None:
        raise RuntimeError(f"{username_key} has invalid format")
    if not 12 <= len(password) <= 72:
        raise RuntimeError(f"{password_key} must contain 12..72 characters")
    return DemoIdentity(username=username, password=password, display_name=display_name)


def _preflight() -> tuple[str, DemoBundleSnapshot, DemoIdentity, DemoIdentity, str]:
    if _required_env("FPMS_ENV") != "demo":
        raise RuntimeError("FPMS_ENV must be demo")
    if _required_env("FPMS_DEMO_SCOPE") != "LOCAL_ABC_E2E":
        raise RuntimeError("FPMS_DEMO_SCOPE must be LOCAL_ABC_E2E")
    run_profile = _required_env("FPMS_DEMO_RUN_PROFILE")
    run_id = _required_env("FPMS_DEMO_RUN_ID")
    if _RUN_ID_RE.fullmatch(run_id) is None:
        raise RuntimeError("FPMS_DEMO_RUN_ID has invalid format")
    jwt_secret = _required_env("JWT_SECRET")
    if len(jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 characters for the local demo")

    bundle_path = Path(_required_env("FPMS_DEMO_BUNDLE_PATH"))
    forbidden_roots = demo_bundle_forbidden_roots(
        bundle_path,
        run_id=run_id,
        configured_storage=os.environ.get("STORAGE_DIR"),
    )
    bundle = load_demo_bundle(
        bundle_path,
        expected_manifest_sha256=_required_env("FPMS_DEMO_EXPECTED_MANIFEST_SHA256"),
        expected_authority_sha256=_required_env("FPMS_DEMO_EXPECTED_AUTHORITY_SHA256"),
        expected_authority_classification=_required_env(
            "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION"
        ),
        repo_root=_REPO_ROOT,
        forbidden_roots=forbidden_roots,
    )
    required_profile = (
        "TECHNICAL_REHEARSAL"
        if bundle.authority_classification == "SYNTHETIC_TEST_ONLY"
        else "CUSTOMER_DEMO"
    )
    if run_profile != required_profile:
        raise RuntimeError(
            f"{bundle.authority_classification} requires {required_profile} run profile"
        )
    operator = _validated_identity(
        "FPMS_DEMO_ADMIN_USERNAME",
        "FPMS_DEMO_ADMIN_PASSWORD",
        "本地演示操作员",
    )
    reviewer = _validated_identity(
        "FPMS_DEMO_REVIEWER_USERNAME",
        "FPMS_DEMO_REVIEWER_PASSWORD",
        "本地证据复核员",
    )
    if operator.username == reviewer.username or operator.password == reviewer.password:
        raise RuntimeError("demo operator and reviewer credentials must be distinct")
    return run_id, bundle, operator, reviewer, jwt_secret


def _sqlite_engine(database_url: str):
    engine = create_engine(database_url, future=True, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    return engine


def _materialize_bundle(bundle: DemoBundleSnapshot, run_root: Path) -> DemoBundleSnapshot:
    target = run_root / "input" / bundle.manifest_sha256
    shutil.copytree(bundle.bundle_root, target, symlinks=False)
    copied = load_demo_bundle(
        target,
        expected_manifest_sha256=bundle.manifest_sha256,
        expected_authority_sha256=bundle.authority_sha256,
        expected_authority_classification=bundle.authority_classification,
        repo_root=_REPO_ROOT,
    )
    for path in sorted(target.rglob("*"), reverse=True):
        path.chmod(0o555 if path.is_dir() else 0o444)
    target.chmod(0o555)
    (run_root / "input").chmod(0o555)
    os.environ["FPMS_DEMO_BUNDLE_PATH"] = str(target)
    return copied


def _candidate_identity() -> tuple[str, str]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=_REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    tree = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=_REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    return commit, tree


def seed_demo_task_templates(db: Session) -> None:
    rows = (
        {
            "code": "OA_REPLY",
            "name": "OA答复期限",
            "add_days": 120,
            "inner_offset_days": 14,
            "description": "审查意见通知书答复期限自动任务",
        },
        {
            "code": "OA_REPLY_SUBSEQUENT",
            "name": "后续审查意见答复期限",
            "add_days": None,
            "inner_offset_days": None,
            "description": "第二次及以后审查意见答复任务；截止日必须使用官文载明的明确期限",
        },
    )
    for row in rows:
        existing = db.query(TaskTemplate).filter(TaskTemplate.code == row["code"]).one_or_none()
        if existing is not None:
            actual = {
                "code": existing.code,
                "name": existing.name,
                "add_days": existing.add_days,
                "inner_offset_days": existing.inner_offset_days,
                "description": existing.description,
            }
            if actual != row:
                raise RuntimeError(f"demo task-template configuration conflicts: {row['code']}")
            continue
        db.add(TaskTemplate(id=str(uuid4()), enabled=True, **row))
    db.flush()


def seed_demo_oa_out_template(db: Session) -> None:
    expected = {
        "code": "OA_OUT",
        "name": "审查意见答复书（发文）",
        "direction": "OUT",
        "need_reply": False,
        "deadline_template_code": None,
        "status_effect": None,
        "status_restore": None,
        "fee_draft_type": None,
        "fee_item_list": None,
        "reply_to_template_code": "OA_IN",
        "input_fields": None,
    }
    existing = db.query(DocTemplate).filter(DocTemplate.code == expected["code"]).one_or_none()
    if existing is not None:
        actual = {field: getattr(existing, field) for field in expected}
        if actual != expected:
            raise RuntimeError("demo document-template configuration conflicts: OA_OUT")
        return
    db.add(DocTemplate(id=str(uuid4()), enabled=True, **expected))
    db.flush()


def _materialize_official_fee_source(
    db: Session,
    *,
    bundle: DemoBundleSnapshot,
    reviewer_username: str,
) -> None:
    source = bundle.official_fee_source
    if source is None:
        return
    selector = bundle.official_fee_selector
    if selector is None:
        raise RuntimeError("V6 official fee source requires a selector")

    reviewer = db.scalar(select(T_User).where(T_User.username == reviewer_username))
    if reviewer is None:
        raise RuntimeError("demo reviewer is unavailable for official fee activation")
    activated_at = datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)

    source_book = source.rate_book
    candidate = OfficialRateBook(
        book_code=source_book.book_code,
        version_code=source_book.version_code,
        source_authority=source_book.source_authority,
        source_reference=source_book.source_reference,
        source_version=source_book.source_version,
        source_published_on=source_book.source_published_on,
        source_snapshot=source_book.source_snapshot,
        source_snapshot_hash=source_book.source_snapshot_hash,
        effective_from=source_book.effective_from,
        effective_to=source_book.effective_to,
        approval_status="PENDING",
        activation_status="INACTIVE",
    )
    db.add(candidate)
    db.flush()
    db.add_all(
        FeeRate(**vars(row), official_rate_book_id=candidate.id)
        for row in source.rows
    )
    db.flush()

    result = activate_official_rate_book(
        ActivateOfficialRateBookCommand(
            rate_book_id=candidate.id,
            approved_by=reviewer.id,
            approved_at=activated_at,
            activated_by=reviewer.id,
            activated_at=activated_at,
            expected_current_rate_book_id=None,
        ),
        db,
    )
    db.flush()
    db.expire_all()

    stored_books = db.scalars(select(OfficialRateBook)).all()
    if len(stored_books) != 1:
        raise RuntimeError("fresh demo must contain exactly one official rate book")
    stored_book = stored_books[0]
    expected_book_facts = (
        source_book.book_code,
        source_book.version_code,
        source_book.source_authority,
        source_book.source_reference,
        source_book.source_version,
        source_book.source_published_on,
        source_book.source_snapshot,
        source_book.source_snapshot_hash,
        source_book.effective_from,
        source_book.effective_to,
    )
    actual_book_facts = (
        stored_book.book_code,
        stored_book.version_code,
        stored_book.source_authority,
        stored_book.source_reference,
        stored_book.source_version,
        stored_book.source_published_on,
        stored_book.source_snapshot,
        stored_book.source_snapshot_hash,
        stored_book.effective_from,
        stored_book.effective_to,
    )
    expected_identity = f"CNIPA|{source_book.book_code}"
    if (
        actual_book_facts != expected_book_facts
        or result.rate_book_id != stored_book.id
        or result.book_code != source_book.book_code
        or result.version_code != source_book.version_code
        or result.approval_status != "APPROVED"
        or result.activation_status != "ACTIVE"
        or stored_book.approval_status != "APPROVED"
        or stored_book.activation_status != "ACTIVE"
        or stored_book.approved_by != reviewer.id
        or stored_book.activated_by != reviewer.id
        or stored_book.approved_at != activated_at
        or stored_book.activated_at != activated_at
        or stored_book.current_identity_key != expected_identity
        or hashlib.sha256(stored_book.source_snapshot.encode("utf-8")).hexdigest()
        != source_book.source_snapshot_hash
    ):
        raise RuntimeError("materialized official rate book verification failed")

    stored_rows = db.scalars(select(FeeRate)).all()
    stored_by_code = {row.fee_code: row for row in stored_rows}
    selector_hashes = dict(selector.fee_row_sha256s)
    if (
        len(stored_rows) != len(source.rows)
        or set(stored_by_code) != set(selector.fee_codes)
    ):
        raise RuntimeError("materialized official fee row set verification failed")
    for fee_code in selector.fee_codes:
        row = stored_by_code[fee_code]
        if (
            row.official_rate_book_id != stored_book.id
            or demo_official_fee_row_sha256(row) != selector_hashes[fee_code]
        ):
            raise RuntimeError("materialized official fee row verification failed")


def bootstrap_demo_run() -> DemoRun:
    run_id, bundle, operator, reviewer, jwt_secret = _preflight()
    run_root = Path(tempfile.gettempdir()) / f"fpms-demo-abc-{run_id}"
    if run_root.exists() or run_root.is_symlink():
        raise RuntimeError(f"demo run ID already exists: {run_id}")

    engine = None
    run_root.mkdir()
    try:
        bundle = _materialize_bundle(bundle, run_root)
        storage_path = run_root / "storage"
        database_path = run_root / "fpms-demo.db"
        storage_path.mkdir()
        database_url = f"sqlite:///{database_path}"
        os.environ.update(
            DATABASE_URL=database_url,
            STORAGE_DIR=str(storage_path),
            JWT_SECRET=jwt_secret,
            CORS_ORIGINS='["http://localhost:5173","http://127.0.0.1:5173"]',
        )
        get_settings.cache_clear()

        alembic_config = Config(str(_BACKEND_ROOT / "alembic.ini"))
        alembic_config.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
        alembic_config.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(alembic_config, "head")

        engine = _sqlite_engine(database_url)
        factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        with factory() as db:
            catalog_count = seed_fee_reduction_approval_official_notice_catalog(db)
            if catalog_count != 60:
                raise RuntimeError(
                    f"fresh demo official-notice catalog must contain 60 rows; changed={catalog_count}"
                )
            seed_demo_task_templates(db)
            seed_demo_oa_out_template(db)
            seed_demo_identities(db, operator=operator, reviewer=reviewer)
            with db.begin():
                _materialize_official_fee_source(
                    db,
                    bundle=bundle,
                    reviewer_username=reviewer.username,
                )
        engine.dispose()
        engine = None

        candidate_commit, candidate_tree = _candidate_identity()
        metadata = {
            "run_id": run_id,
            "candidate_commit": candidate_commit,
            "candidate_tree": candidate_tree,
            "run_profile": os.environ["FPMS_DEMO_RUN_PROFILE"],
            "bundle_id": bundle.bundle_id,
            "bundle_version": bundle.bundle_version,
            "manifest_sha256": bundle.manifest_sha256,
            "authority_sha256": bundle.authority_sha256,
            "authority_classification": bundle.authority_classification,
            "customer_activation_eligible": bundle.customer_activation_eligible,
            "approved_by": bundle.approved_by,
            "approved_at": bundle.approved_at,
            "evaluated_date": bundle.local_date.isoformat(),
            "timezone": "Asia/Shanghai",
            "operator_username": operator.username,
            "reviewer_username": reviewer.username,
            "database_path": str(database_path),
            "storage_path": str(storage_path),
        }
        (run_root / "run-metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
        )
        return DemoRun(
            run_id=run_id,
            run_root=run_root,
            database_path=database_path,
            storage_path=storage_path,
            bundle=bundle,
        )
    except Exception:
        try:
            if engine is not None:
                engine.dispose()
        finally:
            if run_root.exists() and not run_root.is_symlink():
                run_root.chmod(0o755)
                for path in run_root.rglob("*"):
                    if path.is_dir() and not path.is_symlink():
                        path.chmod(0o755)
                shutil.rmtree(run_root)
        raise


def _assert_port_available(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError as exc:
            raise RuntimeError(f"local demo port is already in use: {port}") from exc


def _assert_launch_dependencies() -> None:
    if shutil.which("npm") is None:
        raise RuntimeError("npm is required to start the local demo UI")
    if not (_FRONTEND_ROOT / "node_modules" / ".bin" / "vite").is_file():
        raise RuntimeError("frontend dependencies are missing; run npm ci in frontend first")
    _assert_port_available(8000)
    _assert_port_available(5173)


def _wait_for_backend_ready(process: subprocess.Popen, timeout_seconds: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        returncode = process.poll()
        if returncode is not None:
            raise RuntimeError(f"backend exited before health check: {returncode}")
        connection = http.client.HTTPConnection("127.0.0.1", 8000, timeout=1.0)
        try:
            connection.request("GET", "/healthz")
            if connection.getresponse().status == 200:
                return
        except OSError:
            pass
        finally:
            connection.close()
        time.sleep(0.1)
    raise RuntimeError("backend did not become healthy within 30 seconds")


def _serve(run: DemoRun) -> int:
    backend_env = os.environ.copy()
    frontend_env = os.environ.copy()
    frontend_env["VITE_API_BASE_URL"] = "/api/v1"
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=_BACKEND_ROOT,
        env=backend_env,
    )
    processes = [backend_process]
    try:
        _wait_for_backend_ready(backend_process)
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
            cwd=_FRONTEND_ROOT,
            env=frontend_env,
        )
        processes.append(frontend_process)
        print(f"FPMS local ABC demo: http://127.0.0.1:5173 (run_id={run.run_id})")
        while all(process.poll() is None for process in processes):
            time.sleep(0.25)
        return next((process.returncode for process in processes if process.returncode), 0)
    except KeyboardInterrupt:
        return 130
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local FPMS ABC demo")
    parser.add_argument("--bootstrap-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.bootstrap_only:
        _assert_launch_dependencies()
    run = bootstrap_demo_run()
    if args.bootstrap_only:
        print(run.run_root)
        return 0
    return _serve(run)


if __name__ == "__main__":
    raise SystemExit(main())
