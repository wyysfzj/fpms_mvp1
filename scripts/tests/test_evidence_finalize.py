from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest


FINALIZE = Path(__file__).resolve().parents[1] / "evidence_finalize.sh"
INITIALIZE = Path(__file__).resolve().parents[1] / "evidence_init.sh"
TASK_ID = "EVIDENCE-PRODUCER-FIXTURE"


class RepositoryFixture:
    def __init__(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test User")
        self.write("tasks/task.md", "task baseline\n")
        self.write("work/allowed.txt", "tracked baseline\n")
        self.write("work/delete.txt", "delete baseline\n")
        self.write("work/tool.sh", "#!/bin/sh\nexit 0\n")
        self.write_bytes("work/data.bin", b"\x00baseline\xff")
        self.write("outside.txt", "outside baseline\n")
        self._git("add", ".")
        self._git("commit", "-qm", "baseline")

    def cleanup(self) -> None:
        self.temporary.cleanup()

    def _git(
        self,
        *args: str,
        env: dict[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )

    def write(self, relative: str, text: str) -> None:
        self.write_bytes(relative, text.encode())

    def write_bytes(self, relative: str, content: bytes) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    @property
    def artifact(self) -> Path:
        return self.root / "artifacts" / TASK_ID

    @property
    def allowlist(self) -> list[str]:
        return [
            "tasks/task.md",
            "work/allowed.txt",
            "work/delete.txt",
            "work/tool.sh",
            "work/data.bin",
            "work/new/**",
            f"artifacts/{TASK_ID}/**",
        ]

    def initialize(self, *, baseline_dirty: bool) -> None:
        self.artifact.mkdir(parents=True)
        metadata = {
            "task_id": TASK_ID,
            "task_file": "tasks/task.md",
            "allowlist": self.allowlist,
            "repo_root": self.root.resolve().as_posix(),
            "baseline_dirty": baseline_dirty,
        }
        (self.artifact / "task.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        (self.artifact / "baseline_external_files.txt").write_text(
            "outside.txt\n" if baseline_dirty else "", encoding="utf-8"
        )
        if baseline_dirty:
            baseline = self._git(
                "diff",
                "--binary",
                "--full-index",
                "--",
                *self.allowlist[:-1],
            ).stdout
            (self.artifact / "baseline_allowlist.diff").write_bytes(baseline)

    def run_finalize(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(FINALIZE), TASK_ID],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def run_initialize(self) -> subprocess.CompletedProcess[str]:
        command = [
            str(INITIALIZE),
            TASK_ID,
            "--task-file",
            "tasks/task.md",
        ]
        for entry in self.allowlist:
            command.extend(("--allowlist", entry))
        return subprocess.run(
            command,
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def apply_scoped_patch_to_baseline(self) -> str:
        index = self.root / "verify.index"
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(index)
        self._git("read-tree", "HEAD", env=env)
        baseline = self.artifact / "baseline_allowlist.diff"
        if baseline.exists() and baseline.stat().st_size:
            self._git("apply", "--cached", "--binary", str(baseline), env=env)
        self._git(
            "apply",
            "--cached",
            "--binary",
            str(self.artifact / "git" / "diff.patch"),
            env=env,
        )
        return self._git("write-tree", env=env).stdout.decode().strip()

    def current_allowed_tree(self) -> str:
        index = self.root / "current.index"
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(index)
        self._git("read-tree", "HEAD", env=env)
        concrete = [entry.removesuffix("/**") for entry in self.allowlist[:-1]]
        self._git("add", "-A", "-f", "--", *concrete, env=env)
        return self._git("write-tree", env=env).stdout.decode().strip()


class EvidenceFinalizeTests(unittest.TestCase):
    def fixture(self) -> RepositoryFixture:
        repo = RepositoryFixture()
        self.addCleanup(repo.cleanup)
        return repo

    def test_writes_exact_baseline_subtracted_tracked_and_untracked_patch(self) -> None:
        repo = self.fixture()
        repo.write("work/allowed.txt", "user dirty baseline\n")
        repo.write("outside.txt", "user outside baseline\n")
        repo.initialize(baseline_dirty=True)

        repo.write("tasks/task.md", "task final\n")
        repo.write("work/allowed.txt", "user dirty baseline\ntask delta\n")
        (repo.root / "work/delete.txt").unlink()
        (repo.root / "work/tool.sh").chmod(
            (repo.root / "work/tool.sh").stat().st_mode | stat.S_IXUSR
        )
        repo.write_bytes("work/data.bin", b"\x00task-final\xfe")
        repo.write_bytes("work/new/untracked.bin", b"\x00new\xfd")
        repo.write("outside.txt", "outside changed again\n")
        repo.write("artifacts/EVIDENCE-PRODUCER-FIXTURE/internal.txt", "evidence\n")

        result = repo.run_finalize()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        patch = (repo.artifact / "git/diff.patch").read_bytes()
        self.assertIn(b"work/new/untracked.bin", patch)
        self.assertIn(b"deleted file mode", patch)
        self.assertIn(b"old mode 100644", patch)
        self.assertIn(b"new mode 100755", patch)
        self.assertNotIn(b"outside.txt", patch)
        self.assertNotIn(b"artifacts/EVIDENCE-PRODUCER-FIXTURE", patch)
        self.assertEqual(
            repo.apply_scoped_patch_to_baseline(), repo.current_allowed_tree()
        )
        self.assertTrue((repo.artifact / "git/status.txt").is_file())
        self.assertTrue((repo.artifact / "git/rev.txt").is_file())
        self.assertTrue((repo.artifact / "summary.md").is_file())

    def test_clean_baseline_includes_allowed_untracked_but_excludes_outside(
        self,
    ) -> None:
        repo = self.fixture()
        repo.initialize(baseline_dirty=False)
        repo.write("work/allowed.txt", "task change\n")
        repo.write_bytes("work/new/untracked.bin", b"new")
        repo.write("outside.txt", "outside change\n")

        result = repo.run_finalize()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        patch = (repo.artifact / "git/diff.patch").read_text(
            encoding="utf-8", errors="replace"
        )
        self.assertIn("work/allowed.txt", patch)
        self.assertIn("work/new/untracked.bin", patch)
        self.assertNotIn("outside.txt", patch)

    def test_reconstructs_legacy_staged_then_unstaged_dirty_baseline(self) -> None:
        repo = self.fixture()
        repo.write("work/allowed.txt", "staged baseline\n")
        repo._git("add", "work/allowed.txt")
        repo.write("work/allowed.txt", "staged and unstaged baseline\n")
        repo.initialize(baseline_dirty=True)
        unstaged = repo._git("diff", "--binary", "--", "work/allowed.txt").stdout
        staged = repo._git(
            "diff", "--cached", "--binary", "--", "work/allowed.txt"
        ).stdout
        (repo.artifact / "baseline_allowlist.diff").write_bytes(
            unstaged + b"\n" + staged
        )
        repo.write("work/allowed.txt", "task final\n")

        result = repo.run_finalize()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        patch = (repo.artifact / "git/diff.patch").read_text(encoding="utf-8")
        self.assertIn("-staged and unstaged baseline", patch)
        self.assertIn("+task final", patch)
        self.assertNotIn("-tracked baseline", patch)

    def test_repository_init_captures_untracked_baseline_and_exact_external_paths(
        self,
    ) -> None:
        repo = self.fixture()
        repo.write("work/new/existing.txt", "pre-task untracked\n")
        repo.write("outside dir/one.txt", "one\n")
        repo.write("outside dir/two.txt", "two\n")

        initialized = repo.run_initialize()

        self.assertEqual(
            initialized.returncode, 0, initialized.stdout + initialized.stderr
        )
        baseline = (repo.artifact / "baseline_allowlist.diff").read_text(
            encoding="utf-8"
        )
        self.assertIn("work/new/existing.txt", baseline)
        external = (repo.artifact / "baseline_external_files.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("outside dir/one.txt", external)
        self.assertIn("outside dir/two.txt", external)
        self.assertNotIn("outside dir/\n", external)

        repo.write("work/new/existing.txt", "task changed existing\n")
        repo.write("work/new/task.txt", "task new\n")
        finalized = repo.run_finalize()

        self.assertEqual(finalized.returncode, 0, finalized.stdout + finalized.stderr)
        patch = (repo.artifact / "git/diff.patch").read_text(encoding="utf-8")
        self.assertIn("work/new/existing.txt", patch)
        self.assertIn("-pre-task untracked", patch)
        self.assertIn("+task changed existing", patch)
        self.assertIn("work/new/task.txt", patch)
        self.assertEqual(
            repo.apply_scoped_patch_to_baseline(), repo.current_allowed_tree()
        )

    def test_fails_closed_for_missing_dirty_baseline(self) -> None:
        repo = self.fixture()
        repo.initialize(baseline_dirty=True)
        (repo.artifact / "baseline_allowlist.diff").unlink()

        result = repo.run_finalize()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("baseline_allowlist.diff", result.stderr)

    def test_fails_closed_for_repository_mismatch_and_unsafe_allowlist(self) -> None:
        for mutation, needle in (
            (("repo_root", "/wrong/repository"), "repo_root"),
            (("allowlist", ["../escape.txt"]), "allowlist"),
        ):
            with self.subTest(mutation=mutation):
                repo = self.fixture()
                repo.initialize(baseline_dirty=False)
                metadata_path = repo.artifact / "task.json"
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                metadata[mutation[0]] = mutation[1]
                metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

                result = repo.run_finalize()

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(needle, result.stderr)


if __name__ == "__main__":
    unittest.main()
