from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
SHELL_WRAPPER = ROOT / "scripts" / "evidence_run.sh"
PYTHON_RUNNER = ROOT / "scripts" / "evidence_task.py"
TASK_ID = "TEST-EVIDENCE-TASK"


def write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EvidenceTaskCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        scripts = self.repo / "scripts"
        scripts.mkdir()
        shutil.copy2(SHELL_WRAPPER, scripts / "evidence_run.sh")
        if PYTHON_RUNNER.exists():
            shutil.copy2(PYTHON_RUNNER, scripts / "evidence_task.py")
        artifact = self.repo / "artifacts" / TASK_ID
        (artifact / "outputs").mkdir(parents=True)
        (artifact / "commands.jsonl").write_text("", encoding="utf-8")
        (artifact / "results.jsonl").write_text("", encoding="utf-8")
        self.lock_dir = Path("/tmp/fpms_v8_sqlite.lockdir")
        self.owns_contention_fixture = False
        self.assertFalse(
            self.lock_dir.exists(), "repository SQLite lock is already held"
        )

    def tearDown(self) -> None:
        if self.owns_contention_fixture and self.lock_dir.exists():
            foreign = self.lock_dir / "foreign-owner"
            foreign.unlink(missing_ok=True)
            self.lock_dir.rmdir()
        self.temp_dir.cleanup()

    @property
    def artifact(self) -> Path:
        return self.repo / "artifacts" / TASK_ID

    def run_cli(
        self,
        *args: str,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            [*args],
            cwd=cwd or self.repo,
            env=merged_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def test_legacy_wrapper_keeps_caller_cwd_and_writes_valid_json_argv(self) -> None:
        caller = self.repo / "nested" / "caller"
        caller.mkdir(parents=True)
        observed = self.repo / "observed.json"
        tricky = ['quote"value', r"back\slash", "中文 空格", ""]
        command = [
            sys.executable,
            "-c",
            (
                "import json,os,pathlib,sys;"
                "pathlib.Path(sys.argv[1]).write_text("
                "json.dumps({'cwd':os.getcwd(),'argv':sys.argv[2:]},ensure_ascii=False),"
                "encoding='utf-8')"
            ),
            str(observed),
            *tricky,
        ]

        result = self.run_cli(
            str(self.repo / "scripts" / "evidence_run.sh"),
            TASK_ID,
            "test",
            *command,
            cwd=caller,
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse((caller / "artifacts").exists())
        command_rows = read_jsonl(self.artifact / "commands.jsonl")
        result_rows = read_jsonl(self.artifact / "results.jsonl")
        self.assertEqual(command_rows[0]["argv"], command)
        self.assertIsInstance(command_rows[0]["cmd"], str)
        self.assertEqual(result_rows[0]["rc"], 0)
        payload = json.loads(observed.read_text(encoding="utf-8"))
        self.assertEqual(Path(payload["cwd"]).resolve(), caller.resolve())
        self.assertEqual(payload["argv"], tricky)

    def install_fake_pytest(self) -> Path:
        marker = self.repo / "pytest-observed.json"
        write_executable(
            self.repo / "backend" / ".venv" / "bin" / "pytest",
            """
            #!/usr/bin/env python3
            import json
            import os
            from pathlib import Path
            import sys

            Path(os.environ["FAKE_PYTEST_MARKER"]).write_text(
                json.dumps({"cwd": os.getcwd(), "argv": sys.argv[1:]}),
                encoding="utf-8",
            )
            if signal_number := os.environ.get("FAKE_PYTEST_SIGNAL"):
                os.kill(os.getpid(), int(signal_number))
            raise SystemExit(int(os.environ.get("FAKE_PYTEST_RC", "0")))
            """,
        )
        return marker

    def backend_command(self, *extra: str) -> list[str]:
        return [
            sys.executable,
            str(self.repo / "scripts" / "evidence_task.py"),
            "backend-pytest",
            TASK_ID,
            *extra,
        ]

    def test_backend_red_preserves_real_nonzero_and_releases_own_lock(self) -> None:
        marker = self.install_fake_pytest()
        result = self.run_cli(
            *self.backend_command(
                "--step",
                "red",
                "--expect-nonzero",
                "--",
                "tests/test_one.py",
                "-k",
                "中文 case",
            ),
            env={"FAKE_PYTEST_MARKER": str(marker), "FAKE_PYTEST_RC": "3"},
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(self.lock_dir.exists())
        observed = json.loads(marker.read_text(encoding="utf-8"))
        self.assertEqual(
            Path(observed["cwd"]).resolve(), (self.repo / "backend").resolve()
        )
        self.assertEqual(observed["argv"], ["tests/test_one.py", "-k", "中文 case"])
        row = read_jsonl(self.artifact / "results.jsonl")[-1]
        self.assertEqual(row["rc"], 3)
        self.assertEqual(row["expectation"], "nonzero")
        self.assertIs(row["expectation_met"], True)

    def test_backend_green_propagates_nonzero_and_releases_own_lock(self) -> None:
        marker = self.install_fake_pytest()
        result = self.run_cli(
            *self.backend_command(
                "--step",
                "test",
                "--",
                "tests/test_one.py",
            ),
            env={"FAKE_PYTEST_MARKER": str(marker), "FAKE_PYTEST_RC": "4"},
        )

        self.assertEqual(result.returncode, 4, result.stdout)
        self.assertFalse(self.lock_dir.exists())
        self.assertEqual(read_jsonl(self.artifact / "results.jsonl")[-1]["rc"], 4)

    def test_backend_red_fails_when_pytest_unexpectedly_passes(self) -> None:
        marker = self.install_fake_pytest()
        result = self.run_cli(
            *self.backend_command(
                "--step",
                "red",
                "--expect-nonzero",
                "--",
                "tests/test_one.py",
            ),
            env={"FAKE_PYTEST_MARKER": str(marker), "FAKE_PYTEST_RC": "0"},
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.lock_dir.exists())
        row = read_jsonl(self.artifact / "results.jsonl")[-1]
        self.assertEqual(row["rc"], 0)
        self.assertIs(row["expectation_met"], False)

    def test_backend_red_rejects_missing_pytest_as_infrastructure_failure(self) -> None:
        result = self.run_cli(
            *self.backend_command(
                "--step",
                "red",
                "--expect-nonzero",
                "--",
                "tests/test_one.py",
            )
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.lock_dir.exists())
        row = read_jsonl(self.artifact / "results.jsonl")[-1]
        self.assertEqual(row["rc"], 127)
        self.assertIs(row["executed"], False)
        self.assertIs(row["expectation_met"], False)

    def test_backend_red_rejects_signal_termination_and_releases_lock(self) -> None:
        marker = self.install_fake_pytest()
        result = self.run_cli(
            *self.backend_command(
                "--step",
                "red",
                "--expect-nonzero",
                "--",
                "tests/test_one.py",
            ),
            env={"FAKE_PYTEST_MARKER": str(marker), "FAKE_PYTEST_SIGNAL": "15"},
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.lock_dir.exists())
        row = read_jsonl(self.artifact / "results.jsonl")[-1]
        self.assertEqual(row["rc"], -15)
        self.assertIs(row["executed"], True)
        self.assertIs(row["expectation_met"], False)

    def test_backend_lock_contention_fails_without_running_or_removing_owner(
        self,
    ) -> None:
        marker = self.install_fake_pytest()
        self.lock_dir.mkdir()
        self.owns_contention_fixture = True
        foreign = self.lock_dir / "foreign-owner"
        foreign.write_text("other", encoding="utf-8")
        result = self.run_cli(
            *self.backend_command(
                "--step",
                "test",
                "--",
                "tests/test_one.py",
            ),
            env={"FAKE_PYTEST_MARKER": str(marker), "FAKE_PYTEST_RC": "0"},
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(marker.exists())
        self.assertEqual(foreign.read_text(encoding="utf-8"), "other")
        row = read_jsonl(self.artifact / "results.jsonl")[-1]
        self.assertEqual(row["reason"], "sqlite_lock_contention")
        self.assertIs(row["executed"], False)
        foreign.unlink()
        self.lock_dir.rmdir()
        self.owns_contention_fixture = False

    def install_close_fixture(
        self,
        *,
        task_status: str = "PASS",
        review: str = "Verdict: APPROVED\nP0: 0\nP1: 0\nP2: 0\n",
    ) -> tuple[Path, Path, Path, Path]:
        task_file = self.repo / "tasks" / "task.md"
        task_file.parent.mkdir()
        task_file.write_text(f"# Task\n\nStatus: {task_status}\n", encoding="utf-8")
        summary = self.artifact / "summary.md"
        summary.write_text("# Summary\n\nStatus: PASS\n", encoding="utf-8")
        review_file = self.artifact / "review" / "independent_review.md"
        review_file.parent.mkdir()
        review_file.write_text(review, encoding="utf-8")
        (self.artifact / "task.json").write_text(
            json.dumps(
                {
                    "task_id": TASK_ID,
                    "task_file": "tasks/task.md",
                    "repo_root": str(self.repo),
                    "allowlist": ["tasks/task.md", f"artifacts/{TASK_ID}/**"],
                    "baseline_dirty": False,
                }
            ),
            encoding="utf-8",
        )
        for step in ("lint", "test"):
            log = self.artifact / "outputs" / f"initial_{step}.log"
            log.write_text("ok\n", encoding="utf-8")
            with (self.artifact / "results.jsonl").open(
                "a", encoding="utf-8"
            ) as stream:
                stream.write(
                    json.dumps(
                        {
                            "ts": "20260716T000000",
                            "step": step,
                            "rc": 0,
                            "log": f"artifacts/{TASK_ID}/outputs/{log.name}",
                        }
                    )
                    + "\n"
                )
        order = self.repo / "order.txt"
        self.install_close_script("evidence_finalize.sh", "scope", "FAIL_SCOPE", order)
        self.install_close_script(
            "evidence_validate.py", "independent_review", "FAIL_REVIEW", order
        )
        self.install_close_script(
            "task_validate.sh", "task_gate", "FAIL_TASK_GATE", order
        )
        self.install_close_script(
            "atomic_evidence_validate.py", "atomic_evidence", "FAIL_ATOMIC", order
        )
        return task_file, summary, review_file, order

    def install_close_script(
        self, name: str, label: str, failure_env: str, order: Path
    ) -> None:
        write_executable(
            self.repo / "scripts" / name,
            f"""
            #!/usr/bin/env python3
            import os
            from pathlib import Path
            with Path({str(order)!r}).open("a", encoding="utf-8") as stream:
                stream.write({label!r} + "\\n")
            raise SystemExit(int(os.environ.get({failure_env!r}, "0")))
            """,
        )

    def close_command(self) -> list[str]:
        return [
            sys.executable,
            str(self.repo / "scripts" / "evidence_task.py"),
            "close",
            TASK_ID,
        ]

    def test_close_requires_pass_status_before_recording(self) -> None:
        self.install_close_fixture(task_status="READY")
        before = (self.artifact / "results.jsonl").read_bytes()
        result = self.run_cli(*self.close_command())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.artifact / "results.jsonl").read_bytes(), before)

    def test_close_requires_exact_zero_finding_review_before_recording(self) -> None:
        self.install_close_fixture(review="Verdict: APPROVED\nP0: 0\nP1: 1\nP2: 0\n")
        before = (self.artifact / "results.jsonl").read_bytes()
        result = self.run_cli(*self.close_command())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.artifact / "results.jsonl").read_bytes(), before)

    def test_close_records_exact_order_and_preserves_governed_content(self) -> None:
        task_file, summary, review_file, order = self.install_close_fixture()
        governed = {path: sha256(path) for path in (task_file, summary, review_file)}
        history = (self.artifact / "results.jsonl").read_bytes()

        result = self.run_cli(*self.close_command())

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            order.read_text(encoding="utf-8").splitlines(),
            ["scope", "independent_review", "task_gate", "atomic_evidence"],
        )
        self.assertEqual(governed, {path: sha256(path) for path in governed})
        self.assertTrue(
            (self.artifact / "results.jsonl").read_bytes().startswith(history)
        )
        steps = [row["step"] for row in read_jsonl(self.artifact / "results.jsonl")]
        self.assertEqual(
            steps[-4:],
            ["scope", "independent_review", "task_gate", "atomic_evidence"],
        )

    def test_close_stops_immediately_after_each_failed_stage(self) -> None:
        scenarios = [
            ("FAIL_SCOPE", ["scope"]),
            ("FAIL_REVIEW", ["scope", "independent_review"]),
            ("FAIL_TASK_GATE", ["scope", "independent_review", "task_gate"]),
            (
                "FAIL_ATOMIC",
                ["scope", "independent_review", "task_gate", "atomic_evidence"],
            ),
        ]
        for failure_env, expected in scenarios:
            with self.subTest(failure_env=failure_env):
                self.tearDown()
                self.setUp()
                _, _, _, order = self.install_close_fixture()
                result = self.run_cli(*self.close_command(), env={failure_env: "9"})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(
                    order.read_text(encoding="utf-8").splitlines(), expected
                )
                steps = [
                    row["step"] for row in read_jsonl(self.artifact / "results.jsonl")
                ]
                self.assertEqual(steps[-len(expected) :], expected)


if __name__ == "__main__":
    unittest.main()
