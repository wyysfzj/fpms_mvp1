from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class GovernanceAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name).resolve()
        self.scripts = self.repo / "scripts"
        self.scripts.mkdir()
        for name in ("evidence_init.sh", "evidence_run.sh", "evidence_task.py"):
            shutil.copy2(ROOT / "scripts" / name, self.scripts / name)
        self.capture = self.repo / "capture.json"
        taskctl = self.scripts / "taskctl"
        taskctl.write_text(
            """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

Path(os.environ["FPMS_TEST_CAPTURE"]).write_text(
    json.dumps({"argv": sys.argv[1:], "cwd": os.getcwd()}),
    encoding="utf-8",
)
raise SystemExit(int(os.environ.get("FPMS_TEST_RC", "0")))
""",
            encoding="utf-8",
        )
        taskctl.chmod(taskctl.stat().st_mode | stat.S_IXUSR)
        self.environment = os.environ.copy()
        self.environment["FPMS_TEST_CAPTURE"] = str(self.capture)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_script(
        self,
        name: str,
        *arguments: str,
        cwd: Path | None = None,
        rc: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        environment = dict(self.environment)
        environment["FPMS_TEST_RC"] = str(rc)
        return subprocess.run(
            [str(self.scripts / name), *arguments],
            cwd=cwd or self.repo,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def captured(self) -> dict[str, object]:
        return json.loads(self.capture.read_text(encoding="utf-8"))

    def test_init_accepts_legacy_allowlist_syntax_but_taskctl_owns_scope(self) -> None:
        self.environment["FPMS_EVIDENCE_GATE_HELPER"] = "/missing/direct-helper.py"
        result = self.run_script(
            "evidence_init.sh",
            "TASK-01",
            "--task-file",
            "tasks/TASK-01.md",
            "--allowlist",
            "tasks/TASK-01.md",
            "--allowlist",
            "work/中文 文件.txt",
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            self.captured()["argv"],
            ["TASK-01", "start", "--task-file", "tasks/TASK-01.md"],
        )

        self.capture.unlink()
        result = self.run_script(
            "evidence_init.sh",
            "TASK-01",
            "--task-file",
            "tasks/TASK-01.md",
            "--allowlist",
            "tasks/TASK-01.md",
            "work/中文 文件.txt",
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            self.captured()["argv"],
            ["TASK-01", "start", "--task-file", "tasks/TASK-01.md"],
        )

    def test_init_rejects_unknown_missing_or_duplicate_contract_arguments(self) -> None:
        invalid = (
            ("TASK-01",),
            ("TASK-01", "--task-file", "tasks/TASK-01.md", "--unknown", "x"),
            (
                "TASK-01",
                "--task-file",
                "tasks/TASK-01.md",
                "--task-file",
                "tasks/OTHER.md",
            ),
            ("TASK-01", "--task-file", "tasks/TASK-01.md", "--allowlist"),
        )
        for arguments in invalid:
            with self.subTest(arguments=arguments):
                self.capture.unlink(missing_ok=True)
                result = self.run_script("evidence_init.sh", *arguments)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse(self.capture.exists())

    def test_run_preserves_caller_cwd_and_argument_boundaries(self) -> None:
        caller = self.repo / "nested caller"
        caller.mkdir()
        command = ("python3", "-c", "print('ok')", "中文 空格", "")

        result = self.run_script(
            "evidence_run.sh", "TASK-01", "lint", *command, cwd=caller
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            self.captured(),
            {
                "argv": ["TASK-01", "record", "lint", "--", *command],
                "cwd": str(caller),
            },
        )

    def test_python_compatibility_adapter_delegates_all_modes(self) -> None:
        caller = self.repo / "caller"
        caller.mkdir()
        commands = (
            (
                [
                    "run",
                    "TASK-01",
                    "lint",
                    "--cwd",
                    str(caller),
                    "--",
                    "python3",
                    "-c",
                    "pass",
                ],
                ["TASK-01", "record", "lint", "--", "python3", "-c", "pass"],
                caller,
            ),
            (
                [
                    "backend-pytest",
                    "TASK-01",
                    "--step",
                    "red",
                    "--expect-nonzero",
                    "--",
                    "tests/test_one.py",
                ],
                ["TASK-01", "backend-test", "red", "--", "tests/test_one.py"],
                self.repo,
            ),
            (["close", "TASK-01"], ["TASK-01", "close"], self.repo),
        )
        for arguments, expected, expected_cwd in commands:
            with self.subTest(arguments=arguments):
                self.capture.unlink(missing_ok=True)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(self.scripts / "evidence_task.py"),
                        *arguments,
                    ],
                    cwd=self.repo,
                    env=self.environment,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(self.captured()["argv"], expected)
                self.assertEqual(self.captured()["cwd"], str(expected_cwd))

    def test_adapters_propagate_taskctl_failure_without_fabricating_evidence(
        self,
    ) -> None:
        result = self.run_script("evidence_run.sh", "TASK-01", "lint", "true", rc=7)

        self.assertEqual(result.returncode, 7, result.stdout)
        self.assertFalse((self.repo / "artifacts").exists())

    def test_python_red_compatibility_requires_the_explicit_legacy_marker(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(self.scripts / "evidence_task.py"),
                "backend-pytest",
                "TASK-01",
                "--step",
                "red",
                "--",
                "tests/test_one.py",
            ],
            cwd=self.repo,
            env=self.environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertFalse(self.capture.exists())


if __name__ == "__main__":
    unittest.main()
