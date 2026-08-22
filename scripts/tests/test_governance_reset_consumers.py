from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

from scripts import atomic_evidence_validate as atomic_consumer


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "scripts" / "evidence_validate.py"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "gvr3_evidence_validate", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load evidence validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


class GovernanceConsumerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.previous_cwd = Path.cwd()
        os.chdir(self.root)
        (self.root / "tasks/repo").mkdir(parents=True)
        (self.root / "artifacts").mkdir()
        (self.root / "docs/agents").mkdir(parents=True)

    def tearDown(self) -> None:
        os.chdir(self.previous_cwd)
        self.temporary.cleanup()

    def create_task(
        self,
        task_id: str,
        *,
        status: str = "PASS",
        directory: str = "tasks/repo",
    ) -> Path:
        task = self.root / directory / f"{task_id}.md"
        task.parent.mkdir(parents=True, exist_ok=True)
        relative = task.relative_to(self.root).as_posix()
        task.write_text(
            f"# {task_id}\n\nStatus: {status}\nRisk-Tier: HIGH\n"
            f'Closure-Tags: ["evidence"]\n'
            f"Task-Path: {relative}\n\n"
            "## Allowed Files\n\n"
            f"- `{relative}`\n"
            f"- `artifacts/{task_id}/**`\n",
            encoding="utf-8",
        )
        return task

    def create_legacy_bundle(self, task_id: str = "LEGACY-01") -> Path:
        task = self.create_task(task_id)
        artifact = self.root / "artifacts" / task_id
        (artifact / "git").mkdir(parents=True)
        (artifact / "outputs").mkdir()
        (artifact / "review").mkdir()
        (artifact / "task.json").write_bytes(
            canonical(
                {
                    "task_id": task_id,
                    "task_file": task.relative_to(self.root).as_posix(),
                    "repo_root": str(self.root),
                    "allowlist": [
                        task.relative_to(self.root).as_posix(),
                        f"artifacts/{task_id}/**",
                    ],
                    "baseline_dirty": False,
                }
            )
        )
        (artifact / "summary.md").write_text(
            f"# Summary\nStatus: PASS\nTask-ID: {task_id}\n", encoding="utf-8"
        )
        (artifact / "git/diff.patch").write_text(
            "diff --git a/a b/a\n", encoding="utf-8"
        )
        (artifact / "review/independent_review.md").write_text(
            "Reviewer-ID: legacy-reviewer\nVerdict: APPROVED\nP0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        rows: list[dict[str, object]] = []
        for index, step in enumerate(
            (
                "lint",
                "test",
                "scope",
                "independent_review",
                "task_gate",
                "atomic_evidence",
            ),
            start=1,
        ):
            log = artifact / "outputs" / f"{step}.log"
            log.write_text("PASS\n", encoding="utf-8")
            rows.append(
                {
                    "ts": f"20260717T00000{index}000000",
                    "step": step,
                    "rc": 0,
                    "log": log.relative_to(self.root).as_posix(),
                }
            )
        (artifact / "results.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        (artifact / "commands.jsonl").write_text("{}\n", encoding="utf-8")
        return artifact

    def install_ledger(self, *task_ids: str) -> dict[str, object]:
        ledger = validator.build_legacy_ledger(self.root, list(task_ids))
        (self.root / "docs/agents/legacy-pass-ledger.json").write_bytes(
            validator.canonical_json(ledger)
        )
        return ledger

    def install_consumer_entrypoints(self) -> None:
        scripts = self.root / "scripts"
        scripts.mkdir(exist_ok=True)
        for name in (
            "evidence_validate.py",
            "task_validate.sh",
            "atomic_evidence_validate.py",
        ):
            target = scripts / name
            target.write_bytes((ROOT / "scripts" / name).read_bytes())
            target.chmod((ROOT / "scripts" / name).stat().st_mode)

    def test_legacy_ledger_freezes_exact_task_and_complete_artifact_tree(self) -> None:
        artifact = self.create_legacy_bundle()
        self.install_ledger("LEGACY-01")

        validator.validate("LEGACY-01", [], str(self.root), acceptance_mode="release")

        mutations = (
            lambda: (artifact / "outputs/test.log").write_text(
                "changed\n", encoding="utf-8"
            ),
            lambda: (artifact / "unexpected.txt").write_text("new\n", encoding="utf-8"),
            lambda: (artifact / "review/independent_review.md").unlink(),
            lambda: (self.root / "tasks/repo/LEGACY-01.md").write_text(
                "changed\n", encoding="utf-8"
            ),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                if index:
                    self.tearDown()
                    self.setUp()
                    artifact = self.create_legacy_bundle()
                    self.install_ledger("LEGACY-01")
                mutate()
                with self.assertRaises(validator.EvidenceValidationError):
                    validator.validate(
                        "LEGACY-01", [], str(self.root), acceptance_mode="release"
                    )

    def test_ledger_builder_rejects_symlink_and_nonregular_artifact_entries(
        self,
    ) -> None:
        artifact = self.create_legacy_bundle()
        target = artifact / "outputs/test.log"
        link = artifact / "linked.log"
        link.symlink_to(target)
        with self.assertRaises(validator.EvidenceValidationError):
            validator.build_legacy_ledger(self.root, ["LEGACY-01"])
        link.unlink()

        fifo = artifact / "unsafe.fifo"
        os.mkfifo(fifo)
        try:
            with self.assertRaises(validator.EvidenceValidationError):
                validator.build_legacy_ledger(self.root, ["LEGACY-01"])
        finally:
            fifo.unlink()

    def test_legacy_discovery_is_complete_and_excludes_nonpass_or_v2_tasks(
        self,
    ) -> None:
        self.create_legacy_bundle("LEGACY-01")
        legacy_without_metadata = self.create_legacy_bundle("LEGACY-02")
        (legacy_without_metadata / "task.json").unlink()
        self.create_task("NO-ARTIFACT", status="PASS")
        self.create_task("NOT-PASS", status="READY")
        v2 = self.create_legacy_bundle("V2-EXCLUDED")
        (v2 / "state.json").write_bytes(canonical({"schema_version": 2}))

        self.assertEqual(
            validator.discover_legacy_pass_task_ids(self.root),
            ["LEGACY-01", "LEGACY-02"],
        )

    def write_event(
        self,
        artifact: Path,
        ordinal: int,
        step: str,
        *,
        rc: int = 0,
        argv: list[str] | None = None,
        classification: str = "NON_SQLITE",
        replay_safe: bool = False,
        with_result: bool = True,
        with_log: bool = True,
        log_binding: bool = False,
    ) -> tuple[Path | None, Path | None]:
        events = artifact / "events"
        outputs = artifact / "outputs"
        events.mkdir(exist_ok=True)
        outputs.mkdir(exist_ok=True)
        command_argv = argv or [step]
        request = {
            "task_id": artifact.name,
            "step": step,
            "argv": command_argv,
            "cwd": str(self.root),
            "classification": classification,
            "replay_safe": replay_safe,
        }
        command = events / f"{ordinal:08d}.command.json"
        result = events / f"{ordinal:08d}.result.json"
        command.write_bytes(
            canonical(
                {
                    "schema_version": 2,
                    "task_id": artifact.name,
                    "ordinal": ordinal,
                    "step": step,
                    "argv": command_argv,
                    "cwd": str(self.root),
                    "classification": classification,
                    "replay_safe": replay_safe,
                    "request_digest": hashlib.sha256(
                        json.dumps(
                            request,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        ).encode("utf-8")
                    ).hexdigest(),
                }
            )
        )
        if not with_result:
            return None, None
        payload: dict[str, object] = {
            "schema_version": 2,
            "task_id": artifact.name,
            "ordinal": ordinal,
            "step": step,
            "rc": rc,
            "executed": True,
        }
        log: Path | None = None
        if with_log:
            log = outputs / f"{ordinal:08d}_{step}.log"
            log.write_text("PASS\n", encoding="utf-8")
            payload["log"] = log.relative_to(self.root).as_posix()
            if log_binding:
                payload["log_sha256"] = sha256(log)
        result.write_bytes(canonical(payload))
        return result, log

    def rewrite_event_command(
        self,
        artifact: Path,
        ordinal: int,
        *,
        step: str | None = None,
        argv: list[str] | None = None,
    ) -> None:
        command_path = artifact / f"events/{ordinal:08d}.command.json"
        command = json.loads(command_path.read_text(encoding="utf-8"))
        if step is not None:
            command["step"] = step
        if argv is not None:
            command["argv"] = argv
        request = {
            "task_id": command["task_id"],
            "step": command["step"],
            "argv": command["argv"],
            "cwd": command["cwd"],
            "classification": command["classification"],
            "replay_safe": command["replay_safe"],
        }
        command["request_digest"] = hashlib.sha256(
            json.dumps(
                request,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        command_path.write_bytes(canonical(command))
        result_path = artifact / f"events/{ordinal:08d}.result.json"
        if result_path.exists() and step is not None:
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["step"] = step
            result_path.write_bytes(canonical(result))

    def create_v2_bundle(
        self,
        *,
        terminal: bool,
        inflight: str = "atomic",
        task_directory: str = "tasks/repo",
    ) -> Path:
        task_id = "V2-01"
        task = self.create_task(
            task_id,
            status="REVIEW / CLOSE PENDING",
            directory=task_directory,
        )
        artifact = self.root / "artifacts" / task_id
        (artifact / "git").mkdir(parents=True)
        (artifact / "review").mkdir()
        (artifact / "task.json").write_bytes(
            canonical(
                {
                    "task_id": task_id,
                    "task_file": task.relative_to(self.root).as_posix(),
                    "repo_root": str(self.root),
                    "allowlist": [task.relative_to(self.root).as_posix()],
                    "baseline_dirty": False,
                }
            )
        )
        summary = artifact / "summary.md"
        summary.write_text("# Summary\nStatus: REVIEW\n", encoding="utf-8")
        patch = artifact / "git/diff.patch"
        patch.write_text("diff --git a/a b/a\n", encoding="utf-8")

        required: dict[str, dict[str, str]] = {}
        ordinal = 1
        for step in ("lint", "test", "scope"):
            result, log = self.write_event(artifact, ordinal, step)
            assert result is not None and log is not None
            required[step] = {
                "result_sha256": sha256(result),
                "log_sha256": sha256(log),
            }
            ordinal += 1

        governance = "a" * 64
        candidate: dict[str, object] = {
            "task_sha256": sha256(task),
            "summary_sha256": sha256(summary),
            "scoped_patch_sha256": sha256(patch),
            "patch_sha256": sha256(patch),
            "governance_digest": governance,
            "baseline": {},
            "required_results": required,
            "source_hashes": {},
        }
        candidate["fingerprint"] = hashlib.sha256(
            json.dumps(
                candidate,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        report = artifact / "review/independent_review.md"
        review_body = (
            "Reviewer-ID: reviewer-01\nVerdict: APPROVED\nP0: 0\nP1: 0\nP2: 0\n"
        )
        report.write_text(
            f"Reviewed-Candidate-Fingerprint: {candidate['fingerprint']}\n"
            f"Reviewed-Patch-SHA256: {candidate['patch_sha256']}\n"
            f"Reviewed-Governance-Digest: {governance}\n" + review_body,
            encoding="utf-8",
        )
        state: dict[str, object] = {
            "schema_version": 2,
            "state": "CLOSING",
            "task_id": task_id,
            "task_file": task.relative_to(self.root).as_posix(),
            "allowlist": [task.relative_to(self.root).as_posix()],
            "baseline": {},
            "governance_digest": governance,
            "controller": "lead",
            "implementer": "implementer",
            "review_generation": 1,
            "candidate": candidate,
            "review_leases": {
                "independent": {
                    "axis": "independent",
                    "reviewer": "reviewer-01",
                    "candidate_fingerprint": candidate["fingerprint"],
                    "review_generation": 1,
                    "issued_ns": 1,
                }
            },
            "reviews": {
                "independent": {
                    "axis": "independent",
                    "reviewer": "reviewer-01",
                    "report": str(report.resolve()),
                    "submission_sha256": hashlib.sha256(
                        review_body.encode("utf-8")
                    ).hexdigest(),
                    "report_sha256": sha256(report),
                    "candidate_fingerprint": candidate["fingerprint"],
                    "review_generation": 1,
                }
            },
        }
        close_steps = ["taskctl_scope_refresh", "independent_review"]
        if terminal or inflight == "atomic":
            close_steps.append("task_gate")
        for step in close_steps:
            self.write_event(
                artifact,
                ordinal,
                step,
                argv=validator.expected_gate_argv(task_id, step, candidate, 1),
                classification="INTERNAL",
                replay_safe=True,
                log_binding=True,
            )
            ordinal += 1
        if terminal:
            self.write_event(
                artifact,
                ordinal,
                "atomic_evidence",
                argv=validator.expected_gate_argv(
                    task_id, "atomic_evidence", candidate, 1
                ),
                classification="INTERNAL",
                replay_safe=True,
                log_binding=True,
            )
            ordinal += 1
            close_result, _close_log = self.write_event(
                artifact,
                ordinal,
                "taskctl_close",
                argv=validator.expected_gate_argv(
                    task_id, "taskctl_close", candidate, 1
                ),
                classification="INTERNAL",
                replay_safe=True,
                with_log=False,
            )
            assert close_result is not None
            state["state"] = "PASS"
            state["terminal_ordinal"] = ordinal
            receipts: dict[str, dict[str, object]] = {}
            for event_ordinal in range(4, ordinal + 1):
                command = json.loads(
                    (artifact / f"events/{event_ordinal:08d}.command.json").read_text()
                )
                result_path = artifact / f"events/{event_ordinal:08d}.result.json"
                result_value = json.loads(result_path.read_text())
                receipt: dict[str, object] = {
                    "ordinal": event_ordinal,
                    "result_sha256": sha256(result_path),
                }
                if command["step"] != "taskctl_close":
                    receipt.update(
                        {
                            "log": result_value["log"],
                            "log_sha256": result_value["log_sha256"],
                        }
                    )
                receipts[command["step"]] = receipt
            state["terminal_receipts"] = receipts
        else:
            current = "task_gate" if inflight == "task" else "atomic_evidence"
            self.write_event(
                artifact,
                ordinal,
                current,
                argv=validator.expected_gate_argv(task_id, current, candidate, 1),
                classification="INTERNAL",
                replay_safe=True,
                with_result=False,
            )
        (artifact / "state.json").write_bytes(canonical(state))
        return artifact

    def test_v2_closing_is_gate_only_and_terminal_pass_is_release_only(self) -> None:
        self.create_v2_bundle(terminal=False, inflight="atomic")

        validator.validate(
            "V2-01",
            ["lint", "test", "scope", "independent_review", "task_gate"],
            str(self.root),
            acceptance_mode="atomic",
        )
        with self.assertRaises(validator.EvidenceValidationError):
            validator.validate("V2-01", [], str(self.root), acceptance_mode="release")

        self.tearDown()
        self.setUp()
        self.create_v2_bundle(terminal=False, inflight="task")
        validator.validate(
            "V2-01",
            ["lint", "test", "scope"],
            str(self.root),
            acceptance_mode="task",
        )

        self.tearDown()
        self.setUp()
        self.create_v2_bundle(terminal=True)
        validator.validate("V2-01", [], str(self.root), acceptance_mode="release")

    def test_v2_task_path_is_bound_to_repository_root_at_any_task_depth(self) -> None:
        self.create_v2_bundle(
            terminal=False,
            inflight="task",
            task_directory="tasks/postdemo/v8",
        )

        validator.validate(
            "V2-01",
            ["lint", "test", "scope"],
            str(self.root),
            acceptance_mode="task",
        )

    def test_v2_closing_rejects_mutated_predecessor_command_bindings(self) -> None:
        cases = (
            ("task", 4, ["tampered-scope"]),
            ("task", 5, ["tampered-review"]),
            ("atomic", 6, ["tampered-task-gate"]),
        )
        for index, (mode, ordinal, argv) in enumerate(cases):
            with self.subTest(mode=mode, ordinal=ordinal):
                if index:
                    self.tearDown()
                    self.setUp()
                artifact = self.create_v2_bundle(terminal=False, inflight=mode)
                self.rewrite_event_command(artifact, ordinal, argv=argv)
                required = ["lint", "test", "scope"]
                if mode == "atomic":
                    required.extend(("independent_review", "task_gate"))
                with self.assertRaises(validator.EvidenceValidationError):
                    validator.validate(
                        "V2-01",
                        required,
                        str(self.root),
                        acceptance_mode=mode,
                    )

    def test_v2_closing_rejects_reordered_predecessor_commands(self) -> None:
        for index, mode in enumerate(("task", "atomic")):
            with self.subTest(mode=mode):
                if index:
                    self.tearDown()
                    self.setUp()
                artifact = self.create_v2_bundle(terminal=False, inflight=mode)
                state = json.loads(
                    (artifact / "state.json").read_text(encoding="utf-8")
                )
                candidate = state["candidate"]
                self.rewrite_event_command(
                    artifact,
                    4,
                    step="independent_review",
                    argv=validator.expected_gate_argv(
                        "V2-01", "independent_review", candidate, 1
                    ),
                )
                self.rewrite_event_command(
                    artifact,
                    5,
                    step="taskctl_scope_refresh",
                    argv=validator.expected_gate_argv(
                        "V2-01", "taskctl_scope_refresh", candidate, 1
                    ),
                )
                required = ["lint", "test", "scope"]
                if mode == "atomic":
                    required.extend(("independent_review", "task_gate"))
                with self.assertRaises(validator.EvidenceValidationError):
                    validator.validate(
                        "V2-01",
                        required,
                        str(self.root),
                        acceptance_mode=mode,
                    )

    def test_gvr3_required_commands_match_taskctl_and_reject_drift(self) -> None:
        taskctl = runpy.run_path(
            str(ROOT / "scripts/taskctl"), run_name="gvr3_taskctl_contract"
        )
        self.assertEqual(
            validator.GVR3_REQUIRED_COMMANDS,
            taskctl["GVR3_REQUIRED_COMMANDS"],
        )
        for step, (argv, classification) in validator.GVR3_REQUIRED_COMMANDS.items():
            command = {
                "step": step,
                "argv": list(argv),
                "cwd": str(self.root),
                "classification": classification,
                "replay_safe": False,
            }
            validator.validate_gvr3_required_command(command, step, self.root)
            for key, value in (
                ("argv", [*argv, "tampered"]),
                ("cwd", str(self.root / "elsewhere")),
                ("classification", "INTERNAL"),
                ("replay_safe", True),
            ):
                with self.subTest(step=step, key=key):
                    changed = dict(command)
                    changed[key] = value
                    with self.assertRaises(validator.EvidenceValidationError):
                        validator.validate_gvr3_required_command(
                            changed, step, self.root
                        )

    def test_v2_and_legacy_are_mutually_exclusive_and_neither_fails_closed(
        self,
    ) -> None:
        artifact = self.create_legacy_bundle("MIXED-01")
        self.install_ledger("MIXED-01")
        (artifact / "state.json").write_bytes(canonical({"schema_version": 2}))
        with self.assertRaises(validator.EvidenceValidationError):
            validator.validate(
                "MIXED-01", [], str(self.root), acceptance_mode="release"
            )

        self.create_task("UNACCEPTED-01")
        (self.root / "artifacts/UNACCEPTED-01").mkdir()
        with self.assertRaises(validator.EvidenceValidationError):
            validator.validate(
                "UNACCEPTED-01", [], str(self.root), acceptance_mode="release"
            )

    def test_v2_rejects_review_triple_and_bound_log_drift(self) -> None:
        artifact = self.create_v2_bundle(terminal=False, inflight="task")
        report = artifact / "review/independent_review.md"
        accepted = report.read_bytes()
        state = json.loads((artifact / "state.json").read_text(encoding="utf-8"))
        candidate = state["candidate"]
        for old, new in (
            (str(candidate["governance_digest"]).encode(), b"b" * 64),
            (str(candidate["fingerprint"]).encode(), b"c" * 64),
            (str(candidate["patch_sha256"]).encode(), b"d" * 64),
        ):
            with self.subTest(old=old[:8]):
                report.write_bytes(accepted.replace(old, new, 1))
                with self.assertRaises(validator.EvidenceValidationError):
                    validator.validate(
                        "V2-01",
                        ["lint", "test", "scope"],
                        str(self.root),
                        acceptance_mode="task",
                    )
                report.write_bytes(accepted)

        (artifact / "outputs/00000002_test.log").write_text(
            "tampered\n", encoding="utf-8"
        )
        with self.assertRaises(validator.EvidenceValidationError):
            validator.validate(
                "V2-01",
                ["lint", "test", "scope"],
                str(self.root),
                acceptance_mode="task",
            )

    def test_task_and_atomic_entrypoints_share_the_same_v2_consumer(self) -> None:
        self.install_consumer_entrypoints()
        self.create_v2_bundle(terminal=False, inflight="task")
        task_gate = subprocess.run(
            ["./scripts/task_validate.sh", "V2-01"],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(task_gate.returncode, 0, task_gate.stdout)

        self.tearDown()
        self.setUp()
        self.install_consumer_entrypoints()
        self.create_v2_bundle(terminal=False, inflight="atomic")
        atomic_gate = subprocess.run(
            [
                sys.executable,
                "scripts/atomic_evidence_validate.py",
                "V2-01",
                "--required-step",
                "lint",
                "--required-step",
                "test",
                "--required-step",
                "scope",
                "--required-step",
                "independent_review",
                "--required-step",
                "task_gate",
            ],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(atomic_gate.returncode, 0, atomic_gate.stdout)
        self.assertIn(
            "--acceptance-mode",
            atomic_consumer.helper_command("V2-01", ["lint"]),
        )


if __name__ == "__main__":
    unittest.main()
