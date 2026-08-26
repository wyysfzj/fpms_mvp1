from __future__ import annotations

import base64
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
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

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
    assert len(expected_business_tables) == 77
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
    def __init__(self, returncode: int | None = None) -> None:
        self.returncode = returncode
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


EXPECTED_OBSERVER_FILES = frozenset(
    {"observer-ui-ledger.json"}
    | {f"observer-stage-{stage:02d}.png" for stage in range(1, 12)}
)
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8A"
    "AQUBAScY42YAAAAASUVORK5CYII="
)


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


def _session_tuple(module, context, *, actor: str) -> dict[str, str]:
    return {
        "contract_version": module.UI_SESSION_CONTRACT_VERSION,
        "run_id": context.run_id,
        "candidate_commit": context.candidate_commit,
        "candidate_tree": context.candidate_tree,
        "authority_sha256": context.authority_sha,
        "actor": actor,
    }


def _binding_url(activation_url: str, operation: str, capability: str | None = None) -> str:
    parsed = urllib.parse.urlsplit(activation_url)
    actual = urllib.parse.parse_qs(parsed.query)["capability"][0]
    selected = actual if capability is None else capability
    query = urllib.parse.urlencode({"capability": selected}) if selected else ""
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, f"/{operation}", query, "")
    )


def _host_post(
    activation_url: str,
    operation: str,
    payload: object,
    *,
    capability: str | None = None,
    raw_body: bytes | None = None,
    declared_length: int | None = None,
) -> tuple[int, dict[str, object]]:
    headers = {"Content-Type": "application/json"}
    if declared_length is not None:
        headers["Content-Length"] = str(declared_length)
    request = urllib.request.Request(
        _binding_url(activation_url, operation, capability),
        data=raw_body if raw_body is not None else json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=2) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def _ledger_payload(session_tuple: dict[str, str]) -> dict[str, object]:
    return {
        **session_tuple,
        "filename": "observer-ui-ledger.json",
        "encoding": "json",
        "content": {
            "schema_id": session_tuple["contract_version"],
            "session": session_tuple,
            "events": [],
        },
    }


def _screenshot_payload(
    session_tuple: dict[str, str], filename: str
) -> dict[str, object]:
    return {
        **session_tuple,
        "filename": filename,
        "encoding": "base64",
        "content": base64.b64encode(PNG_1X1).decode(),
    }


def _upload_complete_evidence(
    activation_url: str, session_tuple: dict[str, str]
) -> None:
    assert _host_post(
        activation_url, "observer-artifact", _ledger_payload(session_tuple)
    )[0] == 201
    for filename in sorted(EXPECTED_OBSERVER_FILES - {"observer-ui-ledger.json"}):
        assert _host_post(
            activation_url,
            "observer-artifact",
            _screenshot_payload(session_tuple, filename),
        )[0] == 201


def test_observer_binding_authenticates_exact_tuple_and_revalidates_after_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module, context = _real_ui_context(tmp_path, monkeypatch)
    observer_root = (tmp_path / "artifact" / "observer").resolve()
    session_tuple = _session_tuple(module, context, actor="HUMAN")

    with module._observer_binding(observer_root, session_tuple) as binding:
        activation = urllib.parse.urlsplit(binding.activation_url)
        activation_query = urllib.parse.parse_qs(activation.query)
        capability = activation_query["capability"][0]
        assert len(capability) >= 43
        assert activation_query["actor"] == ["HUMAN"]
        assert _host_post(
            binding.activation_url, "revalidate", session_tuple, capability=""
        )[0] == 401
        assert _host_post(
            binding.activation_url, "revalidate", session_tuple, capability="wrong"
        )[0] == 401
        assert not binding.failed.is_set()

        for key in session_tuple:
            drifted = {**session_tuple, key: f"wrong-{key}"}
            assert _host_post(binding.activation_url, "revalidate", drifted)[0] == 409
        missing_actor = {**session_tuple}
        del missing_actor["actor"]
        assert _host_post(binding.activation_url, "revalidate", missing_actor)[0] == 409

        assert _host_post(binding.activation_url, "revalidate", session_tuple)[0] == 200
        engine = create_engine(f"sqlite:///{context.database_path}")
        with Session(engine) as db:
            db.add(
                Client(
                    id=str(uuid4()),
                    client_code="UI-SESSION-POST-MUTATION",
                    name_cn="会话重校验",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                )
            )
            db.commit()
        engine.dispose()
        assert _host_post(binding.activation_url, "revalidate", session_tuple)[0] == 200
        assert _host_post(binding.activation_url, "unknown", session_tuple)[0] == 404

    assert context.run_root.is_dir()
    assert observer_root.is_dir()
    module.abc.remove_run_root(context.run_root, context.run_id)


def test_observer_binding_accepts_only_exact_named_evidence_and_rejects_invalid_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module, context = _real_ui_context(tmp_path, monkeypatch)
    observer_root = (tmp_path / "artifact" / "observer").resolve()
    session_tuple = _session_tuple(module, context, actor="CODEX")

    assert module.UI_SESSION_OBSERVER_FILES == EXPECTED_OBSERVER_FILES
    with module._observer_binding(observer_root, session_tuple) as binding:
        wrong_ledger_tuple = _ledger_payload(session_tuple)
        wrong_ledger_tuple["content"]["session"] = {
            **session_tuple,
            "run_id": "wrong-run",
        }
        assert _host_post(
            binding.activation_url, "observer-artifact", wrong_ledger_tuple
        )[0] == 400
        malformed_json = {
            **_ledger_payload(session_tuple),
            "encoding": "base64",
        }
        assert _host_post(
            binding.activation_url, "observer-artifact", malformed_json
        )[0] == 400
        assert _host_post(
            binding.activation_url,
            "observer-artifact",
            _ledger_payload(session_tuple),
        )[0] == 201
        assert _host_post(
            binding.activation_url,
            "observer-artifact",
            _ledger_payload(session_tuple),
        )[0] == 409
        assert _host_post(binding.activation_url, "finalize", session_tuple)[0] == 409

        for filename in (
            "../observer-ui-ledger.json",
            "observer-extra.json",
            "observer-stage-12.png",
        ):
            invalid = {**_ledger_payload(session_tuple), "filename": filename}
            assert _host_post(
                binding.activation_url, "observer-artifact", invalid
            )[0] == 400

        malformed_png = {
            **_screenshot_payload(session_tuple, "observer-stage-01.png"),
            "content": "not-base64",
        }
        assert _host_post(
            binding.activation_url, "observer-artifact", malformed_png
        )[0] == 400

        outside = tmp_path / "outside.png"
        outside.write_bytes(PNG_1X1)
        symlink = observer_root / "observer-stage-02.png"
        symlink.symlink_to(outside)
        assert _host_post(
            binding.activation_url,
            "observer-artifact",
            _screenshot_payload(session_tuple, symlink.name),
        )[0] == 409
        symlink.unlink()

        assert _host_post(
            binding.activation_url,
            "observer-artifact",
            {},
            raw_body=b"{}",
            declared_length=2_000_001,
        )[0] == 400

    assert sorted(path.name for path in observer_root.iterdir()) == [
        "observer-ui-ledger.json"
    ]
    module.abc.remove_run_root(context.run_root, context.run_id)


def test_browser_finalization_requires_complete_evidence_and_cleans_exact_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    module, context = _real_ui_context(tmp_path, monkeypatch)
    artifact = (tmp_path / "artifact-finalized").resolve()
    args = module.parse_args(
        ["--ui-session", "--actor", "HUMAN", "--artifact", str(artifact)]
    )
    session_tuple = _session_tuple(module, context, actor="HUMAN")
    browser_process = _BrowserProcess()
    captured_capability = ""

    def launch_browser(command, _env):
        nonlocal captured_capability
        assert command[:3] == ["node", "./node_modules/.bin/playwright", "open"]
        assert "--browser=chromium" in command
        assert "--headless" not in command
        page_query = urllib.parse.parse_qs(urllib.parse.urlsplit(command[-1]).query)
        activation_url = page_query["fpmsObserverBinding"][0]
        captured_capability = urllib.parse.parse_qs(
            urllib.parse.urlsplit(activation_url).query
        )["capability"][0]
        assert command[-1].count(captured_capability) == 1
        assert _host_post(activation_url, "revalidate", session_tuple)[0] == 200
        _upload_complete_evidence(activation_url, session_tuple)
        assert _host_post(activation_url, "finalize", session_tuple)[0] == 200
        return browser_process

    monkeypatch.setattr(module, "_start_headed_browser", launch_browser)
    monkeypatch.setattr(
        "builtins.input", lambda _prompt: pytest.fail("terminal input is forbidden")
    )

    status = module._run_ui_browser_session(args, context, artifact)
    assert status == "FINALIZED"
    module._complete_ui_session(context, artifact, status)

    assert not context.run_root.exists()
    assert captured_capability
    serialized = capsys.readouterr().out + "".join(
        path.read_text(encoding="utf-8")
        for path in artifact.rglob("*.json")
    )
    assert captured_capability not in serialized
    assert context.admin_password not in serialized
    assert context.reviewer_password not in serialized
    final_status = json.loads(
        (artifact / "observer" / "session-status.json").read_text(encoding="utf-8")
    )
    assert final_status == {
        "status": "FINALIZED",
        "run_id": context.run_id,
        "run_root_removed": True,
    }


@pytest.mark.parametrize("stop_reason", ["browser-exit", "timeout"])
def test_browser_exit_or_timeout_stops_without_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stop_reason: str,
):
    module, context = _real_ui_context(tmp_path, monkeypatch)
    artifact = (tmp_path / f"artifact-{stop_reason}").resolve()
    args = module.parse_args(
        ["--ui-session", "--actor", "CODEX", "--artifact", str(artifact)]
    )
    process = _BrowserProcess(returncode=0 if stop_reason == "browser-exit" else None)
    monkeypatch.setattr(module, "_start_headed_browser", lambda *_args: process)
    monkeypatch.setattr(module, "UI_SESSION_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(
        "builtins.input", lambda _prompt: pytest.fail("terminal input is forbidden")
    )

    status = module._run_ui_browser_session(args, context, artifact)
    assert status == "STOPPED"
    module._complete_ui_session(context, artifact, status)

    assert context.run_root.is_dir()
    assert artifact.is_dir()
    final_status = json.loads(
        (artifact / "observer" / "session-status.json").read_text(encoding="utf-8")
    )
    assert final_status["run_root_removed"] is False
    module.abc.remove_run_root(context.run_root, context.run_id)


def test_malformed_host_evidence_records_failure_and_preserves_exact_run_and_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module, context = _real_ui_context(tmp_path, monkeypatch)
    artifact = (tmp_path / "artifact-host-failed").resolve()
    args = module.parse_args(
        ["--ui-session", "--actor", "CODEX", "--artifact", str(artifact)]
    )
    session_tuple = _session_tuple(module, context, actor="CODEX")

    def launch_browser(command, _env):
        page_query = urllib.parse.parse_qs(urllib.parse.urlsplit(command[-1]).query)
        activation_url = page_query["fpmsObserverBinding"][0]
        malformed = _screenshot_payload(session_tuple, "observer-stage-01.png")
        malformed["content"] = "not-base64"
        assert _host_post(
            activation_url,
            "observer-artifact",
            malformed,
        )[0] == 400
        return _BrowserProcess()

    monkeypatch.setattr(module, "_start_headed_browser", launch_browser)

    with pytest.raises(RuntimeError, match="observer host rejected"):
        module._run_ui_browser_session(args, context, artifact)

    assert context.database_path.read_bytes().startswith(b"SQLite format 3")
    assert context.run_root.is_dir()
    assert artifact.is_dir()
    final_status = json.loads(
        (artifact / "observer" / "session-status.json").read_text(encoding="utf-8")
    )
    assert final_status == {
        "status": "FAILED",
        "run_id": context.run_id,
        "run_root_removed": False,
    }
    module.abc.remove_run_root(context.run_root, context.run_id)


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
