import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "task_validate.sh"
TASK_ID = "TEST-TASK-VALIDATE-JSONL"


class TaskValidateJsonlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.artifact_dir = self.root / "artifacts" / TASK_ID

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_gate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(SCRIPT), TASK_ID],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def create_complete_artifacts(self, lines: list[str]) -> None:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        (self.artifact_dir / "summary.md").write_text("# Summary\n\nStatus: PASS\n")
        (self.artifact_dir / "results.jsonl").write_text("\n".join(lines) + "\n")
        (self.artifact_dir / "task.json").write_text(
            json.dumps(
                {
                    "task_id": TASK_ID,
                    "task_file": f"tasks/{TASK_ID}.md",
                    "allowlist": [
                        f"tasks/{TASK_ID}.md",
                        f"artifacts/{TASK_ID}/**",
                    ],
                    "repo_root": self.root.as_posix(),
                    "baseline_dirty": False,
                }
            )
            + "\n"
        )
        outputs = self.artifact_dir / "outputs"
        outputs.mkdir()
        for line in lines:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and isinstance(record.get("log"), str):
                log = self.root / record["log"]
                if log.is_relative_to(outputs) and log.name != "missing.log":
                    log.parent.mkdir(parents=True, exist_ok=True)
                    log.write_text("fixture log\n")
        review = self.artifact_dir / "review"
        review.mkdir()
        (review / "independent_review.md").write_text(
            "Verdict: APPROVED\n\n- P0: none\n- P1: none\n- P2: none\n"
        )
        diff_dir = self.artifact_dir / "git"
        diff_dir.mkdir()
        (diff_dir / "diff.patch").write_text("diff\n")

    def record(self, step: str, rc: object, **extra: object) -> str:
        payload = {
            "step": step,
            "rc": rc,
            "log": f"artifacts/{TASK_ID}/outputs/{step}-{len(extra)}.log",
        }
        payload.update(extra)
        return json.dumps(payload, separators=(",", ":"))

    def assert_gate_fails(self, lines: list[str]) -> subprocess.CompletedProcess[str]:
        self.create_complete_artifacts(lines)
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_missing_artifacts_fail_in_order_with_existing_messages(self) -> None:
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing artifacts", result.stdout)

        self.artifact_dir.mkdir(parents=True)
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing summary", result.stdout)

        (self.artifact_dir / "summary.md").write_text("# Summary\n\nStatus: PASS\n")
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing results", result.stdout)

        (self.artifact_dir / "results.jsonl").write_text("")
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing git diff", result.stdout)

    def test_structural_records_allow_whitespace_key_order_and_extra_fields(
        self,
    ) -> None:
        self.create_complete_artifacts(
            [
                "   ",
                f'  {{ "rc": 0, "extra": true, "step": "lint", "log": "artifacts/{TASK_ID}/outputs/lint.log" }}',
                f'{{"other":"value", "step" : "test", "rc" : 0, "log": "artifacts/{TASK_ID}/outputs/test.log"}}',
            ]
        )
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Task Gate PASS", result.stdout)

    def test_fake_json_substring_does_not_satisfy_required_record(self) -> None:
        fake = json.dumps(
            {"step": "note", "rc": 1, "text": '"step":"lint","rc":0'},
            separators=(",", ":"),
        )
        self.assert_gate_fails([fake, self.record("test", 0)])

    def test_malformed_json_reports_physical_line_number(self) -> None:
        result = self.assert_gate_fails(
            [self.record("lint", 0), "{not-json", self.record("test", 0)]
        )
        self.assertIn("2", result.stdout + result.stderr)

    def test_each_non_object_json_value_fails_with_line_number(self) -> None:
        for value in ("[]", '"text"', "42", "true", "null"):
            with self.subTest(value=value):
                if self.artifact_dir.exists():
                    for path in sorted(self.artifact_dir.rglob("*"), reverse=True):
                        if path.is_file():
                            path.unlink()
                        else:
                            path.rmdir()
                    self.artifact_dir.rmdir()
                result = self.assert_gate_fails(
                    [value, self.record("lint", 0), self.record("test", 0)]
                )
                self.assertIn("1", result.stdout + result.stderr)

    def test_non_integer_zero_return_codes_do_not_count(self) -> None:
        invalid_values = (False, "0", 0.0)
        for step, other_step in (("lint", "test"), ("test", "lint")):
            for value in invalid_values:
                with self.subTest(step=step, value=value):
                    if self.artifact_dir.exists():
                        for path in sorted(self.artifact_dir.rglob("*"), reverse=True):
                            if path.is_file():
                                path.unlink()
                            else:
                                path.rmdir()
                        self.artifact_dir.rmdir()
                    self.assert_gate_fails(
                        [
                            self.record(step, value),
                            self.record(other_step, 0),
                        ]
                    )

    def test_omitting_either_required_success_fails(self) -> None:
        self.assert_gate_fails([self.record("lint", 0)])
        for path in sorted(self.artifact_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            else:
                path.rmdir()
        self.artifact_dir.rmdir()
        self.assert_gate_fails([self.record("test", 0)])

    def test_earlier_failures_then_exact_successes_pass(self) -> None:
        self.create_complete_artifacts(
            [
                self.record("lint", 1, attempt=1),
                self.record("test", 2, attempt=1),
                self.record("lint", 0, attempt=2),
                self.record("test", 0, attempt=2),
            ]
        )
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_success_returns_zero_and_prints_pass(self) -> None:
        self.create_complete_artifacts([self.record("lint", 0), self.record("test", 0)])
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Task Gate PASS", result.stdout)

    def test_latest_required_record_must_succeed(self) -> None:
        result = self.assert_gate_fails(
            [
                self.record("lint", 0, attempt=1),
                self.record("test", 0, attempt=1),
                self.record("lint", 1, attempt=2),
            ]
        )
        self.assertIn("latest", (result.stdout + result.stderr).lower())

    def test_required_log_must_be_normalized_existing_task_output(self) -> None:
        invalid_logs = (
            f"artifacts/{TASK_ID}/outputs/missing.log",
            "../escape.log",
            "artifacts/OTHER/outputs/test.log",
        )
        for invalid in invalid_logs:
            with self.subTest(log=invalid):
                if self.artifact_dir.exists():
                    for path in sorted(self.artifact_dir.rglob("*"), reverse=True):
                        if path.is_file():
                            path.unlink()
                        else:
                            path.rmdir()
                    self.artifact_dir.rmdir()
                result = self.assert_gate_fails(
                    [
                        self.record("lint", 0),
                        json.dumps({"step": "test", "rc": 0, "log": invalid}),
                    ]
                )
                self.assertIn("log", result.stdout + result.stderr)

    def test_summary_review_and_dirty_baseline_fail_closed(self) -> None:
        valid = [self.record("lint", 0), self.record("test", 0)]
        mutations = ("summary", "review", "finding", "dirty_baseline")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                if self.artifact_dir.exists():
                    for path in sorted(self.artifact_dir.rglob("*"), reverse=True):
                        if path.is_file():
                            path.unlink()
                        else:
                            path.rmdir()
                    self.artifact_dir.rmdir()
                self.create_complete_artifacts(valid)
                if mutation == "summary":
                    (self.artifact_dir / "summary.md").write_text("Status: FAIL\n")
                elif mutation == "review":
                    (self.artifact_dir / "review/independent_review.md").unlink()
                elif mutation == "finding":
                    (self.artifact_dir / "review/independent_review.md").write_text(
                        "Verdict: APPROVED\nP0: 0\nP1: 1\nP2: 0\n"
                    )
                else:
                    metadata_path = self.artifact_dir / "task.json"
                    metadata = json.loads(metadata_path.read_text())
                    metadata["baseline_dirty"] = True
                    metadata_path.write_text(json.dumps(metadata))
                result = self.run_gate()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "summary"
                    if mutation == "summary"
                    else "review"
                    if mutation in {"review", "finding"}
                    else "baseline",
                    (result.stdout + result.stderr).lower(),
                )


if __name__ == "__main__":
    unittest.main()
