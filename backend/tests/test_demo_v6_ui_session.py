from __future__ import annotations

import hashlib
import importlib.util
import json
import runpy
from pathlib import Path
from uuid import uuid4

import pytest

from app.core import demo_bundle
from app.db.base import Base
from app.modules.fees import demo_service
from app.modules.masterdata.clients.models import Client

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_demo_integrated_a_rehearsal.py"
SYSTEM_RUNTIME_TABLE_ALLOWLIST = frozenset(
    {
        "t_user",
        "t_role",
        "t_role_perm",
        "t_user_role",
        "t_doc_template",
        "t_task_template",
        "t_fee_rate_book",
        "t_fee_rate",
    }
)


def _runner_module():
    spec = importlib.util.spec_from_file_location("run_demo_integrated_a_rehearsal", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _configure_preflight(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_abc_runtime_bundle.py"))
    )
    bundle, _manifest, manifest_sha = helpers["_valid_v6_bundle"](tmp_path)
    authority_sha = hashlib.sha256((bundle / "authority.json").read_bytes()).hexdigest()
    values = {
        "FPMS_ENV": "demo",
        "FPMS_DEMO_SCOPE": "LOCAL_ABC_E2E",
        "FPMS_DEMO_RUN_PROFILE": "TECHNICAL_REHEARSAL",
        "FPMS_DEMO_RUN_ID": "ui-session-contract",
        "FPMS_DEMO_BUNDLE_PATH": str(bundle),
        "FPMS_DEMO_EXPECTED_MANIFEST_SHA256": manifest_sha,
        "FPMS_DEMO_EXPECTED_AUTHORITY_SHA256": authority_sha,
        "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION": "SYNTHETIC_TEST_ONLY",
        "FPMS_DEMO_CANDIDATE_COMMIT": "a" * 40,
        "FPMS_DEMO_CANDIDATE_TREE": "b" * 40,
        "FPMS_DEMO_CONTRACT_VERSION": "fpms.demo-ui-session/v1",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(demo_bundle, "_current_demo_date", lambda: helpers["date"](2026, 8, 21))
    return authority_sha


def test_preflight_derives_every_business_table_and_rejects_any_nonzero_count(
    client,
    auth_headers,
    session_factory,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    authority_sha = _configure_preflight(tmp_path / "bundle", monkeypatch)
    expected_business_tables = sorted(
        set(Base.metadata.tables) - SYSTEM_RUNTIME_TABLE_ALLOWLIST
    )

    assert demo_service.SYSTEM_RUNTIME_TABLE_ALLOWLIST == SYSTEM_RUNTIME_TABLE_ALLOWLIST
    assert "t_grant_fee_task" in expected_business_tables
    assert {
        "t_official_work_package",
        "t_official_work_package_checklist",
        "t_official_work_package_manifest",
        "t_official_work_package_receipt",
        "t_official_work_package_override",
    } <= set(expected_business_tables)
    response = client.get("/api/v1/fees/demo-preflight", headers=auth_headers)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert list(payload["business_counts"]) == expected_business_tables
    assert set(payload["business_counts"].values()) == {0}
    assert payload["run_id"] == "ui-session-contract"
    assert payload["candidate_commit"] == "a" * 40
    assert payload["candidate_tree"] == "b" * 40
    assert payload["authority_sha256"] == authority_sha
    assert payload["contract_version"] == "fpms.demo-ui-session/v1"

    with session_factory() as db:
        db.add(
            Client(
                id=str(uuid4()),
                client_code="UI-SESSION-NOT-FRESH",
                name_cn="非空业务库",
                client_type="CLIENT",
                default_currency="CNY",
                is_active=True,
            )
        )
        db.commit()

    not_fresh = client.get("/api/v1/fees/demo-preflight", headers=auth_headers)
    assert not_fresh.status_code == 409
    assert not_fresh.json()["error"]["code"] == "DEMO_RUN_NOT_FRESH"


class _Process:
    def __init__(self) -> None:
        self.returncode = None
        self.signals: list[int] = []

    def poll(self):
        return self.returncode

    def send_signal(self, value: int) -> None:
        self.signals.append(value)
        self.returncode = 0

    def terminate(self) -> None:
        self.returncode = 0

    def kill(self) -> None:
        self.returncode = -9

    def wait(self, timeout=None):
        return self.returncode


def _exercise_ui_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    finalization: str,
):
    module = _runner_module()
    artifact = (tmp_path / f"artifact-{finalization.lower()}").resolve()
    bundle = tmp_path / "bundle"
    bundle.mkdir(exist_ok=True)
    processes: list[_Process] = []
    secrets = iter(("admin-secret", "reviewer-secret", "jwt-secret"))
    monkeypatch.setattr(module.secrets, "token_hex", lambda _size: "abcdef123456")
    monkeypatch.setattr(module.secrets, "token_urlsafe", lambda _size: next(secrets))
    monkeypatch.setattr(module.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(module.abc, "wait_url", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("builtins.input", lambda _prompt: finalization)

    def popen_spy(command, **kwargs):
        process = _Process()
        processes.append(process)
        if len(processes) == 1:
            env = kwargs["env"]
            run_root = Path(module.tempfile.gettempdir()) / (
                f"fpms-demo-abc-{env['FPMS_DEMO_RUN_ID']}"
            )
            run_root.mkdir()
            (run_root / "fpms-demo.db").write_bytes(b"sqlite")
        return process

    monkeypatch.setattr(module.subprocess, "Popen", popen_spy)
    args = module.parse_args(
        ["--ui-session", "--actor", "HUMAN", "--artifact", str(artifact)]
    )
    candidate = {"commit": "c" * 40, "tree": "d" * 40}
    module._run_ui_session(args, bundle, "e" * 64, "f" * 64, candidate)

    session = json.loads((artifact / "session.json").read_text(encoding="utf-8"))
    binding = json.loads(
        (artifact / "observer" / "finalize-binding.json").read_text(encoding="utf-8")
    )
    output = capsys.readouterr().out
    assert len(processes) == 2
    assert "playwright" in binding["browser_command"][1]
    assert binding["browser_command"][2] == "open"
    assert "--headless" not in binding["browser_command"]
    assert binding["observer_artifact_root"] == str((artifact / "observer").resolve())
    assert binding["run_id"] == session["run_id"]
    assert "admin-secret" not in output + json.dumps(binding) + json.dumps(session)
    assert "reviewer-secret" not in output + json.dumps(binding) + json.dumps(session)
    assert '"password": "<redacted>"' in output
    return module, artifact, Path(session["run_root"])


def test_ui_session_stop_preserves_exact_run_and_redacted_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    _module, artifact, run_root = _exercise_ui_session(
        tmp_path, monkeypatch, capsys, "STOP"
    )

    assert run_root.is_dir()
    assert artifact.is_dir()
    status = json.loads(
        (artifact / "observer" / "session-status.json").read_text(encoding="utf-8")
    )
    assert status["status"] == "STOPPED"
    assert status["run_root_removed"] is False


def test_ui_session_explicit_success_alone_cleans_the_validated_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    _module, artifact, run_root = _exercise_ui_session(
        tmp_path, monkeypatch, capsys, "FINALIZE_SUCCESS"
    )

    assert not run_root.exists()
    assert artifact.is_dir()
    status = json.loads(
        (artifact / "observer" / "session-status.json").read_text(encoding="utf-8")
    )
    assert status["status"] == "FINALIZED"
    assert status["run_root_removed"] is True


def test_ui_session_cli_rejects_invalid_combinations_before_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module = _runner_module()
    artifact = tmp_path / "relative-artifact"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        module.abc,
        "candidate_identity",
        lambda: pytest.fail("candidate capture is a forbidden side effect"),
    )

    invalid = (
        ["--ui-session", "--artifact", str(artifact)],
        ["--ui-session", "--actor", "HUMAN", "--artifact", "relative"],
        [
            "--ui-session",
            "--actor",
            "CODEX",
            "--artifact",
            str(artifact.resolve()),
            "--profile",
            "TECHNICAL_REHEARSAL",
        ],
        ["--actor", "HUMAN", "--artifact", str(artifact.resolve())],
    )
    for argv in invalid:
        with pytest.raises(SystemExit):
            module.main(argv)
    assert not artifact.exists()


def test_default_integrated_a_cli_contract_remains_compatible():
    module = _runner_module()

    args = module.parse_args(["--profile", "TECHNICAL_REHEARSAL"])

    assert args.ui_session is False
    assert args.actor is None
    assert args.artifact == module.DEFAULT_ARTIFACT
    assert args.runs == 2
    assert args.headless is False
