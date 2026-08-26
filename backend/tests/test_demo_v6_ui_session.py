from __future__ import annotations

import hashlib
import importlib.util
import json
import runpy
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from uuid import uuid4

import pytest

from app.core import demo_bundle
from app.db.base import Base
from app.modules.fees import demo_service
from app.modules.masterdata.clients.models import Client
from scripts import run_local_demo_abc

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_demo_integrated_a_rehearsal.py"
UI_PARITY_CONTRACT = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack"
    / "data"
    / "testcases"
    / "demo_v6_ui_parity_v1.json"
)
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


def _configure_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    ui_session: bool,
) -> str:
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_abc_runtime_bundle.py"))
    )
    bundle, _manifest, manifest_sha = helpers["_valid_v6_bundle"](tmp_path)
    authority_sha = hashlib.sha256((bundle / "authority.json").read_bytes()).hexdigest()
    values: dict[str, str] = {
        "FPMS_ENV": "demo",
        "FPMS_DEMO_SCOPE": "LOCAL_ABC_E2E",
        "FPMS_DEMO_RUN_PROFILE": "TECHNICAL_REHEARSAL",
        "FPMS_DEMO_BUNDLE_PATH": str(bundle),
        "FPMS_DEMO_EXPECTED_MANIFEST_SHA256": manifest_sha,
        "FPMS_DEMO_EXPECTED_AUTHORITY_SHA256": authority_sha,
        "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION": "SYNTHETIC_TEST_ONLY",
    }
    if ui_session:
        schema_id = json.loads(UI_PARITY_CONTRACT.read_text(encoding="utf-8"))[
            "schema_id"
        ]
        values.update(
            FPMS_DEMO_UI_SESSION="1",
            FPMS_DEMO_RUN_ID="ui-session-contract",
            FPMS_DEMO_CANDIDATE_COMMIT="a" * 40,
            FPMS_DEMO_CANDIDATE_TREE="b" * 40,
            FPMS_DEMO_CONTRACT_VERSION=schema_id,
        )
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
    authority_sha = _configure_preflight(
        tmp_path / "bundle", monkeypatch, ui_session=True
    )
    schema_id = json.loads(UI_PARITY_CONTRACT.read_text(encoding="utf-8"))["schema_id"]
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
    assert payload["contract_version"] == schema_id
    assert demo_service._UI_SESSION_CONTRACT_VERSION == schema_id

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


def test_existing_a_preflight_stays_200_with_optional_session_identity(
    client,
    auth_headers,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    authority_sha = _configure_preflight(
        tmp_path / "bundle", monkeypatch, ui_session=False
    )

    response = client.get("/api/v1/fees/demo-preflight", headers=auth_headers)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["readiness"] == "READY"
    assert payload["run_id"] is None
    assert payload["candidate_commit"] is None
    assert payload["candidate_tree"] is None
    assert payload["contract_version"] is None
    assert payload["authority_sha256"] == authority_sha


def test_ui_session_preflight_requires_exact_session_identity(
    client,
    auth_headers,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _configure_preflight(tmp_path / "bundle", monkeypatch, ui_session=True)
    monkeypatch.delenv("FPMS_DEMO_CANDIDATE_TREE")

    response = client.get("/api/v1/fees/demo-preflight", headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DEMO_INPUT_CONFIG_REQUIRED"

    monkeypatch.setenv("FPMS_DEMO_CANDIDATE_TREE", "b" * 40)
    monkeypatch.setenv("FPMS_DEMO_CONTRACT_VERSION", "wrong-contract")
    wrong_contract = client.get("/api/v1/fees/demo-preflight", headers=auth_headers)
    assert wrong_contract.status_code == 409
    assert wrong_contract.json()["error"]["code"] == "DEMO_INPUT_CONFIG_REQUIRED"


class _BrowserProcess:
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


def _real_ui_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module = _runner_module()
    monkeypatch.setattr(module.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(run_local_demo_abc.tempfile, "gettempdir", lambda: str(tmp_path))
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_abc_runtime_bundle.py"))
    )
    bundle, _manifest, manifest_sha = helpers["_valid_v6_bundle"](tmp_path / "bundle")
    authority_sha = hashlib.sha256((bundle / "authority.json").read_bytes()).hexdigest()
    monkeypatch.setattr(demo_bundle, "_current_demo_date", lambda: helpers["date"](2026, 8, 21))
    context = module._new_run_context(
        run_id=f"ui-human-{uuid4().hex[:12]}",
        bundle=bundle,
        manifest_sha=manifest_sha,
        authority_sha=authority_sha,
        candidate={"commit": "c" * 40, "tree": "d" * 40},
        profile="TECHNICAL_REHEARSAL",
        ui_session=True,
    )
    schema_id = json.loads(UI_PARITY_CONTRACT.read_text(encoding="utf-8"))["schema_id"]
    assert context.env["FPMS_DEMO_CONTRACT_VERSION"] == schema_id
    assert context.env["FPMS_DEMO_UI_SESSION"] == "1"
    for key, value in context.env.items():
        if key.startswith("FPMS_") or key in {"JWT_SECRET", "NO_PROXY", "no_proxy"}:
            monkeypatch.setenv(key, value)
    run = run_local_demo_abc.bootstrap_demo_run()
    assert run.run_root == context.run_root
    assert run.database_path.read_bytes().startswith(b"SQLite format 3")
    return module, context


def _exercise_ui_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    finalization: str,
):
    module, context = _real_ui_context(tmp_path, monkeypatch)
    artifact = (tmp_path / f"artifact-{finalization.lower()}").resolve()
    browser_process = _BrowserProcess()
    monkeypatch.setattr(module, "_start_headed_browser", lambda *_args: browser_process)
    monkeypatch.setattr("builtins.input", lambda _prompt: finalization)
    args = module.parse_args(
        ["--ui-session", "--actor", "HUMAN", "--artifact", str(artifact)]
    )
    status = module._run_ui_browser_session(args, context, artifact)
    module._complete_ui_session(context, artifact, status)

    session = json.loads((artifact / "session.json").read_text(encoding="utf-8"))
    binding = json.loads(
        (artifact / "observer" / "finalize-binding.json").read_text(encoding="utf-8")
    )
    output = capsys.readouterr().out
    assert "playwright" in binding["browser_command"][1]
    assert binding["browser_command"][2] == "open"
    assert "--headless" not in binding["browser_command"]
    assert binding["observer_artifact_root"] == str((artifact / "observer").resolve())
    browser_query = urllib.parse.parse_qs(
        urllib.parse.urlsplit(binding["browser_command"][-1]).query
    )
    assert browser_query["fpmsObserverBinding"] == [binding["observer_binding_url"]]
    assert binding["run_id"] == session["run_id"]
    serialized = output + json.dumps(binding) + json.dumps(session)
    assert context.admin_password not in serialized
    assert context.reviewer_password not in serialized
    assert '"password": "<redacted>"' in output
    return module, artifact, context.run_root


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
    _module.abc.remove_run_root(run_root, status["run_id"])


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


def test_real_bootstrap_browser_failure_preserves_exact_run_and_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module, context = _real_ui_context(tmp_path, monkeypatch)
    artifact = (tmp_path / "artifact-failed").resolve()
    args = module.parse_args(
        ["--ui-session", "--actor", "CODEX", "--artifact", str(artifact)]
    )
    monkeypatch.setattr(
        module,
        "_start_headed_browser",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("injected browser failure")),
    )

    with pytest.raises(RuntimeError, match="injected browser failure"):
        module._run_ui_browser_session(args, context, artifact)

    assert context.database_path.read_bytes().startswith(b"SQLite format 3")
    assert context.run_root.is_dir()
    assert artifact.is_dir()
    status = json.loads(
        (artifact / "observer" / "session-status.json").read_text(encoding="utf-8")
    )
    assert status == {
        "status": "FAILED",
        "run_id": context.run_id,
        "run_root_removed": False,
    }
    module.abc.remove_run_root(context.run_root, context.run_id)


def test_observer_host_binding_writes_only_observer_files_and_rejects_escape(
    tmp_path: Path,
):
    module = _runner_module()
    observer_root = (tmp_path / "artifact" / "observer").resolve()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    with module._observer_binding(observer_root) as binding:
        request = urllib.request.Request(
            binding.url,
            data=json.dumps(
                {
                    "filename": "observer-checkpoints.json",
                    "content": {"status": "RECORDED"},
                }
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with opener.open(request, timeout=2) as response:
            assert response.status == 201

        assert json.loads(
            (observer_root / "observer-checkpoints.json").read_text(encoding="utf-8")
        ) == {"status": "RECORDED"}
        for filename in ("../session.json", "session.json", "observer/escape.json"):
            rejected = urllib.request.Request(
                binding.url,
                data=json.dumps({"filename": filename, "content": {}}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with pytest.raises(urllib.error.HTTPError) as error:
                opener.open(rejected, timeout=2)
            assert error.value.code == 400

    assert sorted(path.name for path in observer_root.iterdir()) == [
        "observer-checkpoints.json"
    ]
    assert not (tmp_path / "artifact" / "session.json").exists()


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
