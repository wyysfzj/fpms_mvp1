from __future__ import annotations

import hashlib
import os
import runpy
import sqlite3
from pathlib import Path

import pytest

from app.core.demo_bundle import DemoBundleError

try:
    from scripts import run_local_demo_abc, validate_demo_bundle
except ImportError:
    run_local_demo_abc = None
    validate_demo_bundle = None


def _bundle(tmp_path: Path):
    helpers = runpy.run_path(str(Path(__file__).with_name("test_demo_abc_runtime_bundle.py")))
    return helpers["_valid_bundle"](tmp_path)


def _configure(monkeypatch: pytest.MonkeyPatch, root: Path, digest: str, run_id: str) -> None:
    values = {
        "FPMS_ENV": "demo",
        "FPMS_DEMO_SCOPE": "LOCAL_ABC_E2E",
        "FPMS_DEMO_RUN_PROFILE": "TECHNICAL_REHEARSAL",
        "FPMS_DEMO_RUN_ID": run_id,
        "FPMS_DEMO_BUNDLE_PATH": str(root),
        "FPMS_DEMO_EXPECTED_MANIFEST_SHA256": digest,
        "FPMS_DEMO_EXPECTED_AUTHORITY_SHA256": hashlib.sha256(
            (root / "authority.json").read_bytes()
        ).hexdigest(),
        "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION": "SYNTHETIC_TEST_ONLY",
        "FPMS_DEMO_ADMIN_USERNAME": "admin",
        "FPMS_DEMO_ADMIN_PASSWORD": "local-demo-admin-pass",
        "FPMS_DEMO_REVIEWER_USERNAME": "demo_evidence_reviewer",
        "FPMS_DEMO_REVIEWER_PASSWORD": "local-demo-reviewer-pass",
        "JWT_SECRET": "local-demo-jwt-secret-value-32-bytes-minimum",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_invalid_bundle_creates_no_run_directory(tmp_path: Path, monkeypatch):
    assert run_local_demo_abc is not None, "local runner is not implemented"
    root, _manifest, digest = _bundle(tmp_path / "input")
    with (root / "manifest.json").open("ab") as stream:
        stream.write(b"tampered")
    _configure(monkeypatch, root, digest, "invalid-input")
    monkeypatch.setattr(run_local_demo_abc.tempfile, "gettempdir", lambda: str(tmp_path))

    with pytest.raises(DemoBundleError, match="manifest digest"):
        run_local_demo_abc.bootstrap_demo_run()

    assert not (tmp_path / "fpms-demo-abc-invalid-input").exists()


def test_synthetic_bundle_requires_technical_rehearsal_profile(tmp_path: Path, monkeypatch):
    root, _manifest, digest = _bundle(tmp_path / "input")
    _configure(monkeypatch, root, digest, "wrong-profile")
    monkeypatch.setenv("FPMS_DEMO_RUN_PROFILE", "CUSTOMER_DEMO")
    monkeypatch.setattr(run_local_demo_abc.tempfile, "gettempdir", lambda: str(tmp_path))

    with pytest.raises(RuntimeError, match="requires TECHNICAL_REHEARSAL"):
        run_local_demo_abc.bootstrap_demo_run()

    assert not (tmp_path / "fpms-demo-abc-wrong-profile").exists()


def test_validator_and_runner_reject_the_same_product_storage_root(
    tmp_path: Path, monkeypatch
):
    storage_root = tmp_path / "product-storage"
    root, _manifest, digest = _bundle(storage_root / "input")
    _configure(monkeypatch, root, digest, "storage-boundary")
    monkeypatch.setenv("STORAGE_DIR", str(storage_root))

    with pytest.raises(DemoBundleError, match="product and run storage"):
        validate_demo_bundle.main()
    with pytest.raises(DemoBundleError, match="product and run storage"):
        run_local_demo_abc._preflight()


def test_validator_and_runner_reject_the_same_prior_run_root(tmp_path: Path, monkeypatch):
    root, _manifest, digest = _bundle(tmp_path / "fpms-demo-abc-prior" / "input")
    _configure(monkeypatch, root, digest, "new-run")

    with pytest.raises(DemoBundleError, match="existing run directory"):
        validate_demo_bundle.main()
    with pytest.raises(DemoBundleError, match="existing run directory"):
        run_local_demo_abc._preflight()


def test_fresh_bootstrap_seeds_only_two_demo_users_and_rejects_reuse(
    tmp_path: Path, monkeypatch
):
    assert run_local_demo_abc is not None, "local runner is not implemented"
    root, _manifest, digest = _bundle(tmp_path / "input")
    _configure(monkeypatch, root, digest, "fresh-run")
    monkeypatch.setattr(run_local_demo_abc.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.chdir(tmp_path)

    result = run_local_demo_abc.bootstrap_demo_run()

    assert result.run_root == tmp_path / "fpms-demo-abc-fresh-run"
    assert result.database_path.is_file()
    assert result.bundle.template.path.is_relative_to(result.run_root / "input")
    assert result.bundle.authority_sha256
    assert result.bundle.authority_classification == "SYNTHETIC_TEST_ONLY"
    assert result.bundle.customer_activation_eligible is False
    assert os.environ["FPMS_DEMO_BUNDLE_PATH"] == str(result.bundle.template.path.parents[1])
    for path in (result.run_root / "input").rglob("*"):
        assert path.stat().st_mode & 0o222 == 0
    with sqlite3.connect(result.database_path) as connection:
        users = connection.execute(
            "SELECT username, password_hash FROM t_user ORDER BY username"
        ).fetchall()
        assert [row[0] for row in users] == ["admin", "demo_evidence_reviewer"]
        assert users[0][1] != users[1][1]
        for table in ["t_client", "t_case", "t_template", "t_fee_rate", "t_doc_template"]:
            assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0

    with pytest.raises(RuntimeError, match="run ID already exists"):
        run_local_demo_abc.bootstrap_demo_run()

    metadata = (result.run_root / "run-metadata.json").read_text()
    assert result.bundle.authority_sha256 in metadata
    assert '"candidate_commit":' in metadata
    assert '"candidate_tree":' in metadata
    assert '"customer_activation_eligible": false' in metadata


def test_port_probe_enables_address_reuse_before_bind(monkeypatch):
    assert run_local_demo_abc is not None, "local runner is not implemented"
    calls: list[tuple] = []

    class FakeSocket:
        def __init__(self, *_args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def setsockopt(self, level, option, value):
            calls.append(("setsockopt", level, option, value))

        def bind(self, address):
            calls.append(("bind", address))

    monkeypatch.setattr(run_local_demo_abc.socket, "socket", FakeSocket)

    run_local_demo_abc._assert_port_available(8000)

    assert calls == [
        (
            "setsockopt",
            run_local_demo_abc.socket.SOL_SOCKET,
            run_local_demo_abc.socket.SO_REUSEADDR,
            1,
        ),
        ("bind", ("127.0.0.1", 8000)),
    ]


def test_port_probe_preserves_active_listener_failure(monkeypatch):
    assert run_local_demo_abc is not None, "local runner is not implemented"

    class BusySocket:
        def __init__(self, *_args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def setsockopt(self, *_args):
            return None

        def bind(self, _address):
            raise OSError("busy")

    monkeypatch.setattr(run_local_demo_abc.socket, "socket", BusySocket)

    with pytest.raises(RuntimeError, match="local demo port is already in use: 5173"):
        run_local_demo_abc._assert_port_available(5173)
