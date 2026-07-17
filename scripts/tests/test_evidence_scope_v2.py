from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCOPE = ROOT / "scripts/evidence_scope.py"
TASK_ID = "SCOPE-V2"


class ScopeFixture:
    def __init__(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir()
        shutil.copy2(SCOPE, self.root / "scripts/evidence_scope.py")
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write("tasks/task.md", "baseline\n")
        self.write("work/allowed.txt", "baseline\n")
        self.write("work/delete.txt", "delete\n")
        self.write("work/中文.txt", "中文基线\n")
        self.write("outside.txt", "outside\n")
        self.write(".gitignore", "artifacts/\n")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")
        self.artifact = self.root / "artifacts" / TASK_ID
        self.artifact.mkdir(parents=True)

    def cleanup(self) -> None:
        self.temporary.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def metadata(self, *, dirty: bool, task_id: str = TASK_ID) -> Path:
        artifact = self.root / "artifacts" / task_id
        artifact.mkdir(parents=True, exist_ok=True)
        (artifact / "task.json").write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "task_file": "tasks/task.md",
                    "allowlist": ["tasks/task.md", "work/**"],
                    "repo_root": str(self.root.resolve()),
                    "baseline_dirty": dirty,
                }
            ),
            encoding="utf-8",
        )
        (artifact / "baseline_allowlist.diff").write_bytes(b"")
        (artifact / "baseline_external_files.txt").write_text(
            "outside.txt\n" if dirty else "", encoding="utf-8"
        )
        return artifact

    def run(
        self, command: str, task_id: str = TASK_ID
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/evidence_scope.py", command, task_id],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )


class EvidenceScopeV2Tests(unittest.TestCase):
    def fixture(self) -> ScopeFixture:
        fixture = ScopeFixture()
        self.addCleanup(fixture.cleanup)
        return fixture

    def test_clean_dirty_untracked_non_ascii_and_delete_without_git_write_permission(
        self,
    ) -> None:
        fixture = self.fixture()
        fixture.write("work/allowed.txt", "dirty baseline\n")
        fixture.write("work/existing-untracked.txt", "dirty untracked\n")
        fixture.metadata(dirty=True)
        captured = fixture.run("capture")
        self.assertEqual(captured.returncode, 0, captured.stderr)

        git_mode = (fixture.root / ".git").stat().st_mode
        (fixture.root / ".git").chmod(0o555)
        try:
            fixture.write("work/allowed.txt", "task final\n")
            fixture.write("work/new.txt", "new\n")
            fixture.write("work/中文.txt", "中文任务\n")
            (fixture.root / "work/delete.txt").unlink()
            finalized = fixture.run("finalize")
        finally:
            (fixture.root / ".git").chmod(stat.S_IMODE(git_mode))
        self.assertEqual(finalized.returncode, 0, finalized.stderr)
        patch = (fixture.artifact / "git/diff.patch").read_text(encoding="utf-8")
        self.assertIn("work/new.txt", patch)
        self.assertIn("work/delete.txt", patch)
        self.assertIn("task final", patch)
        self.assertNotIn("outside.txt", patch)

    def test_capture_and_finalize_never_refresh_the_real_git_index(self) -> None:
        fixture = self.fixture()
        fixture.metadata(dirty=False)
        tracked = fixture.root / "work/allowed.txt"
        current = tracked.stat()
        os.utime(tracked, ns=(current.st_atime_ns, current.st_mtime_ns + 1_000_000_000))
        index = fixture.root / ".git/index"

        def snapshot() -> tuple[bytes, int, int, int]:
            info = index.lstat()
            return (index.read_bytes(), info.st_ino, info.st_size, info.st_mtime_ns)

        before_capture = snapshot()
        captured = fixture.run("capture")
        self.assertEqual(captured.returncode, 0, captured.stderr)
        self.assertEqual(snapshot(), before_capture)

        current = tracked.stat()
        os.utime(tracked, ns=(current.st_atime_ns, current.st_mtime_ns + 1_000_000_000))
        before_finalize = snapshot()
        finalized = fixture.run("finalize")
        self.assertEqual(finalized.returncode, 0, finalized.stderr)
        self.assertEqual(snapshot(), before_finalize)

    def test_temporary_workspace_is_0700_random_and_rejects_symlink_base(self) -> None:
        fixture = self.fixture()
        fixture.metadata(dirty=False)
        spec = importlib.util.spec_from_file_location(
            "scope_v2", fixture.root / "scripts/evidence_scope.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        prefix = (
            "fpms-evidence-index-"
            + hashlib.sha256(str(fixture.root.resolve()).encode()).hexdigest()[:16]
            + "-"
        )
        with module.temporary_index(fixture.root) as (_index, _env):
            owned = list(Path(tempfile.gettempdir()).glob(prefix + "*"))
            self.assertTrue(owned)
            self.assertEqual(stat.S_IMODE(owned[-1].stat().st_mode), 0o700)

        symlink = Path(tempfile.gettempdir()) / f"{prefix}symlink"
        target = fixture.root / "foreign"
        target.mkdir()
        symlink.symlink_to(target, target_is_directory=True)
        self.addCleanup(symlink.unlink, missing_ok=True)
        with mock.patch.object(module.tempfile, "mkdtemp", return_value=str(symlink)):
            with self.assertRaises(module.EvidenceError):
                with module.temporary_index(fixture.root):
                    pass

    def test_failure_and_handleable_signal_cleanup_only_owned_workspace(self) -> None:
        fixture = self.fixture()
        fixture.metadata(dirty=False)
        prefix = (
            "fpms-evidence-index-"
            + hashlib.sha256(str(fixture.root.resolve()).encode()).hexdigest()[:16]
            + "-"
        )
        before = set(Path(tempfile.gettempdir()).glob(prefix + "*"))
        script = (
            "import importlib.util,os,pathlib,signal,sys;"
            "p=pathlib.Path(sys.argv[1]);r=pathlib.Path(sys.argv[2]);"
            "s=importlib.util.spec_from_file_location('scope_signal',p);"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            "\ntry:\n"
            "  with m.temporary_index(r): os.kill(os.getpid(),signal.SIGTERM)\n"
            "except m.EvidenceSignal:\n  raise SystemExit(7)\n"
        )
        signaled = subprocess.run(
            [
                sys.executable,
                "-c",
                script,
                str(fixture.root / "scripts/evidence_scope.py"),
                str(fixture.root),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(signaled.returncode, 7, signaled.stderr.decode())
        after = set(Path(tempfile.gettempdir()).glob(prefix + "*"))
        self.assertEqual(after, before)

    def test_setup_git_failure_removes_the_owned_temporary_workspace(self) -> None:
        fixture = self.fixture()
        fixture.metadata(dirty=False)
        spec = importlib.util.spec_from_file_location(
            "scope_setup_failure", fixture.root / "scripts/evidence_scope.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        prefix = (
            "fpms-evidence-index-"
            + hashlib.sha256(str(fixture.root.resolve()).encode()).hexdigest()[:16]
            + "-"
        )
        before = set(Path(tempfile.gettempdir()).glob(prefix + "*"))
        with mock.patch.object(
            module,
            "git",
            side_effect=module.EvidenceError("forced git setup failure"),
        ):
            with self.assertRaises(module.EvidenceError):
                with module.temporary_index(fixture.root):
                    pass
        self.assertEqual(set(Path(tempfile.gettempdir()).glob(prefix + "*")), before)

        def signal_during_setup(*_args, **_kwargs):
            os.kill(os.getpid(), signal.SIGTERM)
            raise AssertionError("signal handler must interrupt setup")

        with mock.patch.object(module, "git", side_effect=signal_during_setup):
            with self.assertRaises(module.EvidenceSignal):
                with module.temporary_index(fixture.root):
                    pass
        self.assertEqual(set(Path(tempfile.gettempdir()).glob(prefix + "*")), before)

        creation_window = Path(tempfile.gettempdir()) / f"{prefix}creation-window"

        def create_then_signal(*_args, **_kwargs) -> str:
            creation_window.mkdir(mode=0o700)
            os.kill(os.getpid(), signal.SIGTERM)
            return str(creation_window)

        with mock.patch.object(
            module.tempfile, "mkdtemp", side_effect=create_then_signal
        ):
            with self.assertRaises(module.EvidenceSignal):
                with module.temporary_index(fixture.root):
                    pass
        self.assertFalse(creation_window.exists())

    def test_two_serial_tasks_do_not_share_index_workspace(self) -> None:
        fixture = self.fixture()
        fixture.metadata(dirty=False)
        second_id = "SCOPE-V2-B"
        fixture.metadata(dirty=False, task_id=second_id)
        fixture.write("work/allowed.txt", "changed\n")
        first = fixture.run("finalize")
        second = fixture.run("finalize", second_id)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        prefix = (
            "fpms-evidence-index-"
            + hashlib.sha256(str(fixture.root.resolve()).encode()).hexdigest()[:16]
            + "-"
        )
        self.assertFalse(any(Path(tempfile.gettempdir()).glob(prefix + "*")))

    def test_new_outside_allowlist_dirty_path_fails_closed(self) -> None:
        fixture = self.fixture()
        fixture.metadata(dirty=False)
        fixture.write("work/allowed.txt", "task change\n")
        fixture.write("outside.txt", "outside changed after capture\n")
        finalized = fixture.run("finalize")
        self.assertNotEqual(finalized.returncode, 0)
        self.assertIn("outside-allowlist dirty paths changed", finalized.stderr)

    def test_concrete_file_allowlist_does_not_authorize_descendants(self) -> None:
        fixture = self.fixture()
        artifact = fixture.metadata(dirty=False)
        metadata_path = artifact / "task.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["allowlist"] = ["tasks/task.md", "work/allowed.txt"]
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        captured = fixture.run("capture")
        self.assertEqual(captured.returncode, 0, captured.stderr)

        allowed = fixture.root / "work/allowed.txt"
        allowed.unlink()
        fixture.write("work/allowed.txt/extra.txt", "outside exact file\n")
        finalized = fixture.run("finalize")
        self.assertNotEqual(finalized.returncode, 0)
        self.assertIn("outside-allowlist dirty paths changed", finalized.stderr)

    def test_allowlist_globs_are_segment_anchored_and_recursive_suffix_works(
        self,
    ) -> None:
        spec = importlib.util.spec_from_file_location("scope_globs", SCOPE)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(
            module.is_allowed(
                "artifacts/B-ONE/nested/result.json",
                ("artifacts/B-*/**",),
            )
        )
        self.assertTrue(module.is_allowed("docs/file.md", ("docs/*.md",)))
        self.assertFalse(module.is_allowed("docs/nested/file.md", ("docs/*.md",)))
        self.assertFalse(module.is_allowed("nested/file.md", ("*.md",)))

    def test_replaced_index_inode_is_preserved_and_fails_cleanup(self) -> None:
        fixture = self.fixture()
        fixture.metadata(dirty=False)
        spec = importlib.util.spec_from_file_location(
            "scope_inode", fixture.root / "scripts/evidence_scope.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        workspace: Path | None = None
        with self.assertRaises(module.EvidenceError):
            with module.temporary_index(fixture.root) as (index, env):
                module.git(fixture.root, ("read-tree", "HEAD"), env=env)
                workspace = index.parent
                replacement = workspace / "replacement"
                replacement.write_bytes(index.read_bytes())
                replacement.replace(index)
        assert workspace is not None
        self.assertTrue(workspace.is_dir())
        self.assertTrue((workspace / "index").is_file())
        shutil.rmtree(workspace)


if __name__ == "__main__":
    unittest.main()
