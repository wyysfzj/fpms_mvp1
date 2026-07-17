from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.tests import test_taskctl as taskctl_tests
from scripts import evidence_validate as evidence_consumer


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01"


class GovernanceActivationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.source = Path(self.temporary.name).resolve() / "source"
        (self.source / "scripts").mkdir(parents=True)
        (self.source / "docs/agents").mkdir(parents=True)
        (self.source / "artifacts" / taskctl_tests.taskctl.GVR1_ID).mkdir(parents=True)
        shutil.copy2(ROOT / "AGENTS.md", self.source / "AGENTS.md")
        shutil.copy2(
            ROOT / "scripts/evidence_scope.py",
            self.source / "scripts/evidence_scope.py",
        )
        for module in (ROOT / "docs/agents").glob("*.md"):
            shutil.copy2(module, self.source / "docs/agents" / module.name)
        shutil.copytree(
            ROOT / "artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate",
            self.source
            / "artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate",
        )
        frozen = ROOT / f"artifacts/{TASK_ID}/bootstrap/frozen-v1"
        for relative in taskctl_tests.taskctl.FROZEN_V1_CONSUMERS:
            destination = self.source / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(frozen / relative, destination)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_existing_fault_contract(self, method_name: str) -> None:
        previous_root = taskctl_tests.ROOT
        case = taskctl_tests.ControllerStateMachineTests(method_name)
        taskctl_tests.ROOT = self.source
        started = False
        try:
            case.setUp()
            started = True
            getattr(case, method_name)()
        finally:
            if started:
                case.tearDown()
            taskctl_tests.ROOT = previous_root

    def test_root_first_manifest_second_recovers_every_frozen_crash_point(self) -> None:
        self.run_existing_fault_contract(
            "test_activation_crash_points_recover_without_missing_or_duplicate"
        )

    def test_close_runs_review_task_atomic_and_writes_pass_last(self) -> None:
        self.run_existing_fault_contract(
            "test_close_orders_review_task_atomic_and_pass_last_with_retry"
        )

    def test_installed_legacy_ledger_is_complete_and_exact(self) -> None:
        ledger = json.loads(
            (ROOT / "docs/agents/legacy-pass-ledger.json").read_text(encoding="utf-8")
        )
        entries = evidence_consumer.validate_ledger_schema(ledger)
        discovered = evidence_consumer.discover_legacy_pass_task_ids(ROOT)
        self.assertEqual(
            [entry["task_id"] for entry in entries],
            discovered,
        )
        for entry in entries:
            evidence_consumer.validate_legacy(ROOT, str(entry["task_id"]), entry)

    def test_release_gate_validates_exact_activation_before_selected_tasks(
        self,
    ) -> None:
        repo = Path(self.temporary.name).resolve() / "release-repo"
        (repo / "scripts").mkdir(parents=True)
        (repo / "docs/agents").mkdir(parents=True)
        gate = repo / "scripts/release_gate.sh"
        shutil.copy2(ROOT / "scripts/release_gate.sh", gate)
        capture = repo / "calls.jsonl"
        (repo / "scripts/evidence_validate.py").write_text(
            "import json,os,sys\n"
            "with open(os.environ['CAPTURE'], 'a', encoding='utf-8') as stream:\n"
            "    stream.write(json.dumps(sys.argv[1:]) + '\\n')\n",
            encoding="utf-8",
        )
        active = repo / "docs/agents/manifest.json"
        active.write_text(json.dumps({"activation_task": TASK_ID}), encoding="utf-8")
        manifest = repo / "product-manifest.md"
        manifest.write_text(
            "- Task file: `tasks/additional_gaps/PRODUCT-01.md`\n",
            encoding="utf-8",
        )
        environment = {
            **os.environ,
            "CAPTURE": str(capture),
            "PYTHONDONTWRITEBYTECODE": "1",
        }

        result = subprocess.run(
            ["./scripts/release_gate.sh", "--manifest", str(manifest)],
            cwd=repo,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        calls = [json.loads(line) for line in capture.read_text().splitlines()]
        self.assertEqual(
            calls,
            [
                [TASK_ID, "--acceptance-mode", "release"],
                ["PRODUCT-01", "--acceptance-mode", "release"],
            ],
        )

        capture.unlink()
        active.write_text(
            json.dumps({"activation_task": "WRONG-ACTIVATION"}), encoding="utf-8"
        )
        rejected = subprocess.run(
            ["./scripts/release_gate.sh", "--manifest", str(manifest)],
            cwd=repo,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertNotEqual(rejected.returncode, 0, rejected.stdout)
        self.assertFalse(capture.exists())

    def build_runner_repo(self) -> Path:
        repo = Path(self.temporary.name).resolve() / "runner-repo"
        (repo / "scripts").mkdir(parents=True)
        (repo / "tasks/repo").mkdir(parents=True)
        (repo / "docs/agents").mkdir(parents=True)
        artifact = repo / "artifacts" / TASK_ID
        frozen_target = artifact / "bootstrap/frozen-v1"
        shutil.copytree(
            ROOT / f"artifacts/{TASK_ID}/bootstrap/frozen-v1", frozen_target
        )
        plan = artifact / "bootstrap/frozen-v1-plan.json"
        shutil.copy2(ROOT / f"artifacts/{TASK_ID}/bootstrap/frozen-v1-plan.json", plan)
        (artifact / "candidate").mkdir()
        (artifact / "review").mkdir()
        shutil.copy2(
            ROOT / "scripts/frozen_v1_acceptance.py",
            repo / "scripts/frozen_v1_acceptance.py",
        )
        for relative in taskctl_tests.taskctl.FROZEN_V1_CONSUMERS:
            destination = repo / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        shutil.copy2(ROOT / "AGENTS.md", repo / "AGENTS.md")
        task = repo / f"tasks/repo/{TASK_ID}.md"
        task.write_text(
            f"# {TASK_ID}\n\nStatus: REVIEW\nRisk-Tier: HIGH\n"
            f'Closure-Tags: ["governance"]\nTask-Path: tasks/repo/{TASK_ID}.md\n\n'
            "## Allowed Files\n\n"
            f"- `tasks/repo/{TASK_ID}.md`\n- `artifacts/{TASK_ID}/**`\n",
            encoding="utf-8",
        )
        (artifact / "task.json").write_text(
            json.dumps(
                {
                    "task_id": TASK_ID,
                    "task_file": f"tasks/repo/{TASK_ID}.md",
                    "repo_root": str(repo),
                    "allowlist": [
                        f"tasks/repo/{TASK_ID}.md",
                        f"artifacts/{TASK_ID}/**",
                    ],
                    "baseline_dirty": True,
                }
            ),
            encoding="utf-8",
        )
        (artifact / "summary.md").write_text("Status: REVIEW\n", encoding="utf-8")
        inventory = frozen_target / "inventory.json"
        (artifact / "state.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "state": "IMPLEMENTING",
                    "task_id": TASK_ID,
                    "baseline": {
                        "frozen_v1_inventory_sha256": hashlib.sha256(
                            inventory.read_bytes()
                        ).hexdigest(),
                        "frozen_v1_plan_sha256": hashlib.sha256(
                            plan.read_bytes()
                        ).hexdigest(),
                    },
                }
            ),
            encoding="utf-8",
        )
        return repo

    def run_frozen_runner(self, repo: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "scripts/frozen_v1_acceptance.py",
                "--task-id",
                TASK_ID,
                "--frozen-root",
                f"artifacts/{TASK_ID}/bootstrap/frozen-v1",
                "--candidate-root",
                f"artifacts/{TASK_ID}/candidate",
            ],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def test_frozen_v1_runner_is_isolated_and_hash_bound(self) -> None:
        repo = self.build_runner_repo()
        protected = {
            path.relative_to(repo).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in (
                repo / "AGENTS.md",
                repo / f"tasks/repo/{TASK_ID}.md",
                repo / f"artifacts/{TASK_ID}/summary.md",
                *(
                    repo / relative
                    for relative in taskctl_tests.taskctl.FROZEN_V1_CONSUMERS
                ),
            )
        }

        result = self.run_frozen_runner(repo)

        self.assertEqual(result.returncode, 0, result.stdout)
        report = repo / f"artifacts/{TASK_ID}/candidate/frozen-v1-report.json"
        self.assertTrue(report.is_file())
        self.assertEqual(
            json.loads(report.read_text(encoding="utf-8"))["decision"], "PASS"
        )
        self.assertEqual(
            protected,
            {
                path: hashlib.sha256((repo / path).read_bytes()).hexdigest()
                for path in protected
            },
        )

        frozen_consumer = (
            repo
            / f"artifacts/{TASK_ID}/bootstrap/frozen-v1/scripts/evidence_validate.py"
        )
        frozen_consumer.write_bytes(frozen_consumer.read_bytes() + b"\n")
        rejected = self.run_frozen_runner(repo)
        self.assertNotEqual(rejected.returncode, 0, rejected.stdout)


if __name__ == "__main__":
    unittest.main()
