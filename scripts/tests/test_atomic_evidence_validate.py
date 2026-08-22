from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


WRAPPER = Path(__file__).resolve().parents[1] / "atomic_evidence_validate.py"
CURRENT = "CURRENT-TASK"
PEER_ONE = "PEER-ONE"
PEER_TWO = "PEER-TWO"


class RepositoryFixture:
    def __init__(self, root: Path, manifest_form: str = "heading") -> None:
        self.root = root
        self.manifest = root / "tasks" / "batch.md"
        self.task_paths = {
            CURRENT: "tasks/CURRENT-TASK.md",
            PEER_ONE: "tasks/PEER-ONE.md",
            PEER_TWO: "tasks/PEER-TWO.md",
        }
        self.allowlists = {
            CURRENT: [
                self.task_paths[CURRENT],
                "work/current.txt",
                f"artifacts/{CURRENT}/**",
            ],
            PEER_ONE: [
                self.task_paths[PEER_ONE],
                "work/peer one.txt",
                f"artifacts/{PEER_ONE}/**",
            ],
            PEER_TWO: [
                self.task_paths[PEER_TWO],
                "work/peer -> two.txt",
                f"artifacts/{PEER_TWO}/**",
            ],
        }
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test User")
        for task_id in (CURRENT, PEER_ONE, PEER_TWO):
            self.write_task(task_id)
        for path in ("work/current.txt", "work/peer one.txt", "work/peer -> two.txt"):
            self.write(path, "baseline\n")
        self.write_manifest(manifest_form)
        self._git("add", ".")
        self._git("commit", "-qm", "baseline")
        for task_id in (CURRENT, PEER_ONE, PEER_TWO):
            self.write_metadata(task_id)
        self.write_evidence(CURRENT)

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_task(self, task_id: str) -> None:
        entries = "\n".join(f"- `{item}`" for item in self.allowlists[task_id])
        self.write(
            self.task_paths[task_id], f"# {task_id}\n\n## Allowed Files\n\n{entries}\n"
        )

    def write_metadata(self, declared_id: str, **overrides: object) -> None:
        metadata: dict[str, object] = {
            "task_id": declared_id,
            "task_file": self.task_paths[declared_id],
            "allowlist": self.allowlists[declared_id],
            "repo_root": self.root.resolve().as_posix(),
            "baseline_dirty": False,
        }
        metadata.update(overrides)
        self.write(
            f"artifacts/{declared_id}/task.json",
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        )

    def write_evidence(
        self,
        task_id: str,
        successful_steps: tuple[str, ...] = ("lint", "test", "scope"),
    ) -> None:
        artifact = self.root / "artifacts" / task_id
        (artifact / "git").mkdir(parents=True, exist_ok=True)
        (artifact / "summary.md").write_text(
            "# Summary\n\nStatus: PASS\n", encoding="utf-8"
        )
        (artifact / "git" / "diff.patch").write_text("fixture\n", encoding="utf-8")
        (artifact / "outputs").mkdir(exist_ok=True)
        records = ""
        for step in successful_steps:
            log = artifact / "outputs" / f"{step}.log"
            log.write_text("fixture log\n", encoding="utf-8")
            records += (
                json.dumps(
                    {
                        "step": step,
                        "rc": 0,
                        "log": log.relative_to(self.root).as_posix(),
                    }
                )
                + "\n"
            )
        (artifact / "results.jsonl").write_text(records, encoding="utf-8")
        (artifact / "review").mkdir(exist_ok=True)
        (artifact / "review" / "independent_review.md").write_text(
            "Verdict: APPROVED\n\nP0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )

    def write_manifest(
        self, form: str = "heading", rows: tuple[str, ...] | None = None
    ) -> None:
        task_ids = rows or (CURRENT, PEER_ONE, PEER_TWO)
        if form == "heading":
            text = "# Batch\n\n" + "\n".join(
                f"## {index:03d}. {task_id}\n\n"
                f"- Task file: `{self.task_paths[task_id]}`\n"
                for index, task_id in enumerate(task_ids, start=1)
            )
        elif form == "table":
            body = "\n".join(
                f"| {index:03d} | `{task_id}` | `{self.task_paths[task_id]}` |"
                for index, task_id in enumerate(task_ids, start=1)
            )
            text = (
                "# Batch\n\n| Row | Task ID | Task file |\n| --- | --- | --- |\n"
                + body
                + "\n"
            )
        else:
            body = "\n".join(
                f"| {index:03d} | H3-2 | `{self.task_paths[task_id]}` |"
                for index, task_id in enumerate(task_ids, start=1)
            )
            text = (
                "# Batch\n\n| Row | Wave | Exact task-file path |\n"
                "| --- | --- | --- |\n" + body + "\n"
            )
        self.manifest.write_text(text, encoding="utf-8")

    def run_wrapper(
        self,
        *extra: str,
        task_id: str = CURRENT,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(WRAPPER), task_id, *extra],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def peer_args(self) -> tuple[str, ...]:
        return (
            "--required-step",
            "lint",
            "--required-step",
            "test",
            "--manifest",
            self.manifest.relative_to(self.root).as_posix(),
            "--concurrent-task",
            PEER_ONE,
            "--concurrent-task",
            PEER_TWO,
        )


class AtomicEvidenceValidateTests(unittest.TestCase):
    def fixture(
        self, manifest_form: str = "heading"
    ) -> tuple[tempfile.TemporaryDirectory[str], RepositoryFixture]:
        temporary = tempfile.TemporaryDirectory()
        return temporary, RepositoryFixture(Path(temporary.name), manifest_form)

    def assert_rejected(
        self, result: subprocess.CompletedProcess[str], *needles: str
    ) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        diagnostic = (result.stdout + result.stderr).lower()
        for needle in needles:
            self.assertIn(needle.lower(), diagnostic)

    def test_no_peer_delegates_forwards_output_and_propagates_return_codes(
        self,
    ) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        shutil.rmtree(repo.root / f"artifacts/{PEER_ONE}")
        shutil.rmtree(repo.root / f"artifacts/{PEER_TWO}")

        passed = repo.run_wrapper("--required-step", "lint", "--required-step", "test")
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
        self.assertIn("Task Gate PASS", passed.stdout)

        failed = repo.run_wrapper("--required-step", "missing-step")
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("Missing successful required steps: missing-step", failed.stderr)

    def test_no_peer_rejects_manifest(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        shutil.rmtree(repo.root / f"artifacts/{PEER_ONE}")
        shutil.rmtree(repo.root / f"artifacts/{PEER_TWO}")
        result = repo.run_wrapper("--manifest", "tasks/batch.md")
        self.assert_rejected(result, "manifest", "peer")

    def test_no_peer_uses_shared_latest_result_semantics(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        shutil.rmtree(repo.root / f"artifacts/{PEER_ONE}")
        shutil.rmtree(repo.root / f"artifacts/{PEER_TWO}")
        failed_log = repo.root / f"artifacts/{CURRENT}/outputs/lint-failed.log"
        failed_log.write_text("failed\n", encoding="utf-8")
        with (repo.root / f"artifacts/{CURRENT}/results.jsonl").open(
            "a", encoding="utf-8"
        ) as results:
            results.write(
                json.dumps(
                    {
                        "step": "lint",
                        "rc": 1,
                        "log": failed_log.relative_to(repo.root).as_posix(),
                    }
                )
                + "\n"
            )

        result = repo.run_wrapper("--required-step", "lint")

        self.assert_rejected(result, "latest", "lint")

    def test_valid_two_peer_wave_supports_all_manifest_forms(self) -> None:
        for form in ("heading", "table", "path_only"):
            with self.subTest(form=form):
                temporary, repo = self.fixture(form)
                self.addCleanup(temporary.cleanup)
                repo.write("work/current.txt", "current change\n")
                repo.write("work/peer one.txt", "peer one change\n")
                repo.write("work/peer -> two.txt", "peer two change\n")
                result = repo.run_wrapper(*repo.peer_args())
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Task Gate PASS", result.stdout)

    def test_explicit_table_id_mismatch_never_falls_back_to_path_stem(self) -> None:
        temporary, repo = self.fixture("table")
        self.addCleanup(temporary.cleanup)
        text = repo.manifest.read_text(encoding="utf-8")
        repo.manifest.write_text(
            text.replace("| `CURRENT-TASK` |", "| `WRONG-TASK` |", 1),
            encoding="utf-8",
        )

        self.assert_rejected(repo.run_wrapper(*repo.peer_args()), "manifest", CURRENT)

    def test_authoritative_delta3_manifest_has_exact_h3_2_pairs(self) -> None:
        module = __import__(
            "scripts.atomic_evidence_validate", fromlist=["parse_manifest"]
        )
        manifest = (
            WRAPPER.parents[1]
            / "tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md"
        )
        rows = module.parse_manifest(manifest)
        expected = (
            (
                "FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01",
                "tasks/postdemo/v8/FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01.md",
            ),
            (
                "FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01",
                "tasks/postdemo/v8/FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01.md",
            ),
        )
        for pair in expected:
            with self.subTest(pair=pair):
                self.assertEqual(rows.count(pair), 1)

    def test_peer_cli_rejects_missing_repeated_or_invalid_relationships(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        cases = (
            (("--concurrent-task", PEER_ONE), ("manifest",)),
            (
                (
                    "--manifest",
                    "tasks/batch.md",
                    "--manifest",
                    "tasks/batch.md",
                    "--concurrent-task",
                    PEER_ONE,
                ),
                ("manifest", "once"),
            ),
            (
                ("--manifest", "tasks/batch.md", "--concurrent-task", CURRENT),
                ("current", "peer"),
            ),
            (
                (
                    "--manifest",
                    "tasks/batch.md",
                    "--concurrent-task",
                    PEER_ONE,
                    "--concurrent-task",
                    PEER_ONE,
                ),
                ("duplicate", "peer"),
            ),
        )
        for args, needles in cases:
            with self.subTest(args=args):
                self.assert_rejected(repo.run_wrapper(*args), *needles)

    def test_manifest_absence_duplication_and_path_mismatch_fail_closed(self) -> None:
        mutations = ("missing", "duplicate", "mismatch")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                temporary, repo = self.fixture()
                self.addCleanup(temporary.cleanup)
                if mutation == "missing":
                    repo.write_manifest(rows=(PEER_ONE, PEER_TWO))
                elif mutation == "duplicate":
                    repo.write_manifest(rows=(CURRENT, CURRENT, PEER_ONE, PEER_TWO))
                else:
                    text = repo.manifest.read_text(encoding="utf-8")
                    repo.manifest.write_text(
                        text.replace("tasks/CURRENT-TASK.md", "tasks/WRONG.md"),
                        encoding="utf-8",
                    )
                self.assert_rejected(
                    repo.run_wrapper(*repo.peer_args()), "manifest", CURRENT
                )

    def test_manifest_symlink_or_symlink_parent_escape_fails_before_parse(self) -> None:
        for kind in ("manifest", "parent"):
            with self.subTest(kind=kind):
                temporary, repo = self.fixture()
                self.addCleanup(temporary.cleanup)
                outside = tempfile.TemporaryDirectory()
                self.addCleanup(outside.cleanup)
                outside_manifest = Path(outside.name) / "batch.md"
                outside_manifest.write_text(
                    repo.manifest.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
                if kind == "manifest":
                    repo.manifest.unlink()
                    repo.manifest.symlink_to(outside_manifest)
                    manifest = "tasks/batch.md"
                else:
                    (repo.root / "linked-manifest").symlink_to(
                        Path(outside.name),
                        target_is_directory=True,
                    )
                    manifest = "linked-manifest/batch.md"
                result = repo.run_wrapper(
                    "--manifest",
                    manifest,
                    "--concurrent-task",
                    PEER_ONE,
                    "--concurrent-task",
                    PEER_TWO,
                )
                self.assert_rejected(result, "manifest", "symlink", "local")

    def test_task_metadata_missing_or_identity_fields_mismatch_fail_closed(
        self,
    ) -> None:
        mutations = {
            "missing": None,
            "task_id": {"task_id": "WRONG"},
            "task_file": {"task_file": "tasks/WRONG.md"},
            "repo_root": {"repo_root": "/wrong/repository"},
            "allowlist": {"allowlist": ["work/current.txt"]},
        }
        for name, overrides in mutations.items():
            with self.subTest(name=name):
                temporary, repo = self.fixture()
                self.addCleanup(temporary.cleanup)
                metadata = repo.root / f"artifacts/{CURRENT}/task.json"
                if overrides is None:
                    metadata.unlink()
                else:
                    repo.write_metadata(CURRENT, **overrides)
                self.assert_rejected(repo.run_wrapper(*repo.peer_args()), "task.json")

    def test_task_file_allowlist_must_equal_metadata_allowlist(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        repo.allowlists[CURRENT] = [
            repo.task_paths[CURRENT],
            "work/different.txt",
            f"artifacts/{CURRENT}/**",
        ]
        repo.write_task(CURRENT)
        result = repo.run_wrapper(*repo.peer_args())
        self.assert_rejected(result, "allowlist", "task.json")

    def test_peer_must_explicitly_own_its_exact_evidence_glob(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        repo.allowlists[PEER_ONE] = [
            entry
            for entry in repo.allowlists[PEER_ONE]
            if entry != f"artifacts/{PEER_ONE}/**"
        ]
        repo.write_task(PEER_ONE)
        repo.write_metadata(PEER_ONE)

        result = repo.run_wrapper(*repo.peer_args())

        self.assert_rejected(result, "evidence", "allowlist")

    def test_invalid_allowlist_forms_fail_closed(self) -> None:
        invalid_entries = {
            "absolute": "/tmp/absolute.txt",
            "parent": "../escape.txt",
            "directory": "work",
            "glob": "work/*.txt",
            "foreign_artifact": f"artifacts/{PEER_ONE}/**",
            "symlink": "work/link.txt",
            "symlink_escape": "linked-dir/outside.txt",
        }
        for name, entry in invalid_entries.items():
            with self.subTest(name=name):
                temporary, repo = self.fixture()
                self.addCleanup(temporary.cleanup)
                if name == "symlink":
                    (repo.root / entry).symlink_to(repo.root / "work/current.txt")
                elif name == "symlink_escape":
                    outside = repo.root.parent / f"{repo.root.name}-outside"
                    outside.mkdir()
                    self.addCleanup(shutil.rmtree, outside, True)
                    (repo.root / "linked-dir").symlink_to(
                        outside, target_is_directory=True
                    )
                repo.allowlists[CURRENT] = [
                    repo.task_paths[CURRENT],
                    entry,
                    f"artifacts/{CURRENT}/**",
                ]
                repo.write_task(CURRENT)
                repo.write_metadata(CURRENT)
                self.assert_rejected(repo.run_wrapper(*repo.peer_args()), "allowlist")

    def test_exact_and_path_prefix_ownership_overlap_fail_before_helper(self) -> None:
        overlaps = (
            ("work/shared.txt", "work/shared.txt"),
            ("work/shared", "work/shared/child.txt"),
        )
        for current_path, peer_path in overlaps:
            with self.subTest(current=current_path, peer=peer_path):
                temporary, repo = self.fixture()
                self.addCleanup(temporary.cleanup)
                repo.allowlists[CURRENT][1] = current_path
                repo.allowlists[PEER_ONE][1] = peer_path
                repo.write_task(CURRENT)
                repo.write_task(PEER_ONE)
                repo.write_metadata(CURRENT)
                repo.write_metadata(PEER_ONE)
                self.assert_rejected(repo.run_wrapper(*repo.peer_args()), "overlap")

    def test_baseline_peer_unknown_and_multiply_owned_dirt(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        repo.write("preexisting.txt", "baseline external\n")
        repo.write(
            f"artifacts/{CURRENT}/baseline_external_files.txt",
            "preexisting.txt\n",
        )
        repo.write("work/peer one.txt", "owned peer dirt\n")
        accepted = repo.run_wrapper(*repo.peer_args())
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)

        repo.write("unknown.txt", "unknown\n")
        self.assert_rejected(repo.run_wrapper(*repo.peer_args()), "unknown.txt")

        repo.allowlists[PEER_TWO][1] = "work/peer one.txt"
        repo.write_task(PEER_TWO)
        repo.write_metadata(PEER_TWO)
        self.assert_rejected(repo.run_wrapper(*repo.peer_args()), "overlap")

    def test_nul_safe_status_preserves_spaces_and_arrow_text(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        repo.write("work/peer one.txt", "space name dirt\n")
        repo.write("work/peer -> two.txt", "arrow text dirt\n")
        result = repo.run_wrapper(*repo.peer_args())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_rename_rejects_and_reports_both_paths(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        repo._git("mv", "work/peer one.txt", "work/peer renamed.txt")
        result = repo.run_wrapper(*repo.peer_args())
        self.assert_rejected(
            result, "rename", "work/peer one.txt", "work/peer renamed.txt"
        )

    def test_copy_and_rename_porcelain_records_reject_both_paths(self) -> None:
        self.assertTrue(WRAPPER.exists(), "public CLI wrapper is absent")
        module = __import__(
            "scripts.atomic_evidence_validate", fromlist=["parse_status"]
        )
        for status, kind in (
            (b"R  new name\0old name\0", "rename"),
            (b"C  copy\0source\0", "copy"),
        ):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(
                    ValueError, rf"{kind}.*new name|{kind}.*copy"
                ) as raised:
                    module.parse_status(status)
                message = str(raised.exception)
                if kind == "rename":
                    self.assertIn("old name", message)
                else:
                    self.assertIn("source", message)

    def test_isolated_clone_copies_current_changes_deletion_and_artifacts_only(
        self,
    ) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        repo.write("work/current.txt", "current changed\n")
        repo.write("work/delete-me.txt", "delete baseline\n")
        repo._git("add", "work/delete-me.txt")
        repo._git("commit", "-qm", "add deletion fixture")
        (repo.root / "work/delete-me.txt").unlink()
        repo.allowlists[CURRENT].insert(2, "work/delete-me.txt")
        repo.write_task(CURRENT)
        repo.write_metadata(CURRENT)
        repo.write("work/peer one.txt", "peer poison\n")
        repo.write(f"artifacts/{PEER_ONE}/poison.txt", "peer artifact poison\n")
        helper_directory = tempfile.TemporaryDirectory()
        self.addCleanup(helper_directory.cleanup)
        helper = Path(helper_directory.name) / "assert_clone_content.py"
        helper.write_text(
            "from pathlib import Path\n"
            "root = Path.cwd()\n"
            "failures = []\n"
            "if (root / 'work/current.txt').read_text() != 'current changed\\n':\n"
            "    failures.append('current modification missing')\n"
            "if (root / 'work/delete-me.txt').exists():\n"
            "    failures.append('current deletion missing')\n"
            f"if not (root / 'artifacts/{CURRENT}/task.json').is_file():\n"
            "    failures.append('current artifact missing')\n"
            "if (root / 'work/peer one.txt').read_text() != 'baseline\\n':\n"
            "    failures.append('peer source contaminated')\n"
            f"if (root / 'artifacts/{PEER_ONE}').exists():\n"
            "    failures.append('peer artifact contaminated')\n"
            "if failures:\n"
            "    raise SystemExit(', '.join(failures))\n",
            encoding="utf-8",
        )
        module = __import__(
            "scripts.atomic_evidence_validate", fromlist=["delegate_isolated"]
        )
        with mock.patch.object(module, "EVIDENCE_CONSUMER", helper):
            with mock.patch.object(module, "copy_current_task", return_value=None):
                mutation_result = module.delegate_isolated(
                    repo.root,
                    CURRENT,
                    repo.allowlists[CURRENT],
                    ["lint", "test"],
                )
            result = module.delegate_isolated(
                repo.root,
                CURRENT,
                repo.allowlists[CURRENT],
                ["lint", "test"],
            )
        self.assertNotEqual(mutation_result, 0)
        self.assertEqual(result, 0)

    def test_deleted_tracked_symlink_is_not_a_rebuildable_regular_file(self) -> None:
        temporary, repo = self.fixture()
        self.addCleanup(temporary.cleanup)
        deleted_link = repo.root / "work/deleted-link.txt"
        deleted_link.symlink_to("current.txt")
        repo._git("add", "work/deleted-link.txt")
        repo._git("commit", "-qm", "add tracked symlink")
        deleted_link.unlink()
        repo.allowlists[CURRENT].insert(2, "work/deleted-link.txt")
        repo.write_task(CURRENT)
        repo.write_metadata(CURRENT)

        result = repo.run_wrapper(*repo.peer_args())

        self.assert_rejected(result, "work/deleted-link.txt", "mode")

    def test_helper_propagation_and_temp_cleanup_on_success_and_failure(self) -> None:
        for required_step, expected_rc in (("lint", 0), ("absent", 1)):
            with self.subTest(required_step=required_step):
                temporary, repo = self.fixture()
                self.addCleanup(temporary.cleanup)
                temp_parent = repo.root / "temporary-parent"
                temp_parent.mkdir()
                before = tuple(temp_parent.iterdir())
                with mock.patch.dict("os.environ", {"TMPDIR": str(temp_parent)}):
                    result = repo.run_wrapper(
                        "--required-step",
                        required_step,
                        "--manifest",
                        "tasks/batch.md",
                        "--concurrent-task",
                        PEER_ONE,
                        "--concurrent-task",
                        PEER_TWO,
                    )
                self.assertEqual(
                    result.returncode, expected_rc, result.stdout + result.stderr
                )
                self.assertEqual(tuple(temp_parent.iterdir()), before)
                if expected_rc == 0:
                    self.assertIn("Task Gate PASS", result.stdout)
                else:
                    self.assertIn(
                        "Missing successful required steps: absent", result.stderr
                    )


if __name__ == "__main__":
    unittest.main()
