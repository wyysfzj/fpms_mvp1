from __future__ import annotations

import argparse
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
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.demo_bundle import DemoBundleSnapshot, load_demo_bundle
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
    run_id = _required_env("FPMS_DEMO_RUN_ID")
    if _RUN_ID_RE.fullmatch(run_id) is None:
        raise RuntimeError("FPMS_DEMO_RUN_ID has invalid format")
    jwt_secret = _required_env("JWT_SECRET")
    if len(jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 characters for the local demo")

    bundle = load_demo_bundle(
        Path(_required_env("FPMS_DEMO_BUNDLE_PATH")),
        expected_manifest_sha256=_required_env("FPMS_DEMO_EXPECTED_MANIFEST_SHA256"),
        repo_root=_REPO_ROOT,
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


def bootstrap_demo_run() -> DemoRun:
    run_id, bundle, operator, reviewer, jwt_secret = _preflight()
    run_root = Path(tempfile.gettempdir()) / f"fpms-demo-abc-{run_id}"
    if run_root.exists() or run_root.is_symlink():
        raise RuntimeError(f"demo run ID already exists: {run_id}")

    storage_path = run_root / "storage"
    database_path = run_root / "fpms-demo.db"
    storage_path.mkdir(parents=True)
    database_url = f"sqlite:///{database_path}"
    os.environ.update(
        DATABASE_URL=database_url,
        STORAGE_DIR=str(storage_path),
        JWT_SECRET=jwt_secret,
        CORS_ORIGINS='["http://localhost:5173","http://127.0.0.1:5173"]',
    )
    get_settings.cache_clear()

    alembic_config = Config(str(_BACKEND_ROOT / "alembic.ini"))
    alembic_config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_config, "head")

    engine = _sqlite_engine(database_url)
    try:
        factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        with factory() as db:
            seed_demo_identities(db, operator=operator, reviewer=reviewer)
    finally:
        engine.dispose()

    metadata = {
        "run_id": run_id,
        "bundle_id": bundle.bundle_id,
        "bundle_version": bundle.bundle_version,
        "manifest_sha256": bundle.manifest_sha256,
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


def _assert_port_available(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
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


def _serve(run: DemoRun) -> int:
    backend_env = os.environ.copy()
    frontend_env = os.environ.copy()
    frontend_env["VITE_API_BASE_URL"] = "http://127.0.0.1:8000/api/v1"
    processes = [
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=_BACKEND_ROOT,
            env=backend_env,
        ),
        subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
            cwd=_FRONTEND_ROOT,
            env=frontend_env,
        ),
    ]
    print(f"FPMS local ABC demo: http://127.0.0.1:5173 (run_id={run.run_id})")
    try:
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
