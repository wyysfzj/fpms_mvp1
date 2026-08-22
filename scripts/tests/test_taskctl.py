from __future__ import annotations

import copy
from contextlib import redirect_stdout
import errno
import hashlib
import importlib.machinery
import importlib.util
import json
import io
import os
from pathlib import Path
import signal
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
from typing import Callable
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
TASKCTL_PATH = ROOT / "scripts" / "taskctl"
GVR3_RED_ARGV = (
    "env",
    "PYTHONDONTWRITEBYTECODE=1",
    "python3",
    "-m",
    "unittest",
    "-v",
    "scripts.tests.test_governance_reset_adapters",
    "scripts.tests.test_governance_reset_consumers",
    "scripts.tests.test_governance_reset_activation",
)


def load_taskctl():
    loader = importlib.machinery.SourceFileLoader("fpms_taskctl", str(TASKCTL_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError("unable to load taskctl")
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


taskctl = load_taskctl()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Fault:
    def __init__(self, point: str, exception: BaseException) -> None:
        self.point = point
        self.exception = exception

    def __call__(self, point: str) -> None:
        if point == self.point:
            raise self.exception


class AtomicWriteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.target = self.root / "state.json"
        self.target.write_bytes(b"old-complete")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def assert_no_temporary(self) -> None:
        self.assertEqual(list(self.root.glob(".*.taskctl-*")), [])

    def test_short_write_and_eintr_are_retried_to_complete_bytes(self) -> None:
        real_write = os.write
        calls = 0

        def flaky_write(fd: int, data: bytes) -> int:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise InterruptedError()
            if calls == 2:
                return real_write(fd, data[:3])
            return real_write(fd, data)

        with mock.patch.object(taskctl.os, "write", side_effect=flaky_write):
            taskctl.atomic_write(self.target, b"new-complete")

        self.assertEqual(self.target.read_bytes(), b"new-complete")
        self.assert_no_temporary()

    def test_enospc_file_fsync_rename_and_dir_fsync_fail_closed(self) -> None:
        cases = (
            ("before_write", OSError(errno.ENOSPC, "full"), b"old-complete"),
            ("before_file_fsync", OSError(errno.EIO, "fsync"), b"old-complete"),
            ("before_replace", OSError(errno.EIO, "rename"), b"old-complete"),
            # Rename is durable before the directory-fsync error: bytes are new and whole.
            ("before_dir_fsync", OSError(errno.EIO, "dir fsync"), b"new-complete"),
        )
        for point, error, expected in cases:
            with self.subTest(point=point):
                self.target.write_bytes(b"old-complete")
                with self.assertRaises(OSError):
                    taskctl.atomic_write(
                        self.target, b"new-complete", fault=Fault(point, error)
                    )
                self.assertEqual(self.target.read_bytes(), expected)
                self.assert_no_temporary()

    def test_sigkill_after_replace_never_leaves_partial_json(self) -> None:
        script = (
            "import importlib.machinery,importlib.util,os,signal,sys;"
            "p=sys.argv[1];t=sys.argv[2];"
            "l=importlib.machinery.SourceFileLoader('tc_child',p);"
            "s=importlib.util.spec_from_loader(l.name,l);m=importlib.util.module_from_spec(s);"
            "sys.modules[l.name]=m;l.exec_module(m);"
            "m.atomic_write(__import__('pathlib').Path(t),b'{\"ok\":true}\\n',"
            "fault=lambda point: os.kill(os.getpid(),signal.SIGKILL) if point=='after_replace' else None)"
        )
        result = subprocess.run(
            [sys.executable, "-c", script, str(TASKCTL_PATH), str(self.target)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, -signal.SIGKILL)
        self.assertEqual(
            json.loads(self.target.read_text(encoding="utf-8")), {"ok": True}
        )
        self.assert_no_temporary()

    def test_atomic_create_never_overwrites_existing_authority(self) -> None:
        self.target.write_bytes(b"first-authority")
        with self.assertRaises(taskctl.TaskctlError):
            taskctl.atomic_create(self.target, b"replacement")
        self.assertEqual(self.target.read_bytes(), b"first-authority")

    def test_atomic_create_faults_leave_no_partial_authority(self) -> None:
        for point, installed in (
            ("before_write", False),
            ("before_file_fsync", False),
            ("before_replace", False),
            ("before_exclusive_link", False),
            ("after_exclusive_link", True),
            ("before_create_dir_fsync", True),
            ("after_create_dir_fsync", True),
        ):
            with self.subTest(point=point):
                self.target.unlink(missing_ok=True)
                with self.assertRaises(RuntimeError):
                    taskctl.atomic_create(
                        self.target,
                        b"complete-authority",
                        fault=Fault(point, RuntimeError(point)),
                    )
                self.assertEqual(self.target.exists(), installed)
                if installed:
                    self.assertEqual(self.target.read_bytes(), b"complete-authority")

    def test_atomic_create_retries_eintr_and_short_write(self) -> None:
        self.target.unlink()
        real_write = os.write
        calls = 0

        def flaky_write(fd: int, data: bytes) -> int:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise InterruptedError()
            if calls == 2:
                return real_write(fd, data[:4])
            return real_write(fd, data)

        with mock.patch.object(taskctl.os, "write", side_effect=flaky_write):
            taskctl.atomic_create(self.target, b"complete-authority")
        self.assertEqual(self.target.read_bytes(), b"complete-authority")


class EventStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.artifact = Path(self.temporary.name) / "artifacts" / "TASK"
        self.artifact.mkdir(parents=True)
        (self.artifact / "commands.jsonl").write_bytes(b"")
        (self.artifact / "results.jsonl").write_bytes(b"")
        self.store = taskctl.EventStore(self.artifact, "TASK")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_two_writers_reserve_distinct_ordinals_and_views_are_valid_jsonl(
        self,
    ) -> None:
        barrier = threading.Barrier(2)
        errors: list[BaseException] = []

        def writer(step: str) -> None:
            try:
                barrier.wait()
                self.store.run(
                    step=step,
                    argv=["python3", "-c", "pass"],
                    cwd=Path.cwd(),
                    classification="NON_SQLITE",
                    runner=lambda: {"rc": 0, "executed": True},
                )
            except BaseException as exc:  # pragma: no cover - diagnostic capture
                errors.append(exc)

        threads = [
            threading.Thread(target=writer, args=(f"step-{i}",)) for i in range(2)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])
        commands = sorted((self.artifact / "events").glob("*.command.json"))
        self.assertEqual(
            [path.stem.split(".")[0] for path in commands], ["00000001", "00000002"]
        )
        self.assertEqual(len(jsonl(self.artifact / "commands.jsonl")), 2)
        self.assertEqual(len(jsonl(self.artifact / "results.jsonl")), 2)

    def test_ordinal_reservation_crash_does_not_consume_or_duplicate_ordinal(
        self,
    ) -> None:
        crashing = taskctl.EventStore(
            self.artifact,
            "TASK",
            fault=Fault("after_ordinal_reservation", RuntimeError("crash")),
        )
        with self.assertRaises(RuntimeError):
            crashing.run(
                step="test",
                argv=["true"],
                cwd=Path.cwd(),
                classification="NON_SQLITE",
                runner=lambda: {"rc": 0},
            )
        self.store.run(
            step="test",
            argv=["true"],
            cwd=Path.cwd(),
            classification="NON_SQLITE",
            runner=lambda: {"rc": 0},
        )
        self.assertTrue((self.artifact / "events/00000001.command.json").is_file())

    def test_opaque_post_effect_pre_result_becomes_outcome_unknown_without_replay(
        self,
    ) -> None:
        marker = self.artifact / "effect"
        calls = 0

        def opaque() -> dict[str, object]:
            nonlocal calls
            calls += 1
            marker.write_text("done", encoding="utf-8")
            raise taskctl.PostEffectCrash("lost result")

        with self.assertRaises(taskctl.PostEffectCrash):
            self.store.run(
                step="test",
                argv=["opaque"],
                cwd=Path.cwd(),
                classification="NON_SQLITE",
                runner=opaque,
            )
        with self.assertRaisesRegex(taskctl.TaskctlError, "OUTCOME_UNKNOWN"):
            self.store.run(
                step="test",
                argv=["opaque"],
                cwd=Path.cwd(),
                classification="NON_SQLITE",
                runner=opaque,
            )
        self.assertEqual(calls, 1)
        self.assertEqual(marker.read_text(encoding="utf-8"), "done")

    def test_replay_safe_effect_verifier_installs_or_reexecutes_result(self) -> None:
        for effect_state, expected_calls in ((True, 0), (False, 1)):
            with self.subTest(effect_state=effect_state):
                artifact = self.artifact.parent / f"TASK-{effect_state}"
                artifact.mkdir()
                (artifact / "commands.jsonl").write_bytes(b"")
                (artifact / "results.jsonl").write_bytes(b"")
                store = taskctl.EventStore(artifact, artifact.name)
                calls = 0

                def first() -> dict[str, object]:
                    raise taskctl.PostEffectCrash("lost")

                with self.assertRaises(taskctl.PostEffectCrash):
                    store.run(
                        step="scope",
                        argv=["internal"],
                        cwd=Path.cwd(),
                        classification="INTERNAL",
                        runner=first,
                        replay_safe=True,
                    )

                def replay() -> dict[str, object]:
                    nonlocal calls
                    calls += 1
                    return {"rc": 0, "executed": True}

                result = store.run(
                    step="scope",
                    argv=["internal"],
                    cwd=Path.cwd(),
                    classification="INTERNAL",
                    runner=replay,
                    replay_safe=True,
                    effect_verifier=lambda: effect_state,
                )
                self.assertEqual(result["rc"], 0)
                self.assertEqual(calls, expected_calls)

    def test_unknown_replay_safe_effect_remains_blocked(self) -> None:
        with self.assertRaises(taskctl.PostEffectCrash):
            self.store.run(
                step="scope",
                argv=["internal"],
                cwd=Path.cwd(),
                classification="INTERNAL",
                runner=lambda: (_ for _ in ()).throw(taskctl.PostEffectCrash()),
                replay_safe=True,
            )
        with self.assertRaisesRegex(taskctl.TaskctlError, "OUTCOME_UNKNOWN"):
            self.store.run(
                step="scope",
                argv=["internal"],
                cwd=Path.cwd(),
                classification="INTERNAL",
                runner=lambda: {"rc": 0},
                replay_safe=True,
                effect_verifier=lambda: None,
            )

    def test_failed_replay_safe_result_recovers_or_retries_by_effect_state(
        self,
    ) -> None:
        for effect_present, expected_retry_calls in ((True, 0), (False, 1)):
            with self.subTest(effect_present=effect_present):
                artifact = self.artifact.parent / f"FAILED-{effect_present}"
                artifact.mkdir()
                (artifact / "commands.jsonl").write_bytes(b"")
                (artifact / "results.jsonl").write_bytes(b"")
                store = taskctl.EventStore(artifact, artifact.name)
                marker = artifact / "effect"

                def first() -> dict[str, object]:
                    if effect_present:
                        marker.write_text("done", encoding="utf-8")
                    raise OSError(errno.ENOSPC, "full")

                failed = store.run(
                    step="internal",
                    argv=["internal"],
                    cwd=Path.cwd(),
                    classification="INTERNAL",
                    runner=first,
                    replay_safe=True,
                    effect_verifier=marker.exists,
                    reuse_completed=True,
                    retry_failed=True,
                    verify_completed_effect=True,
                )
                self.assertNotEqual(failed["rc"], 0)
                retry_calls = 0

                def retry() -> dict[str, object]:
                    nonlocal retry_calls
                    retry_calls += 1
                    marker.write_text("done", encoding="utf-8")
                    return {"rc": 0, "executed": True}

                recovered = store.run(
                    step="internal",
                    argv=["internal"],
                    cwd=Path.cwd(),
                    classification="INTERNAL",
                    runner=retry,
                    replay_safe=True,
                    effect_verifier=marker.exists,
                    reuse_completed=True,
                    retry_failed=True,
                    verify_completed_effect=True,
                )
                self.assertEqual(recovered["rc"], 0)
                self.assertEqual(retry_calls, expected_retry_calls)
                self.assertEqual(len(store._ordinals("command")), 2)
                self.assertIsNone(store.first_incomplete())

    def test_legacy_prefix_is_byte_identical_after_v2_projection(self) -> None:
        command_prefix = b"legacy command without json newline\n"
        result_prefix = b'{"legacy":true}\n'
        (self.artifact / "commands.jsonl").write_bytes(command_prefix)
        (self.artifact / "results.jsonl").write_bytes(result_prefix)
        self.store.adopt_legacy_views()
        self.store.run(
            step="lint",
            argv=["ruff", "check"],
            cwd=Path.cwd(),
            classification="NON_SQLITE",
            runner=lambda: {"rc": 0},
        )
        self.assertTrue(
            (self.artifact / "commands.jsonl").read_bytes().startswith(command_prefix)
        )
        self.assertTrue(
            (self.artifact / "results.jsonl").read_bytes().startswith(result_prefix)
        )
        legacy = read_json(self.artifact / "legacy-prefix.json")
        self.assertEqual(
            legacy["commands_sha256"], hashlib.sha256(command_prefix).hexdigest()
        )
        self.assertEqual(
            legacy["results_sha256"], hashlib.sha256(result_prefix).hexdigest()
        )

    def test_legacy_prefix_adoption_validates_before_persisting_metadata(self) -> None:
        (self.artifact / "commands.jsonl").write_bytes(b"legacy-command\n")
        (self.artifact / "results.jsonl").write_bytes(b"legacy-result\n")
        with self.assertRaisesRegex(taskctl.TaskctlError, "prefix authority"):
            self.store.adopt_legacy_views({})
        self.assertFalse((self.artifact / "legacy-prefix.json").exists())

        with self.assertRaisesRegex(taskctl.TaskctlError, "does not match"):
            self.store.adopt_legacy_views(
                {"command": b"wrong", "result": b"legacy-result\n"}
            )
        self.assertFalse((self.artifact / "legacy-prefix.json").exists())

    def test_view_replace_failure_keeps_old_complete_view_and_can_rebuild(self) -> None:
        self.store.run(
            step="first",
            argv=["true", "first"],
            cwd=Path.cwd(),
            classification="NON_SQLITE",
            runner=lambda: {"rc": 0},
        )
        old_view = (self.artifact / "commands.jsonl").read_bytes()
        failing = taskctl.EventStore(
            self.artifact,
            "TASK",
            fault=Fault(
                "before_replace_command_view", RuntimeError("view replace failed")
            ),
        )
        with self.assertRaises(RuntimeError):
            failing.run(
                step="second",
                argv=["true", "second"],
                cwd=Path.cwd(),
                classification="NON_SQLITE",
                runner=lambda: {"rc": 0},
            )
        self.assertEqual((self.artifact / "commands.jsonl").read_bytes(), old_view)
        self.store.rebuild_views()
        self.assertEqual(len(jsonl(self.artifact / "commands.jsonl")), 2)

    def test_global_incomplete_blocks_every_different_request(self) -> None:
        with self.assertRaises(taskctl.PostEffectCrash):
            self.store.run(
                step="opaque",
                argv=["opaque"],
                cwd=Path.cwd(),
                classification="NON_SQLITE",
                runner=lambda: (_ for _ in ()).throw(taskctl.PostEffectCrash()),
            )
        with self.assertRaisesRegex(taskctl.TaskctlError, "OUTCOME_UNKNOWN"):
            self.store.run(
                step="later",
                argv=["later"],
                cwd=Path.cwd(),
                classification="NON_SQLITE",
                runner=lambda: {"rc": 0},
            )
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )

    def test_old_completed_request_cannot_bypass_later_incomplete(self) -> None:
        request = {
            "step": "old",
            "argv": ["old"],
            "cwd": Path.cwd(),
            "classification": "INTERNAL",
            "runner": lambda: {"rc": 0, "executed": True},
            "replay_safe": True,
            "effect_verifier": lambda: True,
            "reuse_completed": True,
        }
        self.store.run(**request)
        with self.assertRaises(taskctl.PostEffectCrash):
            self.store.run(
                step="opaque",
                argv=["opaque"],
                cwd=Path.cwd(),
                classification="NON_SQLITE",
                runner=lambda: (_ for _ in ()).throw(taskctl.PostEffectCrash()),
            )
        with self.assertRaisesRegex(taskctl.TaskctlError, "OUTCOME_UNKNOWN"):
            self.store.run(**request)

    def test_event_digest_and_result_pair_tampering_fail_closed(self) -> None:
        self.store.run(
            step="lint",
            argv=["ruff", "check"],
            cwd=Path.cwd(),
            classification="NON_SQLITE",
            runner=lambda: {"rc": 0, "executed": True},
        )
        command_path = self.artifact / "events/00000001.command.json"
        command = read_json(command_path)
        command["argv"] = ["changed"]
        command_path.write_text(json.dumps(command), encoding="utf-8")
        with self.assertRaisesRegex(taskctl.TaskctlError, "digest mismatch"):
            self.store.first_incomplete()
        with self.assertRaisesRegex(taskctl.TaskctlError, "digest mismatch"):
            self.store.latest_result("lint")

        command["argv"] = ["ruff", "check"]
        request = {
            key: command[key]
            for key in (
                "task_id",
                "step",
                "argv",
                "cwd",
                "classification",
                "replay_safe",
            )
        }
        command["request_digest"] = taskctl._canonical_digest(request)
        command_path.write_text(json.dumps(command), encoding="utf-8")
        result_path = self.artifact / "events/00000001.result.json"
        result = read_json(result_path)
        result["step"] = "different"
        result_path.write_text(json.dumps(result), encoding="utf-8")
        with self.assertRaisesRegex(taskctl.TaskctlError, "mismatch"):
            self.store.first_incomplete()

    def test_event_filename_alias_and_symlink_are_rejected(self) -> None:
        self.store.run(
            step="lint",
            argv=["ruff", "check"],
            cwd=Path.cwd(),
            classification="NON_SQLITE",
            runner=lambda: {"rc": 0, "executed": True},
        )
        canonical = self.artifact / "events/00000001.command.json"
        alias = self.artifact / "events/1.command.json"
        alias.write_bytes(canonical.read_bytes())
        with self.assertRaisesRegex(taskctl.TaskctlError, "filename"):
            self.store._ordinals("command")
        alias.unlink()
        symlink = self.artifact / "events/00000002.command.json"
        symlink.symlink_to(canonical.name)
        with self.assertRaisesRegex(taskctl.TaskctlError, "regular|symlink"):
            self.store._ordinals("command")

    def test_events_root_symlink_cannot_escape_task_artifact(self) -> None:
        external = self.artifact.parent / "external-events"
        external.mkdir()
        self.store.events.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(taskctl.TaskctlError, "events.*directory|symlink"):
            self.store.run(
                step="test",
                argv=["internal"],
                cwd=Path.cwd(),
                classification="INTERNAL",
                runner=lambda: {"rc": 0},
            )
        self.assertEqual(list(external.iterdir()), [])

    def test_boolean_event_ordinals_are_rejected(self) -> None:
        self.store.run(
            step="lint",
            argv=["ruff", "check"],
            cwd=Path.cwd(),
            classification="NON_SQLITE",
            runner=lambda: {"rc": 0, "executed": True},
        )
        command_path = self.artifact / "events/00000001.command.json"
        command = read_json(command_path)
        command["ordinal"] = True
        command_path.write_text(json.dumps(command), encoding="utf-8")
        with self.assertRaisesRegex(taskctl.TaskctlError, "identity"):
            self.store.first_incomplete()

        command["ordinal"] = 1
        command_path.write_text(json.dumps(command), encoding="utf-8")
        result_path = self.artifact / "events/00000001.result.json"
        result = read_json(result_path)
        result["ordinal"] = True
        result_path.write_text(json.dumps(result), encoding="utf-8")
        with self.assertRaisesRegex(taskctl.TaskctlError, "identity"):
            self.store.first_incomplete()

    def test_middle_event_pair_deletion_is_an_invalid_append_only_gap(self) -> None:
        for index in range(3):
            self.store.run(
                step=f"step-{index}",
                argv=["internal", str(index)],
                cwd=Path.cwd(),
                classification="NON_SQLITE",
                runner=lambda: {"rc": 0},
            )
        (self.artifact / "events/00000002.command.json").unlink()
        (self.artifact / "events/00000002.result.json").unlink()
        with self.assertRaisesRegex(taskctl.TaskctlError, "gap|sequence"):
            self.store.first_incomplete()

    def test_boolean_runner_rc_is_rejected_before_result_authority(self) -> None:
        for value in (False, True):
            with self.subTest(value=value):
                artifact = self.artifact.parent / f"BOOLEAN-RUNNER-{value}"
                artifact.mkdir()
                (artifact / "commands.jsonl").write_bytes(b"")
                (artifact / "results.jsonl").write_bytes(b"")
                store = taskctl.EventStore(artifact, artifact.name)
                with self.assertRaisesRegex(taskctl.TaskctlError, "integer"):
                    store.run(
                        step="test",
                        argv=["internal"],
                        cwd=Path.cwd(),
                        classification="INTERNAL",
                        runner=lambda value=value: {"rc": value, "executed": True},
                    )
                self.assertTrue((artifact / "events/00000001.command.json").is_file())
                self.assertFalse((artifact / "events/00000001.result.json").exists())

    def test_runner_cannot_override_reserved_result_authority_fields(self) -> None:
        reserved = {
            "schema_version": 99,
            "task_id": "OTHER",
            "ordinal": True,
            "step": "other",
            "completed_ns": 0,
        }
        for field, value in reserved.items():
            with self.subTest(field=field):
                artifact = self.artifact.parent / f"RESERVED-{field}"
                artifact.mkdir()
                (artifact / "commands.jsonl").write_bytes(b"")
                (artifact / "results.jsonl").write_bytes(b"")
                store = taskctl.EventStore(artifact, artifact.name)
                with self.assertRaisesRegex(taskctl.TaskctlError, "reserved"):
                    store.run(
                        step="test",
                        argv=["internal"],
                        cwd=Path.cwd(),
                        classification="INTERNAL",
                        runner=lambda field=field, value=value: {
                            "rc": 0,
                            field: value,
                        },
                    )
                self.assertFalse((artifact / "events/00000001.result.json").exists())

    def test_boolean_result_event_is_rejected_as_invalid_authority(self) -> None:
        with self.assertRaises(taskctl.PostEffectCrash):
            self.store.run(
                step="test",
                argv=["internal"],
                cwd=Path.cwd(),
                classification="INTERNAL",
                runner=lambda: (_ for _ in ()).throw(taskctl.PostEffectCrash()),
            )
        result_path = self.artifact / "events/00000001.result.json"
        result_path.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "task_id": "TASK",
                    "ordinal": 1,
                    "step": "test",
                    "rc": False,
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "result event schema"):
            self.store.first_incomplete()

    def test_command_and_result_install_faults_recover_without_partial_events(
        self,
    ) -> None:
        command_fault = taskctl.EventStore(
            self.artifact,
            "TASK",
            fault=Fault(
                "before_file_fsync_command_event", RuntimeError("command fsync")
            ),
        )
        with self.assertRaisesRegex(RuntimeError, "command fsync"):
            command_fault.run(
                step="scope",
                argv=["internal"],
                cwd=Path.cwd(),
                classification="INTERNAL",
                runner=lambda: {"rc": 0},
                replay_safe=True,
                effect_verifier=lambda: False,
            )
        self.assertFalse((self.artifact / "events/00000001.command.json").exists())

        result_fault = taskctl.EventStore(
            self.artifact,
            "TASK",
            fault=Fault("before_file_fsync_result_event", RuntimeError("result fsync")),
        )
        with self.assertRaisesRegex(RuntimeError, "result fsync"):
            result_fault.run(
                step="scope",
                argv=["internal"],
                cwd=Path.cwd(),
                classification="INTERNAL",
                runner=lambda: {"rc": 0, "executed": True},
                replay_safe=True,
                effect_verifier=lambda: False,
            )
        self.assertTrue((self.artifact / "events/00000001.command.json").is_file())
        self.assertFalse((self.artifact / "events/00000001.result.json").exists())
        recovered = self.store.run(
            step="scope",
            argv=["internal"],
            cwd=Path.cwd(),
            classification="INTERNAL",
            runner=lambda: {"rc": 0, "executed": True},
            replay_safe=True,
            effect_verifier=lambda: False,
        )
        self.assertEqual(recovered["ordinal"], 1)

    def test_event_authority_install_fault_matrix_has_only_absent_or_complete_json(
        self,
    ) -> None:
        cases = (
            ("before_write", False),
            ("before_file_fsync", False),
            ("before_replace", False),
            ("before_dir_fsync", False),
            ("before_exclusive_link", False),
            ("after_exclusive_link", True),
            ("before_create_dir_fsync", True),
            ("after_create_dir_fsync", True),
        )
        for kind in ("command", "result"):
            for point, installed in cases:
                with self.subTest(kind=kind, point=point):
                    artifact = self.artifact.parent / f"FAULT-{kind}-{point}"
                    artifact.mkdir()
                    (artifact / "commands.jsonl").write_bytes(b"")
                    (artifact / "results.jsonl").write_bytes(b"")
                    store = taskctl.EventStore(artifact, "TASK")
                    if kind == "result":
                        with self.assertRaises(taskctl.PostEffectCrash):
                            store.run(
                                step="scope",
                                argv=["internal"],
                                cwd=Path.cwd(),
                                classification="INTERNAL",
                                runner=lambda: (_ for _ in ()).throw(
                                    taskctl.PostEffectCrash()
                                ),
                                replay_safe=True,
                            )
                    failing = taskctl.EventStore(
                        artifact,
                        "TASK",
                        fault=Fault(
                            f"{point}_{kind}_event",
                            OSError(errno.ENOSPC, point),
                        ),
                    )
                    with self.assertRaises(OSError):
                        failing.run(
                            step="scope",
                            argv=["internal"],
                            cwd=Path.cwd(),
                            classification="INTERNAL",
                            runner=lambda: {"rc": 0, "executed": True},
                            replay_safe=True,
                            effect_verifier=lambda: False,
                            reuse_completed=True,
                        )
                    authority = artifact / f"events/00000001.{kind}.json"
                    self.assertEqual(authority.exists(), installed)
                    if authority.exists():
                        self.assertEqual(read_json(authority)["ordinal"], 1)

    def test_sigkill_after_event_authority_link_recovers_same_ordinal(self) -> None:
        child = (
            "import importlib.machinery,importlib.util,os,pathlib,signal,sys;"
            "loader=importlib.machinery.SourceFileLoader('tc_child',sys.argv[1]);"
            "spec=importlib.util.spec_from_loader(loader.name,loader);"
            "module=importlib.util.module_from_spec(spec);"
            "sys.modules[loader.name]=module;loader.exec_module(module);"
            "artifact=pathlib.Path(sys.argv[2]);marker=pathlib.Path(sys.argv[3]);"
            "fault_point=sys.argv[4];"
            "store=module.EventStore(artifact,'TASK',"
            "fault=lambda point: os.kill(os.getpid(),signal.SIGKILL) "
            "if point==fault_point else None);"
            "effect=lambda: (lambda fd: (os.write(fd,b'x'),os.fsync(fd),os.close(fd),"
            "{'rc':0,'executed':True})[-1])"
            "(os.open(marker,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600));"
            "store.run(step='scope',argv=['internal'],cwd=pathlib.Path.cwd(),"
            "classification='INTERNAL',runner=effect,replay_safe=True,"
            "effect_verifier=lambda:False,reuse_completed=True)"
        )
        for kind in ("command", "result"):
            with self.subTest(kind=kind):
                artifact = self.artifact.parent / f"SIGKILL-{kind}"
                artifact.mkdir()
                (artifact / "commands.jsonl").write_bytes(b"")
                (artifact / "results.jsonl").write_bytes(b"")
                marker = artifact / "effect"
                fault_point = f"after_exclusive_link_{kind}_event"
                crashed = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        child,
                        str(TASKCTL_PATH),
                        str(artifact),
                        str(marker),
                        fault_point,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(crashed.returncode, -signal.SIGKILL)
                command_path = artifact / "events/00000001.command.json"
                result_path = artifact / "events/00000001.result.json"
                self.assertEqual(read_json(command_path)["ordinal"], 1)
                self.assertEqual(result_path.exists(), kind == "result")
                if result_path.exists():
                    self.assertEqual(read_json(result_path)["ordinal"], 1)

                calls = marker.read_bytes().count(b"x") if marker.exists() else 0

                def effect() -> dict[str, object]:
                    nonlocal calls
                    calls += 1
                    marker.write_bytes(b"x" * calls)
                    return {"rc": 0, "executed": True}

                recovered = taskctl.EventStore(artifact, "TASK").run(
                    step="scope",
                    argv=["internal"],
                    cwd=Path.cwd(),
                    classification="INTERNAL",
                    runner=effect,
                    replay_safe=True,
                    effect_verifier=lambda: False,
                    reuse_completed=True,
                )
                self.assertEqual(recovered["ordinal"], 1)
                self.assertEqual(calls, 1)
                self.assertEqual(
                    len(list((artifact / "events").glob("*.command.json"))), 1
                )
                self.assertEqual(
                    len(list((artifact / "events").glob("*.result.json"))), 1
                )
                self.assertEqual(len(jsonl(artifact / "commands.jsonl")), 1)
                self.assertEqual(len(jsonl(artifact / "results.jsonl")), 1)
                self.assertEqual(
                    [
                        path
                        for path in (artifact / "events").iterdir()
                        if taskctl._is_atomic_temporary(path)
                    ],
                    [],
                )


class StateCasTests(unittest.TestCase):
    def test_two_state_writers_cannot_commit_the_same_expected_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            artifact = repo / "artifacts/TASK"
            artifact.mkdir(parents=True)
            state_path = artifact / "state.json"
            state_path.write_text('{"version":0}\n', encoding="utf-8")
            expected = hashlib.sha256(state_path.read_bytes()).hexdigest()
            barrier = threading.Barrier(2)
            outcomes: list[str] = []

            def write(version: int) -> None:
                controller = taskctl.TaskController(
                    repo, "TASK", actor=f"writer-{version}", implementer="impl"
                )
                barrier.wait()
                try:
                    controller._cas_write_state({"version": version}, expected)
                except taskctl.TaskctlError:
                    outcomes.append("rejected")
                else:
                    outcomes.append("written")

            threads = [
                threading.Thread(target=write, args=(value,)) for value in (1, 2)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(sorted(outcomes), ["rejected", "written"])
            self.assertIn(read_json(state_path)["version"], {1, 2})


class LockLeaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.lock = self.root / "sqlite.lock"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_contention_is_immediate_and_sidecar_is_not_authority(self) -> None:
        first = taskctl.LockLease(self.lock, owner="first")
        first.acquire()
        try:
            with self.assertRaisesRegex(taskctl.TaskctlError, "contention"):
                taskctl.LockLease(self.lock, owner="second").acquire()
        finally:
            first.release()
        self.lock.with_suffix(".owner.json").write_text("stale", encoding="utf-8")
        second = taskctl.LockLease(self.lock, owner="second")
        second.acquire()
        second.release()

    def test_sidecar_cleanup_failure_does_not_create_false_contention(self) -> None:
        first = taskctl.LockLease(self.lock, owner="first")
        first.acquire()
        with mock.patch.object(Path, "unlink", side_effect=OSError("cleanup")):
            with self.assertRaises(taskctl.LeaseCleanupError):
                first.release()
        second = taskctl.LockLease(self.lock, owner="second")
        second.acquire()
        second.release()

    def test_sidecar_write_failure_releases_fd_and_prevents_runner(self) -> None:
        lease = taskctl.LockLease(
            self.lock,
            owner="first",
            sidecar_writer=lambda *_: (_ for _ in ()).throw(OSError("sidecar")),
        )
        with self.assertRaises(OSError):
            lease.acquire()
        next_holder = taskctl.LockLease(self.lock, owner="next")
        next_holder.acquire()
        next_holder.release()

    def test_process_sigkill_releases_kernel_lock(self) -> None:
        ready = self.root / "ready"
        script = (
            "import importlib.machinery,importlib.util,pathlib,sys,time;"
            "l=importlib.machinery.SourceFileLoader('tc_lock',sys.argv[1]);"
            "s=importlib.util.spec_from_loader(l.name,l);m=importlib.util.module_from_spec(s);"
            "sys.modules[l.name]=m;l.exec_module(m);"
            "x=m.LockLease(pathlib.Path(sys.argv[2]),owner='child');x.acquire();"
            "pathlib.Path(sys.argv[3]).write_text('ready');time.sleep(60)"
        )
        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                script,
                str(TASKCTL_PATH),
                str(self.lock),
                str(ready),
            ]
        )
        try:
            for _ in range(100):
                if ready.exists():
                    break
                child.poll()
                threading.Event().wait(0.02)
            self.assertTrue(ready.exists())
            child.kill()
            child.wait(timeout=5)
            holder = taskctl.LockLease(self.lock, owner="parent")
            holder.acquire()
            holder.release()
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)


class BackendLeaseIntegrationTests(unittest.TestCase):
    def fixture(self, script: str | None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repo = Path(temporary.name)
        artifact = repo / "artifacts/TASK"
        (artifact / "outputs").mkdir(parents=True)
        (artifact / "events").mkdir()
        (artifact / "commands.jsonl").write_bytes(b"")
        (artifact / "results.jsonl").write_bytes(b"")
        task_file = repo / "tasks/TASK.md"
        task_file.parent.mkdir(parents=True)
        task_file.write_text(
            "# TASK\n\nStatus: READY\nRisk-Tier: MEDIUM\n"
            'Closure-Tags: ["sqlite"]\nTask-Path: tasks/TASK.md\n\n'
            "## Allowed Files\n\n- `tasks/TASK.md`\n- `backend/tests/**`\n"
            "- `artifacts/TASK/**`\n",
            encoding="utf-8",
        )
        (artifact / "baseline_allowlist.diff").write_bytes(b"")
        (artifact / "baseline_external_files.txt").write_bytes(b"")
        metadata = {
            "task_id": "TASK",
            "task_file": "tasks/TASK.md",
            "allowlist": ["tasks/TASK.md", "backend/tests/**"],
            "repo_root": str(repo.resolve()),
            "baseline_dirty": False,
            "init_ts": "20260717T000000",
        }
        (artifact / "task.json").write_text(json.dumps(metadata), encoding="utf-8")
        (artifact / "module_selection.json").write_text("{}\n", encoding="utf-8")
        (artifact / "state.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "task_id": "TASK",
                    "state": "IMPLEMENTING",
                    "controller": "lead",
                    "implementer": "implementer",
                    "task_file": "tasks/TASK.md",
                    "allowlist": ["tasks/TASK.md", "backend/tests/**"],
                    "baseline": {
                        "task_json_sha256": hashlib.sha256(
                            (artifact / "task.json").read_bytes()
                        ).hexdigest(),
                        "allowlist_sha256": hashlib.sha256(b"").hexdigest(),
                        "external_sha256": hashlib.sha256(b"").hexdigest(),
                        "init_ts": "20260717T000000",
                    },
                    "module_selection_sha256": hashlib.sha256(b"{}\n").hexdigest(),
                    "review_generation": 0,
                }
            ),
            encoding="utf-8",
        )
        pytest = repo / "backend/.venv/bin/pytest"
        if script is not None:
            pytest.parent.mkdir(parents=True)
            pytest.write_text(script, encoding="utf-8")
            pytest.chmod(pytest.stat().st_mode | stat.S_IXUSR)
        controller = taskctl.TaskController(
            repo, "TASK", actor="lead", implementer="implementer"
        )
        return controller

    def test_pytest_failure_and_missing_executable_release_fd(self) -> None:
        failed = self.fixture("#!/bin/sh\nexit 4\n")
        result = failed.backend_test("test", ["tests/test_one.py"])
        self.assertEqual(result["rc"], 4)
        holder = taskctl.LockLease(failed._sqlite_lock(), owner="after-failure")
        holder.acquire()
        holder.release()

        missing = self.fixture(None)
        result = missing.backend_test("test", ["tests/test_one.py"])
        self.assertEqual(result["rc"], 127)
        self.assertIs(result["executed"], False)
        holder = taskctl.LockLease(missing._sqlite_lock(), owner="after-missing")
        holder.acquire()
        holder.release()

    def test_signal_termination_is_not_a_valid_red_and_releases_fd(self) -> None:
        controller = self.fixture("#!/bin/sh\nkill -TERM $$\n")
        result = controller.backend_test("red", ["tests/test_one.py"])
        self.assertEqual(result["rc"], -signal.SIGTERM)
        self.assertIs(result["expectation_met"], False)
        holder = taskctl.LockLease(controller._sqlite_lock(), owner="after-signal")
        holder.acquire()
        holder.release()

    def test_red_accepts_only_pytest_assertion_failure_exit_one(self) -> None:
        assertion_failure = self.fixture("#!/bin/sh\nexit 1\n")
        accepted = assertion_failure.backend_test("red", ["tests/test_one.py"])
        self.assertEqual(accepted["rc"], 1)
        self.assertIs(accepted["expectation_met"], True)

        for rc in (4, 5):
            with self.subTest(rc=rc):
                infrastructure = self.fixture(f"#!/bin/sh\nexit {rc}\n")
                rejected = infrastructure.backend_test("red", ["tests/test_one.py"])
                self.assertEqual(rejected["rc"], rc)
                self.assertIs(rejected["expectation_met"], False)

    def test_sidecar_cleanup_failure_is_a_distinct_nonzero_backend_result(self) -> None:
        controller = self.fixture("#!/bin/sh\nexit 0\n")
        base = taskctl.LockLease

        class CleanupFailLease(base):
            def release(self) -> None:
                sqlite = self.path.name == "sqlite.lock" and self.descriptor is not None
                super().release()
                if sqlite:
                    raise taskctl.LeaseCleanupError("forced cleanup failure")

        with mock.patch.object(taskctl, "LockLease", CleanupFailLease):
            result = controller.backend_test("test", ["tests/test_one.py"])
        self.assertEqual(result["rc"], 125)
        self.assertIs(result["executed"], True)
        self.assertEqual(result["reason"], "sidecar_cleanup_failed")
        holder = taskctl.LockLease(controller._sqlite_lock(), owner="after-cleanup")
        holder.acquire()
        holder.release()

    def test_public_red_rejects_infrastructure_failure_after_pytest(self) -> None:
        fake = mock.Mock()
        fake.backend_test.return_value = {
            "rc": 125,
            "executed": True,
            "reason": "sidecar_cleanup_failed",
        }
        with (
            mock.patch.object(taskctl, "repository_root", return_value=Path.cwd()),
            mock.patch.object(taskctl, "TaskController", return_value=fake),
            redirect_stdout(io.StringIO()),
        ):
            rc = taskctl.main(["TASK", "backend-test", "red", "--", "tests/test.py"])
        self.assertEqual(rc, 1)

        fake.backend_test.return_value = {
            "rc": 1,
            "executed": True,
            "expectation_met": True,
        }
        with (
            mock.patch.object(taskctl, "repository_root", return_value=Path.cwd()),
            mock.patch.object(taskctl, "TaskController", return_value=fake),
            redirect_stdout(io.StringIO()),
        ):
            rc = taskctl.main(["TASK", "backend-test", "red", "--", "tests/test.py"])
        self.assertEqual(rc, 0)


class MainDispatchTests(unittest.TestCase):
    def test_public_main_dispatches_all_controller_actions_with_exact_arguments(
        self,
    ) -> None:
        root = Path("/tmp/fpms-taskctl-main-dispatch").resolve()
        cases = (
            (
                [
                    "TASK",
                    "prepare-review",
                    "--kernel",
                    "candidate/AGENTS.md",
                    "--manifest",
                    "candidate/manifest.json",
                ],
                "prepare_review",
                (),
                {
                    "kernel": root / "candidate/AGENTS.md",
                    "manifest": root / "candidate/manifest.json",
                },
            ),
            (
                ["TASK", "review", "lease", "governance", "--reviewer", "reviewer-1"],
                "review_lease",
                ("governance", "reviewer-1"),
                {},
            ),
            (
                [
                    "TASK",
                    "review",
                    "submit",
                    "tooling",
                    "--report",
                    "artifacts/TASK/review/tooling_axis.md",
                ],
                "review_submit",
                ("tooling", root / "artifacts/TASK/review/tooling_axis.md"),
                {},
            ),
            (
                [
                    "TASK",
                    "governance-adopt",
                    "--approval",
                    "artifacts/TASK/governance_adoption.md",
                ],
                "governance_adopt",
                (root / "artifacts/TASK/governance_adoption.md",),
                {},
            ),
            (
                [
                    "TASK",
                    "activate",
                    "--kernel",
                    "candidate/AGENTS.md",
                    "--manifest",
                    "candidate/manifest.json",
                ],
                "activate",
                (
                    root / "candidate/AGENTS.md",
                    root / "candidate/manifest.json",
                ),
                {},
            ),
            (["TASK", "close"], "close", (), {}),
        )
        for argv, method, positional, keywords in cases:
            with self.subTest(action=method):
                controller = mock.Mock()
                getattr(controller, method).return_value = {"state": "OK"}
                factory = mock.Mock(return_value=controller)
                with (
                    mock.patch.object(taskctl, "repository_root", return_value=root),
                    mock.patch.object(taskctl, "TaskController", factory),
                    mock.patch.dict(
                        os.environ,
                        {
                            "TASKCTL_ACTOR": "controller-1",
                            "TASKCTL_IMPLEMENTER": "implementer-1",
                        },
                    ),
                    redirect_stdout(io.StringIO()),
                ):
                    rc = taskctl.main(argv)
                self.assertEqual(rc, 0)
                factory.assert_called_once_with(
                    root,
                    "TASK",
                    actor="controller-1",
                    implementer="implementer-1",
                )
                getattr(controller, method).assert_called_once_with(
                    *positional, **keywords
                )


class PublicCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name).resolve()
        (self.repo / "scripts").mkdir()
        shutil.copy2(TASKCTL_PATH, self.repo / "scripts/taskctl")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        artifact = self.repo / "artifacts/TASK"
        (artifact / "outputs").mkdir(parents=True)
        (artifact / "commands.jsonl").write_bytes(b"")
        (artifact / "results.jsonl").write_bytes(b"")
        task_file = self.repo / "tasks/TASK.md"
        task_file.parent.mkdir(parents=True)
        task_file.write_text(
            "# TASK\n\nStatus: READY\nRisk-Tier: MEDIUM\n"
            'Closure-Tags: ["evidence"]\nTask-Path: tasks/TASK.md\n\n'
            "## Allowed Files\n\n- `tasks/TASK.md`\n- `observed.json`\n"
            "- `artifacts/TASK/**`\n",
            encoding="utf-8",
        )
        (artifact / "baseline_allowlist.diff").write_bytes(b"")
        (artifact / "baseline_external_files.txt").write_bytes(b"")
        metadata = {
            "task_id": "TASK",
            "task_file": "tasks/TASK.md",
            "allowlist": ["tasks/TASK.md", "observed.json"],
            "repo_root": str(self.repo.resolve()),
            "baseline_dirty": False,
            "init_ts": "20260717T000000",
        }
        (artifact / "task.json").write_text(json.dumps(metadata), encoding="utf-8")
        (artifact / "module_selection.json").write_text("{}\n", encoding="utf-8")
        (artifact / "state.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "task_id": "TASK",
                    "state": "IMPLEMENTING",
                    "controller": "lead",
                    "implementer": "implementer",
                    "task_file": "tasks/TASK.md",
                    "allowlist": ["tasks/TASK.md", "observed.json"],
                    "baseline": {
                        "task_json_sha256": hashlib.sha256(
                            (artifact / "task.json").read_bytes()
                        ).hexdigest(),
                        "allowlist_sha256": hashlib.sha256(b"").hexdigest(),
                        "external_sha256": hashlib.sha256(b"").hexdigest(),
                        "init_ts": "20260717T000000",
                    },
                    "module_selection_sha256": hashlib.sha256(b"{}\n").hexdigest(),
                    "review_generation": 0,
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(
        self,
        *args: str,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(self.repo / "scripts/taskctl"), "TASK", *args],
            cwd=cwd or self.repo,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def test_record_preserves_public_argv_boundaries_and_caller_cwd(self) -> None:
        caller = self.repo / "nested/caller"
        caller.mkdir(parents=True)
        tricky = ['quote"value', "中文 空格", ""]
        command = ["git", "rev-parse", "--sq-quote", *tricky]
        result = self.run_cli("record", "lint", "--", *command, cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout)
        event = read_json(self.repo / "artifacts/TASK/events/00000001.command.json")
        self.assertEqual(event["argv"], command)
        self.assertEqual(Path(event["cwd"]).resolve(), caller.resolve())
        recorded = read_json(self.repo / "artifacts/TASK/events/00000001.result.json")
        log = self.repo / str(recorded["log"])
        self.assertEqual(
            log.read_text(encoding="utf-8").strip(), "'quote\"value' '中文 空格' ''"
        )

    def test_record_disables_inherited_git_external_diff(self) -> None:
        tracked = self.repo / "tracked.txt"
        tracked.write_text("before\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.txt"], cwd=self.repo, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "commit",
                "-qm",
                "baseline",
            ],
            cwd=self.repo,
            check=True,
        )
        tracked.write_text("after\n", encoding="utf-8")
        inherited = os.environ.copy()
        inherited["GIT_EXTERNAL_DIFF"] = "/usr/bin/false"
        result = self.run_cli(
            "record",
            "lint",
            "--",
            "git",
            "diff",
            "--",
            "tracked.txt",
            env=inherited,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        event = read_json(self.repo / "artifacts/TASK/events/00000001.command.json")
        self.assertEqual(event["argv"], ["git", "diff", "--", "tracked.txt"])

    def test_public_unknown_command_fails_closed_without_event(self) -> None:
        commands = (
            ("bash", "-c", "pytest tests"),
            ("python3", "scripts/run_backend_suite.py"),
            ("python3", "-c", '__import__("py"+"test").main()'),
            ("npm", "run", "backend-db-tests"),
        )
        for command in commands:
            with self.subTest(command=command):
                result = self.run_cli("record", "test", "--", *command)
                self.assertNotEqual(result.returncode, 0)
                events = self.repo / "artifacts/TASK/events"
                self.assertFalse(events.exists())

    def test_public_start_rejects_bootstrap_outside_exact_gvr3_pair(self) -> None:
        ordinary = self.run_cli(
            "start",
            "--task-file",
            "tasks/TASK.md",
            "--bootstrap-kernel",
            "tasks/TASK.md",
            "--bootstrap-manifest",
            "tasks/TASK.md",
        )
        self.assertNotEqual(ordinary.returncode, 0)

        task_id = taskctl.GVR3_ID
        task_file = self.repo / f"tasks/{task_id}.md"
        task_file.write_text(
            f"# {task_id}\n\nStatus: READY / CONTRACT FROZEN\nRisk-Tier: HIGH\n"
            f'Closure-Tags: ["activation"]\nTask-Path: tasks/{task_id}.md\n\n'
            "## Allowed Files\n\n"
            f"- `tasks/{task_id}.md`\n- `AGENTS.md`\n"
            f"- `artifacts/{task_id}/**`\n",
            encoding="utf-8",
        )
        missing_pair = subprocess.run(
            [
                str(self.repo / "scripts/taskctl"),
                task_id,
                "start",
                "--task-file",
                f"tasks/{task_id}.md",
            ],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertNotEqual(missing_pair.returncode, 0)
        one_sided = subprocess.run(
            [
                str(self.repo / "scripts/taskctl"),
                task_id,
                "start",
                "--task-file",
                f"tasks/{task_id}.md",
                "--bootstrap-kernel",
                f"tasks/{task_id}.md",
            ],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertNotEqual(one_sided.returncode, 0)

    def test_doctor_public_command_is_read_only_json(self) -> None:
        before = (self.repo / "artifacts/TASK/state.json").read_bytes()
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["live_state"], "IMPLEMENTING")
        self.assertEqual((self.repo / "artifacts/TASK/state.json").read_bytes(), before)

    def test_public_doctor_reports_known_failed_ordinal(self) -> None:
        state_path = self.repo / "artifacts/TASK/state.json"
        state = read_json(state_path)
        state.update({"state": "FAIL", "failed_ordinal": 7, "resume_from": "task_gate"})
        state_path.write_text(json.dumps(state), encoding="utf-8")
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(report["first_problem_ordinal"], 7)
        self.assertEqual(report["resume_from"], "task_gate")

    def test_public_normal_start_rejects_incomplete_activation_authority(self) -> None:
        shutil.copy2(
            ROOT / "scripts/evidence_scope.py", self.repo / "scripts/evidence_scope.py"
        )
        candidate = ROOT / f"artifacts/{taskctl.GVR1_ID}/candidate"
        (self.repo / "docs/agents").mkdir(parents=True)
        (self.repo / "AGENTS.md").write_bytes((candidate / "AGENTS.md").read_bytes())
        (self.repo / "docs/agents/manifest.json").write_bytes(
            (candidate / "manifest.json").read_bytes()
        )
        for module in (ROOT / "docs/agents").glob("*.md"):
            (self.repo / "docs/agents" / module.name).write_bytes(module.read_bytes())
        activation = self.repo / f"artifacts/{taskctl.GVR3_ID}"
        activation.mkdir(parents=True)
        manifest = json.loads(
            (self.repo / "docs/agents/manifest.json").read_text(encoding="utf-8")
        )
        digest, _inputs = taskctl.governance_digest(
            self.repo, self.repo / "AGENTS.md", manifest
        )
        kernel_sha256 = hashlib.sha256(
            (self.repo / "AGENTS.md").read_bytes()
        ).hexdigest()
        manifest_sha256 = hashlib.sha256(
            (self.repo / "docs/agents/manifest.json").read_bytes()
        ).hexdigest()
        candidate_record = {
            "governance_digest": digest,
            "source_hashes": {
                "kernel_sha256": kernel_sha256,
                "manifest_sha256": manifest_sha256,
            },
        }
        candidate_record["fingerprint"] = taskctl._canonical_digest(candidate_record)
        (activation / "state.json").write_text(
            json.dumps(
                {
                    "state": "PASS",
                    "activation": {
                        "kernel_sha256": kernel_sha256,
                        "manifest_sha256": manifest_sha256,
                        "governance_digest": digest,
                    },
                    "candidate": candidate_record,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        task_file = self.repo / "tasks/repo/NORMAL.md"
        task_file.parent.mkdir(parents=True)
        task_file.write_text(
            """# NORMAL\n\nStatus: READY / CONTRACT FROZEN\nRisk-Tier: MEDIUM\nClosure-Tags: [\"api\"]\nTask-Path: tasks/repo/NORMAL.md\n\n## Allowed Files\n\n- `tasks/repo/NORMAL.md`\n- `work/allowed.txt`\n- `artifacts/NORMAL/**`\n""",
            encoding="utf-8",
        )
        (self.repo / "work").mkdir()
        (self.repo / "work/allowed.txt").write_text("baseline\n", encoding="utf-8")
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=self.repo, check=True
        )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.repo, check=True)
        command = [
            str(self.repo / "scripts/taskctl"),
            "NORMAL",
            "start",
            "--task-file",
            "tasks/repo/NORMAL.md",
        ]
        result = subprocess.run(
            command,
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stdout.lower(), r"activation|identit")
        self.assertFalse((self.repo / "artifacts/NORMAL/state.json").exists())


class ContractAndReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.task_path = self.root / "tasks/repo/TASK.md"
        self.task_path.parent.mkdir(parents=True)
        self.task_path.write_text(
            """# TASK\n\nStatus: READY / CONTRACT FROZEN\nRisk-Tier: HIGH\nClosure-Tags: [\"evidence\", \"governance\"]\nTask-Path: tasks/repo/TASK.md\n\n## Allowed Files\n\n- `tasks/repo/TASK.md`\n- `scripts/tool`\n- `artifacts/TASK/**`\n""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_task_contract_parses_allowlist_and_rejects_duplicate_or_broad_metadata(
        self,
    ) -> None:
        contract = taskctl.parse_task_contract(self.task_path, "TASK", self.root)
        self.assertEqual(contract.task_path, "tasks/repo/TASK.md")
        self.assertEqual(contract.allowlist, ("tasks/repo/TASK.md", "scripts/tool"))
        self.task_path.write_text(
            self.task_path.read_text(encoding="utf-8") + "\nRisk-Tier: HIGH\n",
            encoding="utf-8",
        )
        with self.assertRaises(taskctl.TaskctlError):
            taskctl.parse_task_contract(self.task_path, "TASK", self.root)

    def test_task_contract_rejects_ambiguous_allowlist_metacharacters(self) -> None:
        original = self.task_path.read_text(encoding="utf-8")
        for unsafe in (
            "work/report[1].txt",
            "work/report?.txt",
            "work/{report}.txt",
            "work/***.txt",
        ):
            with self.subTest(unsafe=unsafe):
                self.task_path.write_text(
                    original.replace(
                        "- `scripts/tool`\n",
                        f"- `scripts/tool`\n- `{unsafe}`\n",
                    ),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(taskctl.TaskctlError, "unsupported"):
                    taskctl.parse_task_contract(self.task_path, "TASK", self.root)

        self.task_path.write_text(
            original.replace(
                "- `scripts/tool`\n",
                "- `scripts/tool`\n- `work/*.txt`\n- `work/**`\n",
            ),
            encoding="utf-8",
        )
        contract = taskctl.parse_task_contract(self.task_path, "TASK", self.root)
        self.assertIn("work/*.txt", contract.allowlist)
        self.assertIn("work/**", contract.allowlist)

    def test_command_classifier_blocks_backend_migration_close_and_shell_hiding(
        self,
    ) -> None:
        blocked = (
            ["pytest", "tests"],
            ["alembic", "upgrade", "head"],
            ["./scripts/taskctl", "TASK", "close"],
            ["python3", "scripts/taskctl", "TASK", "close"],
            ["python3", "scripts/run_backend_suite.py"],
            ["python3", "-c", '__import__("py"+"test").main()'],
            ["npm", "run", "backend-db-tests"],
            ["node", "scripts/run-anything.js"],
            ["npx", "unknown-tool"],
            ["/tmp/git", "diff"],
            ["env", "PATH=/tmp", "git", "diff"],
            ["git", "diff", "--ext-diff"],
            ["git", "diff", "--textconv"],
            ["bash", "-c", "pytest tests"],
        )
        for argv in blocked:
            with self.subTest(argv=argv), self.assertRaises(taskctl.TaskctlError):
                taskctl.classify_record("TASK", "test", argv)
        self.assertEqual(
            taskctl.classify_record("TASK", "lint", ["ruff", "check", "scripts/tool"]),
            "NON_SQLITE",
        )
        self.assertEqual(
            taskctl.classify_record(
                "TASK",
                "scope",
                ["python3", "scripts/evidence_scope.py", "finalize", "TASK"],
            ),
            "SCOPE",
        )
        self.assertEqual(
            taskctl.classify_record(
                "TASK",
                "frozen_v1",
                [
                    "python3",
                    "scripts/frozen_v1_acceptance.py",
                    "--task-id",
                    "TASK",
                    "--frozen-root",
                    "artifacts/TASK/bootstrap/frozen-v1",
                    "--candidate-root",
                    "artifacts/TASK/candidate",
                ],
            ),
            "FROZEN_V1",
        )
        for step, argv, classification in (
            ("test", taskctl.GVR3_LEGACY_RED_ARGV, "NON_SQLITE"),
            ("shell_check", taskctl.GVR3_SHELL_CHECK_ARGV, "NON_SQLITE"),
            ("format_check", taskctl.GVR3_FORMAT_CHECK_ARGV, "NON_SQLITE"),
            ("lint", taskctl.GVR3_LINT_ARGV, "NON_SQLITE"),
            ("compile", taskctl.GVR3_COMPILE_ARGV, "NON_SQLITE"),
            ("diff_check", taskctl.GVR3_DIFF_CHECK_ARGV, "NON_SQLITE"),
        ):
            with self.subTest(gvr3_exact_step=step):
                self.assertEqual(
                    taskctl.classify_record(taskctl.GVR3_ID, step, list(argv)),
                    classification,
                )
        for step, argv in (
            ("test", ["git", "status", "--porcelain=v1"]),
            ("lint", ["ruff", "check", "scripts/taskctl"]),
            ("compile", ["bash", "-n", "scripts/evidence_run.sh"]),
            ("diff_check", ["git", "diff", "--check"]),
        ):
            with self.subTest(gvr3_step=step):
                with self.assertRaisesRegex(taskctl.TaskctlError, "exact frozen"):
                    taskctl.classify_record(taskctl.GVR3_ID, step, argv)
        with self.assertRaises(taskctl.TaskctlError):
            taskctl.classify_record(
                "TASK",
                "scope",
                ["python3", "scripts/evidence_scope.py", "finalize", "TASK", "extra"],
            )

    def test_task_contract_rejects_symlink_invocation(self) -> None:
        alias = self.root / "tasks/repo/ALIAS.md"
        alias.symlink_to(self.task_path)
        with self.assertRaisesRegex(taskctl.TaskctlError, "symlink"):
            taskctl.parse_task_contract(alias, "TASK", self.root)

        external = self.root.parent / f"{self.root.name}-external-task-alias.md"
        external.symlink_to(self.task_path)
        self.addCleanup(external.unlink, missing_ok=True)
        with self.assertRaisesRegex(taskctl.TaskctlError, "outside|symlink"):
            taskctl.parse_task_contract(external, "TASK", self.root)

    def test_task_contract_rejects_noncanonical_path_bytes(self) -> None:
        original = self.task_path.read_text(encoding="utf-8")
        for replacement in ("tasks//repo/TASK.md", "tasks/./repo/TASK.md"):
            with self.subTest(replacement=replacement):
                self.task_path.write_text(
                    original.replace("tasks/repo/TASK.md", replacement),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(taskctl.TaskctlError, "canonical"):
                    taskctl.parse_task_contract(self.task_path, "TASK", self.root)

    def test_task_contract_requires_exact_allowed_files_heading(self) -> None:
        self.task_path.write_text(
            self.task_path.read_text(encoding="utf-8").replace(
                "## Allowed Files", "## Allowed Files — draft only"
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "Allowed Files"):
            taskctl.parse_task_contract(self.task_path, "TASK", self.root)

    def test_allowed_files_stops_at_commonmark_h2_boundaries(self) -> None:
        prefix = self.task_path.read_text(encoding="utf-8").split(
            "## Allowed Files", 1
        )[0]
        for boundary in ("##\tExplicit Non-Closure", "   ## Explicit Non-Closure"):
            with self.subTest(boundary=repr(boundary)):
                self.task_path.write_text(
                    prefix
                    + "## Allowed Files\n\n- `tasks/repo/TASK.md`\n"
                    + f"{boundary}\n\n- `scripts/not-authorized.py`\n",
                    encoding="utf-8",
                )
                contract = taskctl.parse_task_contract(
                    self.task_path, "TASK", self.root
                )
                self.assertEqual(contract.allowlist, ("tasks/repo/TASK.md",))

        self.task_path.write_text(
            prefix
            + "## Allowed Files\n\n- `tasks/repo/TASK.md`\n"
            + "### Allowed helper\n\n- `scripts/tool`\n",
            encoding="utf-8",
        )
        contract = taskctl.parse_task_contract(self.task_path, "TASK", self.root)
        self.assertEqual(contract.allowlist, ("tasks/repo/TASK.md", "scripts/tool"))

    def test_task_metadata_must_precede_any_commonmark_h2(self) -> None:
        metadata = (
            "Status: READY / CONTRACT FROZEN\nRisk-Tier: HIGH\n"
            'Closure-Tags: ["evidence", "governance"]\n'
            "Task-Path: tasks/repo/TASK.md\n"
        )
        for boundary in ("##\tNotes", "   ## Notes"):
            with self.subTest(boundary=repr(boundary)):
                self.task_path.write_text(
                    f"# TASK\n\n{boundary}\n\n{metadata}\n"
                    "## Allowed Files\n\n- `tasks/repo/TASK.md`\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(taskctl.TaskctlError, "metadata"):
                    taskctl.parse_task_contract(self.task_path, "TASK", self.root)

    def test_pass_status_requires_one_exact_status_field(self) -> None:
        status = self.root / "status.md"
        status.write_text("# X\n\n<!-- Status: PASS -->\n", encoding="utf-8")
        self.assertFalse(taskctl._exact_pass_status(status, metadata_only=True))
        status.write_text("# X\n\nStatus: PASS / ACCEPTED\n", encoding="utf-8")
        self.assertTrue(taskctl._exact_pass_status(status, metadata_only=True))
        status.write_text(
            "# X\n\nStatus: PASS\n\n## Notes\nStatus: PASS\n", encoding="utf-8"
        )
        self.assertFalse(taskctl._exact_pass_status(status, metadata_only=True))
        with self.assertRaises(taskctl.TaskctlError):
            taskctl.classify_record(
                "TASK",
                "frozen_v1",
                ["python3", "scripts/frozen_v1_acceptance.py", "--task-id", "TASK"],
            )
        with self.assertRaises(taskctl.TaskctlError):
            taskctl.classify_record(
                "TASK",
                "scope",
                [
                    "env",
                    "PYTHONPATH=/tmp/injected",
                    "python3",
                    "scripts/evidence_scope.py",
                    "finalize",
                    "TASK",
                ],
            )

    def test_strict_review_rejects_self_stale_dual_verdict_and_nonzero_counts(
        self,
    ) -> None:
        candidate = {
            "fingerprint": "a" * 64,
            "patch_sha256": "b" * 64,
            "governance_digest": "c" * 64,
        }
        valid = (
            f"Reviewed-Candidate-Fingerprint: {'a' * 64}\n"
            f"Reviewed-Patch-SHA256: {'b' * 64}\n"
            f"Reviewed-Governance-Digest: {'c' * 64}\n"
            "Reviewer-ID: reviewer-1\nVerdict: APPROVED\nP0: 0\nP1: 0\nP2: 0\n"
        )
        report = self.root / "review.md"
        report.write_text(valid, encoding="utf-8")
        parsed = taskctl.validate_review(
            report,
            candidate,
            expected_reviewer="reviewer-1",
            implementer="implementer",
            used_reviewers=set(),
        )
        self.assertEqual(parsed["Reviewer-ID"], "reviewer-1")
        mutations = (
            valid.replace("reviewer-1", "implementer"),
            valid.replace("a" * 64, "d" * 64),
            valid.replace("b" * 64, "d" * 64),
            valid.replace("c" * 64, "d" * 64),
            valid + "Verdict: CHANGES_REQUESTED\n",
            valid + "CHANGES_REQUESTED\n",
            valid + "Review history mentioned CHANGES_REQUESTED before approval.\n",
            valid.replace("P1: 0", "P1: 1"),
            valid.replace("P2: 0", "P2: none"),
        )
        for content in mutations:
            with self.subTest(content=content[-40:]):
                report.write_text(content, encoding="utf-8")
                with self.assertRaises(taskctl.TaskctlError):
                    taskctl.validate_review(
                        report,
                        candidate,
                        expected_reviewer="reviewer-1",
                        implementer="implementer",
                        used_reviewers=set(),
                    )
        none_reviewer = valid.replace("reviewer-1", "none")
        report.write_text(none_reviewer, encoding="utf-8")
        with self.assertRaises(taskctl.TaskctlError):
            taskctl.validate_review(
                report,
                candidate,
                expected_reviewer="none",
                implementer="implementer",
                used_reviewers=set(),
            )


class LegacyPassTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name).resolve()
        self.task_id = taskctl.GVR1_ID
        self.task_file = self.repo / f"tasks/{self.task_id}.md"
        self.task_file.parent.mkdir(parents=True)
        self.task_file.write_text(
            f"# {self.task_id}\n\nStatus: PASS / ACCEPTED\nRisk-Tier: HIGH\n"
            f'Closure-Tags: ["evidence"]\nTask-Path: tasks/{self.task_id}.md\n\n'
            "## Allowed Files\n\n"
            f"- `tasks/{self.task_id}.md`\n- `work/file.txt`\n"
            f"- `artifacts/{self.task_id}/**`\n",
            encoding="utf-8",
        )
        artifact = self.repo / "artifacts" / self.task_id
        (artifact / "git").mkdir(parents=True)
        (artifact / "review").mkdir()
        (artifact / "outputs").mkdir()
        (artifact / "summary.md").write_text(
            "# Summary\nStatus: PASS / ACCEPTED\n", encoding="utf-8"
        )
        (artifact / "git/diff.patch").write_bytes(b"accepted patch\n")
        (artifact / "task.json").write_text(
            json.dumps(
                {
                    "task_id": self.task_id,
                    "task_file": f"tasks/{self.task_id}.md",
                    "allowlist": [f"tasks/{self.task_id}.md", "work/file.txt"],
                    "repo_root": str(self.repo.resolve()),
                    "baseline_dirty": True,
                }
            ),
            encoding="utf-8",
        )
        paths = [
            self.task_file,
            artifact / "summary.md",
            artifact / "git/diff.patch",
        ]
        hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        (artifact / "review/candidate.sha256").write_text(
            "".join(
                f"{digest}  {path.relative_to(self.repo).as_posix()}\n"
                for digest, path in zip(hashes, paths, strict=True)
            ),
            encoding="utf-8",
        )
        (artifact / "review/independent_review.md").write_text(
            f"Reviewed-Task-SHA256: {hashes[0]}\n"
            f"Reviewed-Summary-SHA256: {hashes[1]}\n"
            f"Reviewed-Patch-SHA256: {hashes[2]}\n"
            "Reviewer-ID: independent-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        rows = []
        for step in (
            "lint",
            "test",
            "review_binding",
            "scope",
            "independent_review",
            "task_gate",
            "atomic_evidence",
            "review_binding",
        ):
            log = artifact / "outputs" / f"{len(rows):02d}-{step}.log"
            log.write_text("PASS\n", encoding="utf-8")
            rows.append(
                {
                    "step": step,
                    "rc": 0,
                    "log": log.relative_to(self.repo).as_posix(),
                }
            )
        (artifact / "results.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        script = self.repo / "scripts/evidence_scope.py"
        script.parent.mkdir()
        script.write_text(
            "def build_patch(task_id, *, root, check_external=True):\n"
            "    return (root / 'artifacts' / task_id / 'git/diff.patch').read_bytes()\n",
            encoding="utf-8",
        )
        self.artifact = artifact

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_legacy_pass_requires_exact_identity_review_order_and_logs(self) -> None:
        self.assertTrue(taskctl.legacy_task_pass(self.repo, self.task_id))
        metadata_path = self.artifact / "task.json"
        metadata = read_json(metadata_path)
        metadata["task_id"] = "FAKE"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        self.assertFalse(taskctl.legacy_task_pass(self.repo, self.task_id))

        metadata["task_id"] = self.task_id
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        checksum = self.artifact / "review/candidate.sha256"
        lines = checksum.read_text(encoding="utf-8").splitlines()
        checksum.write_text(
            "\n".join([lines[0], lines[0], lines[2]]) + "\n", encoding="utf-8"
        )
        self.assertFalse(taskctl.legacy_task_pass(self.repo, self.task_id))

    def test_gvr_dependency_rejects_reversed_legacy_gate_order(self) -> None:
        self.assertTrue(taskctl.legacy_task_pass(self.repo, self.task_id))
        results = self.artifact / "results.jsonl"
        rows = results.read_text(encoding="utf-8").splitlines()
        results.write_text("\n".join(reversed(rows)) + "\n", encoding="utf-8")
        self.assertFalse(taskctl.legacy_task_pass(self.repo, self.task_id))

    def test_gvr_dependency_rejects_new_failure_after_old_success(self) -> None:
        self.assertTrue(taskctl.legacy_task_pass(self.repo, self.task_id))
        log = self.artifact / "outputs/task-gate-failed.log"
        log.write_text("FAIL\n", encoding="utf-8")
        with (self.artifact / "results.jsonl").open("a", encoding="utf-8") as output:
            output.write(
                json.dumps(
                    {
                        "step": "task_gate",
                        "rc": 9,
                        "log": log.relative_to(self.repo).as_posix(),
                    }
                )
                + "\n"
            )
        self.assertFalse(taskctl.legacy_task_pass(self.repo, self.task_id))

    def test_gvr_dependency_requires_native_absolute_identity_fields(self) -> None:
        metadata_path = self.artifact / "task.json"
        accepted = read_json(metadata_path)
        current_directory = Path.cwd()
        os.chdir(self.repo)
        try:
            cases = []
            missing_root = dict(accepted)
            missing_root.pop("repo_root")
            cases.append(missing_root)
            relative_root = dict(accepted)
            relative_root["repo_root"] = "."
            cases.append(relative_root)
            wrong_root = dict(accepted)
            wrong_root["repo_root"] = str(self.repo.parent)
            cases.append(wrong_root)
            non_string_task = dict(accepted)
            non_string_task["task_file"] = 123
            cases.append(non_string_task)

            for metadata in cases:
                with self.subTest(metadata=metadata):
                    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
                    self.assertFalse(taskctl.legacy_task_pass(self.repo, self.task_id))
        finally:
            metadata_path.write_text(json.dumps(accepted), encoding="utf-8")
            os.chdir(current_directory)

    def test_gvr_dependency_rejects_none_legacy_reviewer(self) -> None:
        review = self.artifact / "review/independent_review.md"
        review.write_text(
            review.read_text(encoding="utf-8").replace(
                "Reviewer-ID: independent-reviewer", "Reviewer-ID: none"
            ),
            encoding="utf-8",
        )
        self.assertFalse(taskctl.legacy_task_pass(self.repo, self.task_id))

    def test_gvr_dependency_rejects_boolean_required_result_rc(self) -> None:
        results = self.artifact / "results.jsonl"
        rows = jsonl(results)
        for row in reversed(rows):
            if row["step"] == "lint":
                row["rc"] = False
                break
        results.write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        self.assertFalse(taskctl.legacy_task_pass(self.repo, self.task_id))


class ControllerStateMachineTests(unittest.TestCase):
    TASK_ID = "REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name).resolve()
        (self.repo / "tasks/repo").mkdir(parents=True)
        (self.repo / "scripts").mkdir()
        shutil.copy2(
            ROOT / "scripts/evidence_scope.py", self.repo / "scripts/evidence_scope.py"
        )
        (self.repo / "docs/agents").mkdir(parents=True)
        (self.repo / "AGENTS.md").write_bytes((ROOT / "AGENTS.md").read_bytes())
        self.task_file = self.repo / f"tasks/repo/{self.TASK_ID}.md"
        self.task_file.write_text(
            f"""# {self.TASK_ID}\n\nStatus: READY / CONTRACT FROZEN\nRisk-Tier: HIGH\nClosure-Tags: [\"activation\", \"evidence\", \"governance\", \"release\"]\nTask-Path: tasks/repo/{self.TASK_ID}.md\n\n## Allowed Files\n\n- `tasks/repo/{self.TASK_ID}.md`\n- `AGENTS.md`\n- `docs/agents/manifest.json`\n- `scripts/evidence_init.sh`\n- `scripts/evidence_run.sh`\n- `scripts/evidence_task.py`\n- `scripts/evidence_validate.py`\n- `scripts/task_validate.sh`\n- `scripts/atomic_evidence_validate.py`\n- `scripts/release_gate.sh`\n- `scripts/frozen_v1_acceptance.py`\n- `artifacts/{self.TASK_ID}/**`\n""",
            encoding="utf-8",
        )
        (self.repo / "scripts/frozen_v1_acceptance.py").write_text(
            "raise SystemExit(0)\n", encoding="utf-8"
        )
        for relative in taskctl.FROZEN_V1_CONSUMERS:
            shutil.copy2(ROOT / relative, self.repo / relative)
        self.artifact = self.repo / "artifacts" / self.TASK_ID
        (self.artifact / "git").mkdir(parents=True)
        (self.artifact / "outputs").mkdir()
        (self.artifact / "review").mkdir()
        self.red_ts = "20260717T000000000001"
        self.red_log = self.artifact / "outputs" / f"{self.red_ts}_red.log"
        self.red_log.write_text("RED\n", encoding="utf-8")
        (self.artifact / "commands.jsonl").write_text(
            json.dumps(
                {
                    "ts": self.red_ts,
                    "step": "red",
                    "cmd": " ".join(GVR3_RED_ARGV),
                    "argv": list(GVR3_RED_ARGV),
                    "cwd": str(self.repo.resolve()),
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.artifact / "results.jsonl").write_text(
            json.dumps(
                {
                    "ts": self.red_ts,
                    "step": "red",
                    "rc": 1,
                    "log": self.red_log.relative_to(self.repo).as_posix(),
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.artifact / "task.json").write_text(
            json.dumps(
                {
                    "task_id": self.TASK_ID,
                    "task_file": f"tasks/repo/{self.TASK_ID}.md",
                    "allowlist": [
                        f"tasks/repo/{self.TASK_ID}.md",
                        "AGENTS.md",
                        "docs/agents/manifest.json",
                        *taskctl.FROZEN_V1_CONSUMERS,
                        "scripts/frozen_v1_acceptance.py",
                    ],
                    "repo_root": str(self.repo.resolve()),
                    "baseline_dirty": True,
                    "init_ts": "20260717T000000",
                }
            ),
            encoding="utf-8",
        )
        source_candidate = (
            ROOT / "artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate"
        )
        self.gvr1_candidate = (
            self.repo / "artifacts/REPO-GOVERNANCE-RESET-MODULES-20260716-01/candidate"
        )
        self.gvr1_candidate.mkdir(parents=True)
        for name in ("AGENTS.md", "manifest.json", "governance_digest.json"):
            self.gvr1_candidate.joinpath(name).write_bytes(
                source_candidate.joinpath(name).read_bytes()
            )
        for module in (ROOT / "docs/agents").glob("*.md"):
            self.repo.joinpath("docs/agents", module.name).write_bytes(
                module.read_bytes()
            )
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=self.repo, check=True
        )
        subprocess.run(
            [
                "git",
                "add",
                "AGENTS.md",
                "docs/agents",
                "scripts/evidence_scope.py",
                *taskctl.FROZEN_V1_CONSUMERS,
                "scripts/frozen_v1_acceptance.py",
                "tasks",
                f"artifacts/{taskctl.GVR1_ID}",
            ],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.repo, check=True)
        captured = subprocess.run(
            [sys.executable, "scripts/evidence_scope.py", "capture", self.TASK_ID],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(captured.returncode, 0, captured.stderr)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def kernel(self) -> Path:
        return self.gvr1_candidate / "AGENTS.md"

    @property
    def manifest(self) -> Path:
        return self.gvr1_candidate / "manifest.json"

    def controller(self, **kwargs):
        return taskctl.TaskController(
            self.repo,
            self.TASK_ID,
            actor="lead",
            implementer="implementer",
            **kwargs,
        )

    def test_controller_rejects_noncanonical_durable_identities(self) -> None:
        invalid = ("", " ", "none", "NoNe", " reviewer ", "reviewer\nshadow")
        for identity in invalid:
            with self.subTest(role="actor", identity=repr(identity)):
                with self.assertRaisesRegex(taskctl.TaskctlError, "identit"):
                    taskctl.TaskController(
                        self.repo,
                        self.TASK_ID,
                        actor=identity,
                        implementer="implementer",
                    )
            with self.subTest(role="implementer", identity=repr(identity)):
                with self.assertRaisesRegex(taskctl.TaskctlError, "identit"):
                    taskctl.TaskController(
                        self.repo,
                        self.TASK_ID,
                        actor="lead",
                        implementer=identity,
                    )

    def test_state_binding_rejects_noncanonical_implementer_alias(self) -> None:
        controller = self.bootstrap()
        state = read_json(self.artifact / "state.json")
        state["implementer"] = " governance-reviewer "
        (self.artifact / "state.json").write_bytes(taskctl.canonical_json(state))
        with self.assertRaisesRegex(taskctl.TaskctlError, "identit"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)

    def delete_result_for_step(self, step: str, artifact: Path | None = None) -> None:
        event_root = (artifact or self.artifact) / "events"
        matches = [
            path
            for path in event_root.glob("*.command.json")
            if read_json(path)["step"] == step
        ]
        self.assertTrue(matches, step)
        ordinal = matches[-1].name.split(".", 1)[0]
        (event_root / f"{ordinal}.result.json").unlink()

    def bootstrap(self) -> taskctl.TaskController:
        controller = self.controller()
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        return controller

    def assert_raw_bootstrap_candidate_drift_rejected(self, name: str) -> None:
        path = self.gvr1_candidate / name
        accepted = path.read_bytes()
        path.write_bytes(accepted + b"\n")
        try:
            with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
                with self.assertRaisesRegex(
                    taskctl.TaskctlError, "accepted GVR-1|bootstrap governance"
                ):
                    self.controller().start(
                        self.task_file,
                        bootstrap_kernel=self.kernel,
                        bootstrap_manifest=self.manifest,
                    )
            self.assertFalse((self.artifact / "state.json").exists())
            self.assertFalse((self.artifact / "events").exists())
        finally:
            path.write_bytes(accepted)

    def test_bootstrap_rejects_manifest_raw_drift_before_first_start(self) -> None:
        self.assert_raw_bootstrap_candidate_drift_rejected("manifest.json")

    def test_bootstrap_rejects_digest_record_raw_drift_before_first_start(self) -> None:
        self.assert_raw_bootstrap_candidate_drift_rejected("governance_digest.json")

    def test_bootstrap_rejects_kernel_raw_drift_before_first_start(self) -> None:
        self.assert_raw_bootstrap_candidate_drift_rejected("AGENTS.md")

    def test_bootstrap_rejects_pre_v2_root_drift_before_any_durable_action(
        self,
    ) -> None:
        root = self.repo / "AGENTS.md"
        root.write_bytes(root.read_bytes() + b"\n")
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "pre-v2 root"):
                self.controller().start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertFalse((self.artifact / "events").exists())
        self.assertFalse((self.artifact / "legacy-bundle.json").exists())
        self.assertFalse((self.artifact / "bootstrap").exists())

    def test_bootstrap_rejects_external_symlink_to_candidate(self) -> None:
        alias = self.repo.parent / f"{self.repo.name}-kernel-alias"
        alias.symlink_to(self.kernel)
        try:
            with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
                with self.assertRaisesRegex(taskctl.TaskctlError, "outside|symlink"):
                    self.controller().start(
                        self.task_file,
                        bootstrap_kernel=alias,
                        bootstrap_manifest=self.manifest,
                    )
            self.assertFalse((self.artifact / "state.json").exists())
        finally:
            alias.unlink(missing_ok=True)

    def test_bootstrap_rejects_symlinked_task_lock_authority(self) -> None:
        external = self.repo.parent / f"{self.repo.name}-external-locks"
        external.mkdir()
        (self.artifact / "locks").symlink_to(external, target_is_directory=True)
        try:
            with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
                with self.assertRaisesRegex(taskctl.TaskctlError, "authority|symlink"):
                    self.controller().start(
                        self.task_file,
                        bootstrap_kernel=self.kernel,
                        bootstrap_manifest=self.manifest,
                    )
            self.assertEqual(list(external.iterdir()), [])
            self.assertTrue((self.artifact / "locks").is_symlink())
        finally:
            (self.artifact / "locks").unlink(missing_ok=True)
            shutil.rmtree(external)

    def test_bootstrap_rejects_noncanonical_or_external_red_log(self) -> None:
        accepted = (self.artifact / "results.jsonl").read_bytes()
        outside = self.repo / "outside-red.log"
        outside.write_text("RED\n", encoding="utf-8")
        invalid_logs = (
            str(outside.resolve()),
            "../outside-red.log",
            f"artifacts/{self.TASK_ID}/red.log",
        )
        try:
            for log in invalid_logs:
                with self.subTest(log=log):
                    result = json.loads(accepted.decode("utf-8"))
                    result["log"] = log
                    (self.artifact / "results.jsonl").write_text(
                        json.dumps(result) + "\n",
                        encoding="utf-8",
                    )
                    with mock.patch.object(
                        taskctl, "legacy_task_pass", return_value=True
                    ):
                        with self.assertRaisesRegex(taskctl.TaskctlError, "RED log"):
                            self.controller().start(
                                self.task_file,
                                bootstrap_kernel=self.kernel,
                                bootstrap_manifest=self.manifest,
                            )
                    self.assertFalse((self.artifact / "state.json").exists())
        finally:
            (self.artifact / "results.jsonl").write_bytes(accepted)

    def assert_bootstrap_red_record_rejected(
        self,
        *,
        command_change: Callable[[dict[str, object]], None] | None = None,
        result_change: Callable[[dict[str, object]], None] | None = None,
    ) -> None:
        command = jsonl(self.artifact / "commands.jsonl")[0]
        result = jsonl(self.artifact / "results.jsonl")[0]
        if command_change is not None:
            command_change(command)
        if result_change is not None:
            result_change(result)
        (self.artifact / "commands.jsonl").write_text(
            json.dumps(command) + "\n", encoding="utf-8"
        )
        (self.artifact / "results.jsonl").write_text(
            json.dumps(result) + "\n", encoding="utf-8"
        )
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "RED"):
                self.controller().start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertFalse((self.artifact / "state.json").exists())

    def test_bootstrap_rejects_unpaired_red_command(self) -> None:
        self.assert_bootstrap_red_record_rejected(
            command_change=lambda command: command.update(ts="20260717T999999999999")
        )

    def test_bootstrap_rejects_wrong_red_argv(self) -> None:
        self.assert_bootstrap_red_record_rejected(
            command_change=lambda command: command.update(argv=["python3", "-V"])
        )

    def test_bootstrap_rejects_wrong_red_cwd(self) -> None:
        self.assert_bootstrap_red_record_rejected(
            command_change=lambda command: command.update(cwd=str(self.repo.parent))
        )

    def test_bootstrap_rejects_boolean_red_rc(self) -> None:
        self.assert_bootstrap_red_record_rejected(
            result_change=lambda result: result.update(rc=True)
        )

    def test_bootstrap_rejects_signal_terminated_red(self) -> None:
        self.assert_bootstrap_red_record_rejected(
            result_change=lambda result: result.update(rc=-signal.SIGTERM)
        )

    def red_command(self, timestamp: str) -> dict[str, object]:
        return {
            "ts": timestamp,
            "step": "red",
            "cmd": " ".join(GVR3_RED_ARGV),
            "argv": list(GVR3_RED_ARGV),
            "cwd": str(self.repo.resolve()),
        }

    def red_result(self, timestamp: str) -> dict[str, object]:
        log = self.artifact / "outputs" / f"{timestamp}_red.log"
        log.write_text("RED\n", encoding="utf-8")
        return {
            "ts": timestamp,
            "step": "red",
            "rc": 1,
            "log": log.relative_to(self.repo).as_posix(),
        }

    def test_bootstrap_accepts_latest_exact_red_pair_after_prior_retry(self) -> None:
        earlier = "20260716T235959999999"
        commands = [
            self.red_command(earlier),
            *jsonl(self.artifact / "commands.jsonl"),
        ]
        results = [
            self.red_result(earlier),
            *jsonl(self.artifact / "results.jsonl"),
        ]
        (self.artifact / "commands.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in commands),
            encoding="utf-8",
        )
        (self.artifact / "results.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in results),
            encoding="utf-8",
        )
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            state = self.controller().start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(state["state"], "IMPLEMENTING")

    def test_bootstrap_rejects_later_unmatched_red_command(self) -> None:
        later = "20260717T000000000002"
        with (self.artifact / "commands.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps(self.red_command(later)) + "\n")
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "RED"):
                self.controller().start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )

    def test_bootstrap_rejects_later_unmatched_red_result(self) -> None:
        later = "20260717T000000000002"
        with (self.artifact / "results.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps(self.red_result(later)) + "\n")
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "RED"):
                self.controller().start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )

    def test_bootstrap_rejects_invalid_task_metadata_root_identity(self) -> None:
        metadata_path = self.artifact / "task.json"
        accepted = read_json(metadata_path)
        cases = []
        missing = dict(accepted)
        missing.pop("repo_root")
        cases.append(missing)
        non_string = dict(accepted)
        non_string["repo_root"] = 123
        cases.append(non_string)
        relative = dict(accepted)
        relative["repo_root"] = "."
        cases.append(relative)
        wrong = dict(accepted)
        wrong["repo_root"] = str(self.repo.parent)
        cases.append(wrong)
        current_directory = Path.cwd()
        os.chdir(self.repo)
        try:
            for metadata in cases:
                with self.subTest(repo_root=metadata.get("repo_root")):
                    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
                    with mock.patch.object(
                        taskctl, "legacy_task_pass", return_value=True
                    ):
                        with self.assertRaisesRegex(taskctl.TaskctlError, "repo_root"):
                            self.controller().start(
                                self.task_file,
                                bootstrap_kernel=self.kernel,
                                bootstrap_manifest=self.manifest,
                            )
                    self.assertFalse((self.artifact / "state.json").exists())
                    self.assertFalse((self.artifact / "events").exists())
        finally:
            metadata_path.write_text(json.dumps(accepted), encoding="utf-8")
            os.chdir(current_directory)

    def test_bootstrap_rejects_frozen_consumer_drift_before_snapshot(self) -> None:
        for index, relative in enumerate(taskctl.FROZEN_V1_CONSUMERS):
            with self.subTest(relative=relative):
                if index:
                    self.tearDown()
                    self.setUp()
                consumer = self.repo / relative
                consumer.write_bytes(consumer.read_bytes() + b"\n# drift\n")
                with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
                    with self.assertRaisesRegex(
                        taskctl.TaskctlError, "frozen-v1 consumer"
                    ):
                        self.controller().start(
                            self.task_file,
                            bootstrap_kernel=self.kernel,
                            bootstrap_manifest=self.manifest,
                        )
                self.assertFalse((self.artifact / "state.json").exists())
                self.assertFalse((self.artifact / "events").exists())
                self.assertFalse(
                    (self.artifact / "bootstrap/frozen-v1-plan.json").exists()
                )
                self.assertFalse((self.artifact / "bootstrap/frozen-v1").exists())

    def test_bootstrap_rejects_preseeded_invalid_frozen_source_plan(self) -> None:
        plan_path = self.artifact / "bootstrap/frozen-v1-plan.json"
        plan_path.parent.mkdir(parents=True)
        entries: list[dict[str, object]] = []
        plan_path.write_bytes(
            taskctl.canonical_json(
                {
                    "schema_version": 999,
                    "entries": entries,
                    "tree_sha256": taskctl._canonical_digest(entries),
                }
            )
        )
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "frozen-v1 source plan"):
                self.controller().start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertFalse((self.artifact / "events").exists())

    def test_bootstrap_rejects_unowned_valid_partial_frozen_snapshot(self) -> None:
        controller = self.controller()
        contract = taskctl.parse_task_contract(self.task_file, self.TASK_ID, self.repo)
        plan = controller._prepare_frozen_v1_plan(contract)
        plan_path = self.artifact / "bootstrap/frozen-v1-plan.json"
        plan_path.parent.mkdir(parents=True)
        plan_path.write_bytes(taskctl.canonical_json(plan))
        first = taskctl.FROZEN_V1_CONSUMERS[0]
        snapshot = self.artifact / "bootstrap/frozen-v1" / first
        snapshot.parent.mkdir(parents=True)
        shutil.copy2(self.repo / first, snapshot)
        drifted = self.repo / taskctl.FROZEN_V1_CONSUMERS[1]
        drifted.write_bytes(b"DRIFTED-BEFORE-DURABLE-START\n")

        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "live source"):
                controller.start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertFalse((self.artifact / "events").exists())

    def test_bootstrap_rejects_preseeded_invalid_legacy_bundle_inventory(self) -> None:
        entries: list[dict[str, object]] = []
        (self.artifact / "legacy-bundle.json").write_bytes(
            taskctl.canonical_json(
                {
                    "schema_version": 999,
                    "task_id": "WRONG",
                    "entries": entries,
                    "tree_sha256": taskctl._canonical_digest(entries),
                }
            )
        )
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "legacy bundle"):
                self.controller().start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertFalse((self.artifact / "events").exists())

    def test_bootstrap_rejects_preseeded_truncated_legacy_prefix(self) -> None:
        commands = (self.artifact / "commands.jsonl").read_bytes()
        results = (self.artifact / "results.jsonl").read_bytes()
        (self.artifact / "legacy-prefix.json").write_bytes(
            taskctl.canonical_json(
                {
                    "commands_length": 0,
                    "commands_sha256": hashlib.sha256(b"").hexdigest(),
                    "results_length": 0,
                    "results_sha256": hashlib.sha256(b"").hexdigest(),
                }
            )
        )
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "entire pre-v2 view"):
                self.controller().start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertEqual((self.artifact / "commands.jsonl").read_bytes(), commands)
        self.assertEqual((self.artifact / "results.jsonl").read_bytes(), results)
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertFalse((self.artifact / "events").exists())

    def test_bootstrap_preserves_unattributed_taskctl_named_file(self) -> None:
        foreign = self.artifact / (".commands.jsonl.taskctl-123-" + "a" * 32)
        foreign.write_text("foreign legacy bytes\n", encoding="utf-8")
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "unattributed"):
                self.controller().start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertEqual(foreign.read_text(encoding="utf-8"), "foreign legacy bytes\n")
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertFalse((self.artifact / "events").exists())

    def test_bootstrap_missing_mismatch_dependency_failure_and_idempotence(
        self,
    ) -> None:
        controller = self.controller()
        with self.assertRaises(taskctl.TaskctlError):
            controller.start(self.task_file, bootstrap_kernel=self.kernel)
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=False):
            with self.assertRaisesRegex(taskctl.TaskctlError, "dependency"):
                controller.start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        preserved = {
            name: (self.artifact / name).read_bytes()
            for name in (
                "task.json",
                "baseline_allowlist.diff",
                "baseline_external_files.txt",
                "commands.jsonl",
                "results.jsonl",
            )
        }
        (self.artifact / "results.jsonl").write_bytes(b"")
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "RED"):
                controller.start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        (self.artifact / "results.jsonl").write_bytes(preserved["results.jsonl"])
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
            first_state = (self.artifact / "state.json").read_bytes()
            first_prefix = (self.artifact / "commands.jsonl").read_bytes()
            controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        for name in (
            "task.json",
            "baseline_allowlist.diff",
            "baseline_external_files.txt",
        ):
            self.assertEqual((self.artifact / name).read_bytes(), preserved[name])
        self.assertTrue(
            (self.artifact / "commands.jsonl")
            .read_bytes()
            .startswith(preserved["commands.jsonl"])
        )
        self.assertTrue(
            (self.artifact / "results.jsonl")
            .read_bytes()
            .startswith(preserved["results.jsonl"])
        )
        self.assertEqual((self.artifact / "state.json").read_bytes(), first_state)
        self.assertEqual((self.artifact / "commands.jsonl").read_bytes(), first_prefix)
        selection = read_json(self.artifact / "module_selection.json")
        self.assertEqual(selection["task_id"], self.TASK_ID)
        self.assertTrue(selection["modules"])
        self.assertTrue(
            all(
                "field_matches" in row
                for module in selection["modules"]
                for row in module["selectors"]
            )
        )
        frozen = self.artifact / "bootstrap/frozen-v1"
        for relative in taskctl.FROZEN_V1_CONSUMERS:
            self.assertEqual(
                (frozen / relative).read_bytes(), (self.repo / relative).read_bytes()
            )
        self.assertTrue((frozen / "inventory.json").is_file())
        wrong_kernel = self.gvr1_candidate / "wrong.md"
        wrong_kernel.write_text("wrong", encoding="utf-8")
        with self.assertRaises(taskctl.TaskctlError):
            controller.start(
                self.task_file,
                bootstrap_kernel=wrong_kernel,
                bootstrap_manifest=self.manifest,
            )
        manifest_bytes = self.manifest.read_bytes()
        self.manifest.write_bytes(manifest_bytes + b"\n")
        try:
            with self.assertRaises(taskctl.TaskctlError):
                controller.start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        finally:
            self.manifest.write_bytes(manifest_bytes)

    def test_bound_legacy_prefix_metadata_cannot_drop_original_views(self) -> None:
        controller = self.bootstrap()
        commands_before = (self.artifact / "commands.jsonl").read_bytes()
        results_before = (self.artifact / "results.jsonl").read_bytes()
        (self.artifact / "legacy-prefix.json").write_bytes(
            taskctl.canonical_json(
                {
                    "commands_length": 0,
                    "commands_sha256": hashlib.sha256(b"").hexdigest(),
                    "results_length": 0,
                    "results_sha256": hashlib.sha256(b"").hexdigest(),
                }
            )
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "legacy prefix"):
            controller.record(
                "lint",
                [sys.executable, "-c", "raise SystemExit(0)"],
                self.repo,
            )
        self.assertEqual(
            (self.artifact / "commands.jsonl").read_bytes(), commands_before
        )
        self.assertEqual((self.artifact / "results.jsonl").read_bytes(), results_before)

    def test_manifest_mutations_fail_closed_before_routing(self) -> None:
        valid = json.loads(self.manifest.read_text(encoding="utf-8"))
        cases: list[dict[str, object]] = []

        invalid_risk = copy.deepcopy(valid)
        invalid_risk["modules"][3]["selectors"][0]["risk_any"] = ["ULTRA"]
        cases.append(invalid_risk)

        unsafe_glob = copy.deepcopy(valid)
        unsafe_glob["modules"][4]["selectors"][1]["task_path_any"] = ["../tasks/**"]
        cases.append(unsafe_glob)

        invalid_tag = copy.deepcopy(valid)
        invalid_tag["required_closure_tags"] = sorted(
            [*invalid_tag["required_closure_tags"], "Bad-Tag"]
        )
        cases.append(invalid_tag)

        unrouted = copy.deepcopy(valid)
        unrouted["required_closure_tags"] = sorted(
            [*unrouted["required_closure_tags"], "unrouted"]
        )
        cases.append(unrouted)

        invalid_owner = copy.deepcopy(valid)
        invalid_owner["rule_owners"]["bad id"] = "docs/agents/evidence.md"
        cases.append(invalid_owner)

        for manifest in cases:
            with (
                self.subTest(manifest=manifest),
                self.assertRaises(taskctl.TaskctlError),
            ):
                taskctl._validate_manifest(manifest, self.repo)

        wrong_owner = copy.deepcopy(valid)
        wrong_owner["rule_owners"]["GOV-SCOPE-001"] = "docs/agents/evidence.md"
        with self.assertRaisesRegex(taskctl.TaskctlError, "owner inventory"):
            taskctl.governance_digest(self.repo, self.kernel, wrong_owner)

    def test_frozen_v1_partial_copy_recovers_only_from_durable_source_plan(
        self,
    ) -> None:
        original_commands = (self.artifact / "commands.jsonl").read_bytes()
        original_results = (self.artifact / "results.jsonl").read_bytes()
        controller = self.controller(
            fault=Fault(
                f"after_frozen_v1_copy:{taskctl.FROZEN_V1_CONSUMERS[0]}",
                RuntimeError("copy crash"),
            )
        )
        second = self.repo / taskctl.FROZEN_V1_CONSUMERS[1]
        original_second = second.read_bytes()
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(RuntimeError, "copy crash"):
                controller.start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertTrue((self.artifact / "bootstrap/frozen-v1-plan.json").is_file())
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )
        self.assertEqual(
            (self.artifact / "bootstrap/legacy-bundle/commands.jsonl").read_bytes(),
            original_commands,
        )
        self.assertEqual(
            (self.artifact / "bootstrap/legacy-bundle/results.jsonl").read_bytes(),
            original_results,
        )
        second.write_bytes(b"NEW-AFTER-CRASH\n")
        controller.fault = None
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(
            (
                self.artifact / "bootstrap/frozen-v1" / taskctl.FROZEN_V1_CONSUMERS[1]
            ).read_bytes(),
            original_second,
        )

    def test_bootstrap_command_precedes_effect_and_blocks_owner_takeover(
        self,
    ) -> None:
        original_commands = (self.artifact / "commands.jsonl").read_bytes()
        original_results = (self.artifact / "results.jsonl").read_bytes()
        controller_a = self.controller()
        controller_a.events.fault = Fault(
            "after_create_dir_fsync_command_event",
            RuntimeError("command crash"),
        )
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(RuntimeError, "command crash"):
                controller_a.start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )

        self.assertFalse((self.artifact / "state.json").exists())
        commands = sorted((self.artifact / "events").glob("*.command.json"))
        self.assertEqual(len(commands), 1)
        command = read_json(commands[0])
        self.assertEqual(command["step"], "taskctl_start")
        self.assertEqual(
            command["argv"][command["argv"].index("--controller") + 1], "lead"
        )
        self.assertEqual(
            command["argv"][command["argv"].index("--implementer") + 1],
            "implementer",
        )
        expected_prefix_values = {
            "--legacy-commands-length": str(len(original_commands)),
            "--legacy-commands-sha256": hashlib.sha256(original_commands).hexdigest(),
            "--legacy-results-length": str(len(original_results)),
            "--legacy-results-sha256": hashlib.sha256(original_results).hexdigest(),
        }
        for flag, expected_value in expected_prefix_values.items():
            self.assertEqual(
                command["argv"][command["argv"].index(flag) + 1], expected_value
            )
        self.assertFalse(
            (
                self.artifact / "events" / commands[0].name.replace("command", "result")
            ).is_file()
        )
        self.assertEqual(
            (self.artifact / "commands.jsonl").read_bytes(), original_commands
        )
        self.assertEqual(
            (self.artifact / "results.jsonl").read_bytes(), original_results
        )
        for relative in (
            "legacy-bundle.json",
            "legacy-prefix.json",
            "bootstrap/legacy-bundle",
            "bootstrap/frozen-v1-plan.json",
            "bootstrap/frozen-v1",
            "module_selection.json",
            "state.json",
        ):
            self.assertFalse((self.artifact / relative).exists(), relative)

        for actor, implementer in (
            ("lead-B", "implementer"),
            ("lead", "implementer-B"),
        ):
            controller_b = taskctl.TaskController(
                self.repo,
                self.TASK_ID,
                actor=actor,
                implementer=implementer,
            )
            with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
                with self.assertRaisesRegex(
                    taskctl.TaskctlError, "ownership|immutable inputs"
                ):
                    controller_b.start(
                        self.task_file,
                        bootstrap_kernel=self.kernel,
                        bootstrap_manifest=self.manifest,
                    )
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )

        controller_a.events.fault = None
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            state = controller_a.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(state["controller"], "lead")
        self.assertEqual(state["implementer"], "implementer")
        self.assertIsNone(controller_a.events.first_incomplete())
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )

    def test_bootstrap_sigkill_view_temporary_recovers_same_ordinal(self) -> None:
        original_commands = (self.artifact / "commands.jsonl").read_bytes()
        original_results = (self.artifact / "results.jsonl").read_bytes()
        child = (
            "import importlib.machinery,importlib.util,os,pathlib,signal,sys;"
            "loader=importlib.machinery.SourceFileLoader('tc_bootstrap_child',sys.argv[1]);"
            "spec=importlib.util.spec_from_loader(loader.name,loader);"
            "module=importlib.util.module_from_spec(spec);"
            "sys.modules[loader.name]=module;loader.exec_module(module);"
            "module.legacy_task_pass=lambda *args,**kwargs: True;"
            "controller=module.TaskController(pathlib.Path(sys.argv[2]),sys.argv[3],"
            "actor='lead',implementer='implementer');"
            "controller.events.fault=lambda point: os.kill(os.getpid(),signal.SIGKILL) "
            "if point=='before_replace_command_view' else None;"
            "controller.start(pathlib.Path(sys.argv[4]),"
            "bootstrap_kernel=pathlib.Path(sys.argv[5]),"
            "bootstrap_manifest=pathlib.Path(sys.argv[6]))"
        )
        crashed = subprocess.run(
            [
                sys.executable,
                "-c",
                child,
                str(TASKCTL_PATH),
                str(self.repo),
                self.TASK_ID,
                str(self.task_file),
                str(self.kernel),
                str(self.manifest),
            ],
            cwd=self.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(crashed.returncode, -signal.SIGKILL, crashed.stderr)
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )
        self.assertFalse((self.artifact / "state.json").exists())
        self.assertEqual(
            (self.artifact / "commands.jsonl").read_bytes(), original_commands
        )
        self.assertEqual(
            (self.artifact / "results.jsonl").read_bytes(), original_results
        )
        self.assertTrue(list(self.artifact.glob(".commands.jsonl.taskctl-*")))

        controller = self.controller()
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            state = controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(state["state"], "IMPLEMENTING")
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )
        self.assertIsNone(controller.events.first_incomplete())
        self.assertEqual(
            [
                path
                for path in self.artifact.rglob("*")
                if taskctl._is_atomic_temporary(path)
            ],
            [],
        )
        self.assertEqual(
            (self.artifact / "bootstrap/legacy-bundle/commands.jsonl").read_bytes(),
            original_commands,
        )
        self.assertEqual(
            (self.artifact / "bootstrap/legacy-bundle/results.jsonl").read_bytes(),
            original_results,
        )

    def test_bootstrap_sigkill_before_command_link_cleans_staging_and_recovers(
        self,
    ) -> None:
        child = (
            "import importlib.machinery,importlib.util,os,pathlib,signal,sys;"
            "loader=importlib.machinery.SourceFileLoader('tc_prelink_child',sys.argv[1]);"
            "spec=importlib.util.spec_from_loader(loader.name,loader);"
            "module=importlib.util.module_from_spec(spec);"
            "sys.modules[loader.name]=module;loader.exec_module(module);"
            "module.legacy_task_pass=lambda *args,**kwargs: True;"
            "controller=module.TaskController(pathlib.Path(sys.argv[2]),sys.argv[3],"
            "actor='lead',implementer='implementer');"
            "controller.events.fault=lambda point: os.kill(os.getpid(),signal.SIGKILL) "
            "if point=='before_exclusive_link_command_event' else None;"
            "controller.start(pathlib.Path(sys.argv[4]),"
            "bootstrap_kernel=pathlib.Path(sys.argv[5]),"
            "bootstrap_manifest=pathlib.Path(sys.argv[6]))"
        )
        crashed = subprocess.run(
            [
                sys.executable,
                "-c",
                child,
                str(TASKCTL_PATH),
                str(self.repo),
                self.TASK_ID,
                str(self.task_file),
                str(self.kernel),
                str(self.manifest),
            ],
            cwd=self.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(crashed.returncode, -signal.SIGKILL, crashed.stderr)
        self.assertFalse(list((self.artifact / "events").glob("*.command.json")))
        self.assertTrue(list((self.artifact / "events").glob(".*.create-*")))

        controller = self.controller()
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            state = controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(state["state"], "IMPLEMENTING")
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )
        self.assertEqual(
            [
                path
                for path in self.artifact.rglob("*")
                if taskctl._is_atomic_temporary(path)
            ],
            [],
        )

    def test_bootstrap_sigkill_after_command_link_recovers_same_authority(
        self,
    ) -> None:
        child = (
            "import importlib.machinery,importlib.util,os,pathlib,signal,sys;"
            "loader=importlib.machinery.SourceFileLoader('tc_postlink_child',sys.argv[1]);"
            "spec=importlib.util.spec_from_loader(loader.name,loader);"
            "module=importlib.util.module_from_spec(spec);"
            "sys.modules[loader.name]=module;loader.exec_module(module);"
            "module.legacy_task_pass=lambda *args,**kwargs: True;"
            "controller=module.TaskController(pathlib.Path(sys.argv[2]),sys.argv[3],"
            "actor='lead',implementer='implementer');"
            "controller.events.fault=lambda point: os.kill(os.getpid(),signal.SIGKILL) "
            "if point=='after_exclusive_link_command_event' else None;"
            "controller.start(pathlib.Path(sys.argv[4]),"
            "bootstrap_kernel=pathlib.Path(sys.argv[5]),"
            "bootstrap_manifest=pathlib.Path(sys.argv[6]))"
        )
        crashed = subprocess.run(
            [
                sys.executable,
                "-c",
                child,
                str(TASKCTL_PATH),
                str(self.repo),
                self.TASK_ID,
                str(self.task_file),
                str(self.kernel),
                str(self.manifest),
            ],
            cwd=self.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(crashed.returncode, -signal.SIGKILL, crashed.stderr)
        commands = list((self.artifact / "events").glob("*.command.json"))
        staging = list((self.artifact / "events").glob(".*.create-*"))
        self.assertEqual(len(commands), 1)
        self.assertEqual(len(staging), 1)
        self.assertEqual(commands[0].stat().st_ino, staging[0].stat().st_ino)
        self.assertFalse((self.artifact / "state.json").exists())

        controller = self.controller()
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            state = controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(state["state"], "IMPLEMENTING")
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )
        self.assertEqual(
            [
                path
                for path in self.artifact.rglob("*")
                if taskctl._is_atomic_temporary(path)
            ],
            [],
        )

    def test_bootstrap_exact_verifies_frozen_snapshot_before_state(self) -> None:
        extra = self.artifact / "bootstrap/frozen-v1/unexpected.txt"
        extra.parent.mkdir(parents=True)
        extra.write_text("unexpected\n", encoding="utf-8")
        controller = self.controller()
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaisesRegex(taskctl.TaskctlError, "missing or extra"):
                controller.start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        self.assertFalse((self.artifact / "state.json").exists())
        commands = list((self.artifact / "events").glob("*.command.json"))
        self.assertEqual(len(commands), 1)
        self.assertFalse(
            (
                self.artifact / "events" / commands[0].name.replace("command", "result")
            ).exists()
        )

        extra.unlink()
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            state = controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(state["state"], "IMPLEMENTING")
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), 1
        )

    def test_doctor_reports_pre_state_partial_and_recoverable_start(self) -> None:
        controller = self.controller(
            fault=Fault(
                f"after_frozen_v1_copy:{taskctl.FROZEN_V1_CONSUMERS[0]}",
                RuntimeError("copy crash"),
            )
        )
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            with self.assertRaises(RuntimeError):
                controller.start(
                    self.task_file,
                    bootstrap_kernel=self.kernel,
                    bootstrap_manifest=self.manifest,
                )
        before = {
            path.relative_to(self.artifact): path.read_bytes()
            for path in self.artifact.rglob("*")
            if path.is_file()
        }
        report = controller.doctor()
        self.assertEqual(report["live_state"], "RECOVERABLE_INTERNAL")
        self.assertEqual(report["first_incomplete_ordinal"], 1)
        after = {
            path.relative_to(self.artifact): path.read_bytes()
            for path in self.artifact.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_state_binding_rejects_task_json_allowlist_tampering(self) -> None:
        controller = self.bootstrap()
        metadata = read_json(self.artifact / "task.json")
        metadata["allowlist"].append("outside.txt")
        (self.artifact / "task.json").write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(taskctl.TaskctlError, "task.json|baseline"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        state = read_json(self.artifact / "state.json")
        self.assertEqual(state["state"], "IMPLEMENTING")
        self.assertNotIn("candidate", state)

    def test_prepare_review_rejects_tampered_required_command(self) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "lint"
        ]
        self.assertTrue(commands)
        command = read_json(commands[-1])
        command["argv"] = ["tampered"]
        commands[-1].write_text(json.dumps(command), encoding="utf-8")
        with self.assertRaisesRegex(taskctl.TaskctlError, "digest mismatch"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "IMPLEMENTING"
        )

    def test_prepare_review_requires_every_frozen_gvr3_result(self) -> None:
        required_steps = tuple(
            step for step, _argv, _classification in self.gvr3_required_commands()
        )
        for index, missing in enumerate(required_steps):
            with self.subTest(missing=missing):
                if index:
                    self.tearDown()
                    self.setUp()
                controller = self.bootstrap()
                self.install_required_results(controller, omit=frozenset({missing}))
                patch = self.artifact / "git/diff.patch"
                if not patch.exists():
                    patch.write_bytes(b"")
                with self.assertRaises(taskctl.TaskctlError):
                    controller.prepare_review(
                        kernel=self.kernel, manifest=self.manifest
                    )
                self.assertEqual(
                    read_json(self.artifact / "state.json")["state"],
                    "IMPLEMENTING",
                )

    def test_prepare_review_rejects_latest_test_from_nonfrozen_command(self) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        log = self.artifact / "outputs/backend-version.log"
        log.write_text("pytest version\n", encoding="utf-8")
        controller.events.run(
            step="test",
            argv=[str(self.repo / "backend/.venv/bin/pytest"), "--version"],
            cwd=self.repo / "backend",
            classification="SQLITE",
            runner=lambda: {
                "rc": 0,
                "executed": True,
                "log": str(log.relative_to(self.repo)),
            },
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "exact frozen"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)

    def test_gvr3_reserved_record_requires_repository_root(self) -> None:
        controller = self.bootstrap()
        shadow = self.repo / "shadow"
        shadow.mkdir()
        with self.assertRaisesRegex(taskctl.TaskctlError, "repository root"):
            controller.record("diff_check", list(taskctl.GVR3_DIFF_CHECK_ARGV), shadow)

    def test_gvr3_backend_test_cannot_replace_frozen_unittest(self) -> None:
        controller = self.bootstrap()
        with self.assertRaisesRegex(taskctl.TaskctlError, "exact frozen"):
            controller.backend_test("test", ["--version"])

    def test_prepare_review_rejects_external_or_symlink_required_log(self) -> None:
        for index, mode in enumerate(("absolute", "symlink")):
            with self.subTest(mode=mode):
                if index:
                    self.tearDown()
                    self.setUp()
                controller = self.bootstrap()
                self.install_required_results(controller)
                existing = self.artifact / "outputs/lint.log"
                if mode == "absolute":
                    invalid_log = str(existing.resolve())
                else:
                    linked = self.artifact / "outputs/linked-required.log"
                    linked.symlink_to(existing.name)
                    invalid_log = linked.relative_to(self.repo).as_posix()
                results = [
                    path
                    for path in (self.artifact / "events").glob("*.result.json")
                    if read_json(path)["step"] == "lint"
                ]
                self.assertTrue(results)
                result = read_json(results[-1])
                result["log"] = invalid_log
                results[-1].write_text(json.dumps(result), encoding="utf-8")
                with self.assertRaisesRegex(
                    taskctl.TaskctlError, "required result.*log|log.*task outputs"
                ):
                    controller.prepare_review(
                        kernel=self.kernel, manifest=self.manifest
                    )
                self.assertEqual(
                    read_json(self.artifact / "state.json")["state"], "IMPLEMENTING"
                )

    def test_controlled_runner_uses_repo_cwd_exact_argv_and_strips_python_env(
        self,
    ) -> None:
        controller = self.bootstrap()
        observation = self.artifact / "controlled-env.json"
        runner = self.repo / "scripts/frozen_v1_acceptance.py"
        runner.write_text(
            "import json,os,pathlib,sys\n"
            f"pathlib.Path({str(observation)!r}).write_text(json.dumps({{"
            "'cwd':os.getcwd(),'argv':sys.argv[1:],"
            "'pythonpath':os.environ.get('PYTHONPATH'),"
            "'pythonhome':os.environ.get('PYTHONHOME')}))\n",
            encoding="utf-8",
        )
        argv = [
            "python3",
            "scripts/frozen_v1_acceptance.py",
            "--task-id",
            self.TASK_ID,
            "--frozen-root",
            f"artifacts/{self.TASK_ID}/bootstrap/frozen-v1",
            "--candidate-root",
            f"artifacts/{self.TASK_ID}/candidate",
        ]
        with mock.patch.dict(
            os.environ,
            {"PYTHONPATH": "/tmp/injected", "PYTHONHOME": "/tmp/injected-home"},
        ):
            result = controller.record("frozen_v1", argv, self.repo)
        self.assertEqual(result["rc"], 0)
        observed = read_json(observation)
        self.assertEqual(Path(observed["cwd"]).resolve(), self.repo.resolve())
        self.assertEqual(observed["argv"], argv[2:])
        self.assertIsNone(observed["pythonpath"])
        self.assertIsNone(observed["pythonhome"])

    def test_internal_start_prepare_lease_and_submit_recover_lost_results(self) -> None:
        controller = self.bootstrap()
        self.delete_result_for_step("taskctl_start")
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.install_required_results(controller)
        candidate = controller.prepare_review(
            kernel=self.kernel, manifest=self.manifest
        )
        self.delete_result_for_step("taskctl_prepare_review")
        self.assertEqual(
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest),
            candidate,
        )
        controller.review_lease("governance", "governance-reviewer")
        self.delete_result_for_step("taskctl_review_lease")
        controller.review_lease("governance", "governance-reviewer")
        report = self.artifact / "review/governance_axis.md"
        report.write_text(
            "Reviewer-ID: governance-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        reviewer = taskctl.TaskController(
            self.repo,
            self.TASK_ID,
            actor="governance-reviewer",
            implementer="implementer",
        )
        reviewer.review_submit("governance", report)
        self.delete_result_for_step("taskctl_review_submit")
        reviewer.review_submit("governance", report)
        for step in (
            "taskctl_start",
            "taskctl_prepare_review",
            "taskctl_review_lease",
            "taskctl_review_submit",
        ):
            commands = [
                path
                for path in (self.artifact / "events").glob("*.command.json")
                if read_json(path)["step"] == step
            ]
            self.assertEqual(len(commands), 1, step)

    def test_internal_transition_retries_a_durable_oserror_result(self) -> None:
        controller = self.controller()
        with (
            mock.patch.object(taskctl, "legacy_task_pass", return_value=True),
            mock.patch.object(
                controller,
                "_cas_write_state",
                side_effect=OSError(errno.ENOSPC, "full"),
            ),
            self.assertRaisesRegex(taskctl.TaskctlError, "internal transition failed"),
        ):
            controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertFalse((self.artifact / "state.json").exists())
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            recovered = controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(recovered["state"], "IMPLEMENTING")
        commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "taskctl_start"
        ]
        self.assertEqual(len(commands), 2)
        self.assertIsNone(controller.events.first_incomplete())

    def test_prepare_recovers_command_before_effect_without_deadlock(self) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        state = read_json(self.artifact / "state.json")
        candidate = controller._candidate_inputs(
            state, kernel=self.kernel, manifest=self.manifest
        )
        parameters = controller._prepare_parameters(
            self.kernel, self.manifest, candidate, 1
        )
        with self.assertRaises(taskctl.PostEffectCrash):
            controller.events.run(
                step="taskctl_prepare_review",
                argv=parameters,
                cwd=self.repo,
                classification="INTERNAL",
                runner=lambda: (_ for _ in ()).throw(taskctl.PostEffectCrash()),
                replay_safe=True,
            )
        recovered = controller.prepare_review(
            kernel=self.kernel, manifest=self.manifest
        )
        self.assertEqual(recovered, candidate)
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "READY_FOR_REVIEW"
        )
        self.assertIsNone(controller.events.first_incomplete())
        prepare_commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "taskctl_prepare_review"
        ]
        self.assertEqual(len(prepare_commands), 1)

    def test_prepare_recovers_effect_before_invalidating_drifted_candidate(
        self,
    ) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.delete_result_for_step("taskctl_prepare_review")
        lint_log = self.artifact / "outputs/lint.log"
        accepted = lint_log.read_bytes()
        lint_log.write_bytes(accepted + b"drift\n")
        with self.assertRaisesRegex(taskctl.TaskctlError, "candidate changed"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertIsNone(controller.events.first_incomplete())
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "IMPLEMENTING"
        )
        lint_log.write_bytes(accepted)
        controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "READY_FOR_REVIEW"
        )

    def test_review_submit_injects_triple_and_rejects_prefilled_hashes(self) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        candidate = controller.prepare_review(
            kernel=self.kernel, manifest=self.manifest
        )
        controller.review_lease("governance", "governance-reviewer")
        report = self.artifact / "review/governance_axis.md"
        report.write_text(
            f"Reviewed-Candidate-Fingerprint: {candidate['fingerprint']}\n"
            f"Reviewed-Patch-SHA256: {candidate['patch_sha256']}\n"
            f"Reviewed-Governance-Digest: {candidate['governance_digest']}\n"
            "Reviewer-ID: governance-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        reviewer = taskctl.TaskController(
            self.repo,
            self.TASK_ID,
            actor="governance-reviewer",
            implementer="implementer",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "must submit unbound"):
            reviewer.review_submit("governance", report)
        report.write_text(
            "Reviewer-ID: governance-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        reviewer.review_submit("governance", report)
        bound = report.read_text(encoding="utf-8")
        self.assertTrue(
            bound.startswith(
                f"Reviewed-Candidate-Fingerprint: {candidate['fingerprint']}\n"
                f"Reviewed-Patch-SHA256: {candidate['patch_sha256']}\n"
                f"Reviewed-Governance-Digest: {candidate['governance_digest']}\n"
            )
        )

    def test_fresh_review_cycle_rejects_a_prebound_report_from_prior_cycle(
        self,
    ) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        first = controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        controller.review_lease("governance", "governance-reviewer")
        report = self.artifact / "review/governance_axis.md"
        report.write_text(
            "Reviewer-ID: governance-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        reviewer = taskctl.TaskController(
            self.repo,
            self.TASK_ID,
            actor="governance-reviewer",
            implementer="implementer",
        )
        reviewer.review_submit("governance", report)
        self.assertTrue(report.read_text(encoding="utf-8").startswith("Reviewed-"))

        lint_log = self.artifact / "outputs/lint.log"
        accepted = lint_log.read_bytes()
        lint_log.write_bytes(accepted + b"drift\n")
        with self.assertRaisesRegex(taskctl.TaskctlError, "candidate changed"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        lint_log.write_bytes(accepted)
        second = controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertEqual(second, first)
        controller.review_lease("governance", "governance-reviewer")
        with self.assertRaisesRegex(taskctl.TaskctlError, "submit unbound"):
            reviewer.review_submit("governance", report)

    def gvr3_required_commands(self):
        return (
            ("test", taskctl.GVR3_LEGACY_RED_ARGV, "NON_SQLITE"),
            ("shell_check", taskctl.GVR3_SHELL_CHECK_ARGV, "NON_SQLITE"),
            ("format_check", taskctl.GVR3_FORMAT_CHECK_ARGV, "NON_SQLITE"),
            ("lint", taskctl.GVR3_LINT_ARGV, "NON_SQLITE"),
            ("compile", taskctl.GVR3_COMPILE_ARGV, "NON_SQLITE"),
            (
                "frozen_v1",
                (
                    "python3",
                    "scripts/frozen_v1_acceptance.py",
                    "--task-id",
                    self.TASK_ID,
                    "--frozen-root",
                    f"artifacts/{self.TASK_ID}/bootstrap/frozen-v1",
                    "--candidate-root",
                    f"artifacts/{self.TASK_ID}/candidate",
                ),
                "FROZEN_V1",
            ),
            ("diff_check", taskctl.GVR3_DIFF_CHECK_ARGV, "NON_SQLITE"),
            (
                "scope",
                (
                    "python3",
                    "scripts/evidence_scope.py",
                    "finalize",
                    self.TASK_ID,
                ),
                "SCOPE",
            ),
        )

    def install_required_results(
        self,
        controller: taskctl.TaskController,
        *,
        omit: frozenset[str] = frozenset(),
    ) -> None:
        for step, argv, classification in self.gvr3_required_commands():
            if step in omit:
                continue
            if step in {"scope", "frozen_v1"}:
                controller.record(step, list(argv), self.repo)
                continue
            log = self.artifact / "outputs" / f"{step}.log"
            log.write_text("PASS\n", encoding="utf-8")
            controller.events.run(
                step=step,
                argv=list(argv),
                cwd=self.repo,
                classification=classification,
                runner=lambda log=log: {
                    "rc": 0,
                    "log": str(log.relative_to(self.repo)),
                    "executed": True,
                },
            )
        (self.artifact / "summary.md").write_text(
            "# Summary\nStatus: REVIEW\n", encoding="utf-8"
        )

    def test_ordinary_pre_v2_bundle_adopts_prefix_and_full_snapshot_once(self) -> None:
        task_id = "ORDINARY-LEGACY"
        task_file = self.repo / f"tasks/repo/{task_id}.md"
        task_file.write_text(
            f"# {task_id}\n\nStatus: READY\nRisk-Tier: MEDIUM\n"
            f'Closure-Tags: ["evidence"]\nTask-Path: tasks/repo/{task_id}.md\n\n'
            "## Allowed Files\n\n"
            f"- `tasks/repo/{task_id}.md`\n- `work/ordinary.txt`\n"
            f"- `artifacts/{task_id}/**`\n",
            encoding="utf-8",
        )
        artifact = self.repo / "artifacts" / task_id
        (artifact / "git").mkdir(parents=True)
        (artifact / "outputs").mkdir()
        (artifact / "review").mkdir()
        (artifact / "commands.jsonl").write_bytes(b"legacy malformed command\n")
        (artifact / "results.jsonl").write_bytes(b"legacy malformed result\n")
        (artifact / "baseline_allowlist.diff").write_bytes(b"")
        (artifact / "baseline_external_files.txt").write_bytes(b"")
        (artifact / "summary.md").write_text("legacy summary\n", encoding="utf-8")
        (artifact / "git/diff.patch").write_bytes(b"legacy patch\n")
        (artifact / "outputs/legacy.log").write_text("legacy log\n", encoding="utf-8")
        (artifact / "review/legacy.md").write_text("legacy review\n", encoding="utf-8")
        (artifact / "task.json").write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "task_file": f"tasks/repo/{task_id}.md",
                    "allowlist": [
                        f"tasks/repo/{task_id}.md",
                        "work/ordinary.txt",
                    ],
                    "repo_root": str(self.repo.resolve()),
                    "baseline_dirty": True,
                    "init_ts": "20260717T000000",
                }
            ),
            encoding="utf-8",
        )
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        digest, inputs = taskctl.governance_digest(self.repo, self.kernel, manifest)
        contract = taskctl.parse_task_contract(task_file, task_id, self.repo)
        active = (
            manifest,
            digest,
            taskctl.select_modules(manifest, contract),
            inputs,
        )
        controller = taskctl.TaskController(
            self.repo, task_id, actor="lead", implementer="implementer"
        )
        with mock.patch.object(controller, "_active_context", return_value=active):
            controller.start(task_file)
            first_state = (artifact / "state.json").read_bytes()
            controller.start(task_file)
        self.assertEqual((artifact / "state.json").read_bytes(), first_state)
        self.assertTrue(
            (artifact / "commands.jsonl")
            .read_bytes()
            .startswith(b"legacy malformed command\n")
        )
        inventory = read_json(artifact / "legacy-bundle.json")
        paths = {entry["path"] for entry in inventory["entries"]}
        self.assertTrue(
            {
                "task.json",
                "baseline_allowlist.diff",
                "baseline_external_files.txt",
                "commands.jsonl",
                "results.jsonl",
                "summary.md",
                "git/diff.patch",
                "review/legacy.md",
                "outputs/legacy.log",
            }
            <= paths
        )
        self.assertEqual(
            (artifact / "bootstrap/legacy-bundle/summary.md").read_text(
                encoding="utf-8"
            ),
            "legacy summary\n",
        )

    def test_partial_new_v2_start_is_not_misclassified_as_legacy_prefix(self) -> None:
        task_id = "NEW-V2"
        task_file = self.repo / f"tasks/repo/{task_id}.md"
        task_file.write_text(
            f"# {task_id}\n\nStatus: READY\nRisk-Tier: MEDIUM\n"
            f'Closure-Tags: ["evidence"]\nTask-Path: tasks/repo/{task_id}.md\n\n'
            "## Allowed Files\n\n"
            f"- `tasks/repo/{task_id}.md`\n- `work/new-v2.txt`\n"
            f"- `artifacts/{task_id}/**`\n",
            encoding="utf-8",
        )
        controller = taskctl.TaskController(
            self.repo, task_id, actor="lead", implementer="implementer"
        )
        contract = taskctl.parse_task_contract(task_file, task_id, self.repo)
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        digest, inputs = taskctl.governance_digest(self.repo, self.kernel, manifest)
        active = (
            manifest,
            digest,
            taskctl.select_modules(manifest, contract),
            inputs,
        )
        controller.events.fault = Fault(
            "after_create_dir_fsync_command_event",
            RuntimeError("durable start command crash"),
        )
        with (
            mock.patch.object(controller, "_active_context", return_value=active),
            self.assertRaisesRegex(RuntimeError, "durable start command crash"),
        ):
            controller.start(task_file)
        artifact = self.repo / "artifacts" / task_id
        self.assertEqual(len(list((artifact / "events").glob("*.command.json"))), 1)
        for relative in (
            "init-provenance.json",
            "task.json",
            "baseline_allowlist.diff",
            "baseline_external_files.txt",
            "module_selection.json",
            "state.json",
        ):
            self.assertFalse((artifact / relative).exists(), relative)

        intruder = taskctl.TaskController(
            self.repo, task_id, actor="other-lead", implementer="other-implementer"
        )
        with (
            mock.patch.object(intruder, "_active_context", return_value=active),
            self.assertRaisesRegex(taskctl.TaskctlError, "ownership|inputs changed"),
        ):
            intruder.start(task_file)
        controller.events.fault = None
        with mock.patch.object(controller, "_active_context", return_value=active):
            controller.start(task_file)
        self.assertFalse((artifact / "legacy-prefix.json").exists())
        self.assertFalse((artifact / "legacy-bundle.json").exists())
        self.assertEqual(len(list((artifact / "events").glob("*.command.json"))), 1)
        self.assertEqual(len(jsonl(artifact / "commands.jsonl")), 1)

    def test_partial_baseline_pair_is_never_recaptured_after_tree_drift(self) -> None:
        task_id = "NEW-V2-PARTIAL-BASELINE"
        task_file = self.repo / f"tasks/repo/{task_id}.md"
        work = self.repo / "work/new-v2-partial.txt"
        work.parent.mkdir(exist_ok=True)
        work.write_text("before\n", encoding="utf-8")
        task_file.write_text(
            f"# {task_id}\n\nStatus: READY\nRisk-Tier: MEDIUM\n"
            f'Closure-Tags: ["evidence"]\nTask-Path: tasks/repo/{task_id}.md\n\n'
            "## Allowed Files\n\n"
            f"- `tasks/repo/{task_id}.md`\n- `work/new-v2-partial.txt`\n"
            f"- `artifacts/{task_id}/**`\n",
            encoding="utf-8",
        )
        controller = taskctl.TaskController(
            self.repo, task_id, actor="lead", implementer="implementer"
        )
        contract = taskctl.parse_task_contract(task_file, task_id, self.repo)
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        digest, inputs = taskctl.governance_digest(self.repo, self.kernel, manifest)
        active = (
            manifest,
            digest,
            taskctl.select_modules(manifest, contract),
            inputs,
        )
        real_atomic_write = taskctl.atomic_write
        crashed = False

        def crash_before_external(path, content, **kwargs):
            nonlocal crashed
            if path.name == "baseline_external_files.txt" and not crashed:
                crashed = True
                raise RuntimeError("partial baseline crash")
            return real_atomic_write(path, content, **kwargs)

        with (
            mock.patch.object(controller, "_active_context", return_value=active),
            mock.patch.object(
                taskctl, "atomic_write", side_effect=crash_before_external
            ),
            self.assertRaisesRegex(RuntimeError, "partial baseline crash"),
        ):
            controller.start(task_file)
        artifact = self.repo / "artifacts" / task_id
        captured = (artifact / "baseline_allowlist.diff").read_bytes()
        self.assertFalse((artifact / "baseline_external_files.txt").exists())

        work.write_text("after\n", encoding="utf-8")
        with (
            mock.patch.object(controller, "_active_context", return_value=active),
            self.assertRaisesRegex(taskctl.TaskctlError, "inputs changed"),
        ):
            controller.start(task_file)
        self.assertEqual((artifact / "baseline_allowlist.diff").read_bytes(), captured)
        self.assertFalse((artifact / "baseline_external_files.txt").exists())
        self.assertFalse((artifact / "state.json").exists())

    def test_concurrent_start_accepts_only_the_winning_owner(self) -> None:
        task_id = "START-OWNER"
        task_file = self.repo / f"tasks/repo/{task_id}.md"
        task_file.write_text(
            f"# {task_id}\n\nStatus: READY\nRisk-Tier: MEDIUM\n"
            f'Closure-Tags: ["evidence"]\nTask-Path: tasks/repo/{task_id}.md\n\n'
            "## Allowed Files\n\n"
            f"- `tasks/repo/{task_id}.md`\n- `work/start-owner.txt`\n"
            f"- `artifacts/{task_id}/**`\n",
            encoding="utf-8",
        )
        artifact = self.repo / "artifacts" / task_id
        artifact.mkdir(parents=True)
        for name in (
            "baseline_allowlist.diff",
            "baseline_external_files.txt",
            "commands.jsonl",
            "results.jsonl",
        ):
            (artifact / name).write_bytes(b"")
        (artifact / "task.json").write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "task_file": f"tasks/repo/{task_id}.md",
                    "allowlist": [
                        f"tasks/repo/{task_id}.md",
                        "work/start-owner.txt",
                    ],
                    "repo_root": str(self.repo.resolve()),
                    "baseline_dirty": True,
                    "init_ts": "20260717T000000",
                }
            ),
            encoding="utf-8",
        )
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        contract = taskctl.parse_task_contract(task_file, task_id, self.repo)
        digest, inputs = taskctl.governance_digest(self.repo, self.kernel, manifest)
        active = (
            manifest,
            digest,
            taskctl.select_modules(manifest, contract),
            inputs,
        )
        controllers = [
            taskctl.TaskController(
                self.repo, task_id, actor=actor, implementer=f"impl-{actor}"
            )
            for actor in ("A", "B")
        ]
        for controller in controllers:
            controller._active_context = mock.Mock(return_value=active)
        barrier = threading.Barrier(2)
        outcomes: list[tuple[str, str]] = []

        def run(controller: taskctl.TaskController) -> None:
            barrier.wait()
            try:
                state = controller.start(task_file)
            except taskctl.TaskctlError:
                outcomes.append((controller.actor, "REJECTED"))
            else:
                outcomes.append((controller.actor, str(state["controller"])))

        threads = [
            threading.Thread(target=run, args=(controller,))
            for controller in controllers
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        winner = read_json(artifact / "state.json")["controller"]
        loser = ({"A", "B"} - {winner}).pop()
        self.assertCountEqual(outcomes, [(winner, winner), (loser, "REJECTED")])

    def submit_axis(
        self,
        controller: taskctl.TaskController,
        axis: str,
        reviewer: str,
    ) -> None:
        controller.review_lease(axis, reviewer)
        report = self.artifact / "review" / f"{axis}_axis.md"
        report.write_text(
            f"Reviewer-ID: {reviewer}\nVerdict: APPROVED\nP0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        reviewer_controller = taskctl.TaskController(
            self.repo,
            self.TASK_ID,
            actor=reviewer,
            implementer="implementer",
        )
        reviewer_controller.review_submit(axis, report)

    def ready_candidate(self) -> taskctl.TaskController:
        controller = self.bootstrap()
        self.install_required_results(controller)
        controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.submit_axis(controller, "governance", "governance-reviewer")
        self.submit_axis(controller, "tooling", "tooling-reviewer")
        return controller

    def test_prepare_review_requires_results_and_gvr3_candidate_pair(self) -> None:
        controller = self.bootstrap()
        with self.assertRaises(taskctl.TaskctlError):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.install_required_results(controller)
        with self.assertRaises(taskctl.TaskctlError):
            controller.prepare_review(kernel=self.kernel)
        candidate = controller.prepare_review(
            kernel=self.kernel, manifest=self.manifest
        )
        self.assertRegex(candidate["fingerprint"], r"^[0-9a-f]{64}$")
        self.assertEqual(
            set(candidate["required_results"]),
            {step for step, _argv, _classification in self.gvr3_required_commands()},
        )
        virtual_patch = self.artifact / "candidate/virtual.patch"
        self.assertTrue(virtual_patch.is_file())
        self.assertEqual(
            hashlib.sha256(virtual_patch.read_bytes()).hexdigest(),
            candidate["patch_sha256"],
        )
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "READY_FOR_REVIEW"
        )

    def test_changed_source_invalidates_candidate_and_allows_fresh_virtual_patch(
        self,
    ) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        first = controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        virtual_path = self.artifact / "candidate/virtual.patch"
        first_virtual = virtual_path.read_bytes()
        runner = self.repo / "scripts/frozen_v1_acceptance.py"
        runner.write_text(
            runner.read_text(encoding="utf-8") + "# changed\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "scoped patch"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "IMPLEMENTING"
        )
        controller.record(
            "scope",
            ["python3", "scripts/evidence_scope.py", "finalize", self.TASK_ID],
            self.repo,
        )
        second = controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertNotEqual(second["fingerprint"], first["fingerprint"])
        self.assertNotEqual(virtual_path.read_bytes(), first_virtual)

    def test_completed_prepare_reexecutes_when_its_durable_effect_was_removed(
        self,
    ) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        first = controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        lint_log = self.artifact / "outputs/lint.log"
        accepted = lint_log.read_bytes()
        lint_log.write_bytes(accepted + b"changed\n")
        with self.assertRaisesRegex(taskctl.TaskctlError, "candidate changed"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "IMPLEMENTING"
        )
        lint_log.write_bytes(accepted)
        second = controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertEqual(second, first)
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "READY_FOR_REVIEW"
        )
        prepare_commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "taskctl_prepare_review"
        ]
        self.assertEqual(len(prepare_commands), 2)

    def test_review_axes_require_distinct_non_implementer_identities(self) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        with self.assertRaises(taskctl.TaskctlError):
            controller.review_lease("governance", "implementer")
        for reviewer in ("", "none", " NONE ", "reviewer\x00bad"):
            with (
                self.subTest(reviewer=reviewer),
                self.assertRaises(taskctl.TaskctlError),
            ):
                controller.review_lease("governance", reviewer)
        controller.review_lease("governance", "same")
        with self.assertRaises(taskctl.TaskctlError):
            controller.review_lease("tooling", "same")

    def test_concurrent_review_leases_leave_no_orphan_command(self) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        controllers = [self.controller(), self.controller()]
        barrier = threading.Barrier(2)
        outcomes: list[str] = []

        def lease(owner: taskctl.TaskController, reviewer: str) -> None:
            barrier.wait()
            try:
                owner.review_lease("governance", reviewer)
            except taskctl.TaskctlError:
                outcomes.append("REJECTED")
            else:
                outcomes.append(reviewer)

        threads = [
            threading.Thread(target=lease, args=(controllers[0], "reviewer-1")),
            threading.Thread(target=lease, args=(controllers[1], "reviewer-2")),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(outcomes.count("REJECTED"), 1)
        self.assertIsNone(controller.events.first_incomplete())
        commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "taskctl_review_lease"
        ]
        self.assertEqual(len(commands), 1)

    def assert_mutator_rechecks_state_after_prepare(
        self,
        *,
        step: str,
        operation: Callable[[taskctl.TaskController], object],
    ) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        prepare_controller = self.controller()
        prepare_entered = threading.Event()
        release_prepare = threading.Event()
        original_candidate_inputs = prepare_controller._candidate_inputs

        def blocking_candidate_inputs(state, **kwargs):
            prepare_entered.set()
            if not release_prepare.wait(5):
                raise RuntimeError("prepare race was not released")
            return original_candidate_inputs(state, **kwargs)

        prepare_controller._candidate_inputs = blocking_candidate_inputs
        prepare_errors: list[Exception] = []

        def prepare() -> None:
            try:
                prepare_controller.prepare_review(
                    kernel=self.kernel, manifest=self.manifest
                )
            except Exception as exc:
                prepare_errors.append(exc)

        prepare_thread = threading.Thread(target=prepare)
        prepare_thread.start()
        self.assertTrue(prepare_entered.wait(2))

        mutator = self.controller()
        state_read = threading.Event()
        original_state = mutator._state

        def observed_state():
            state_read.set()
            return original_state()

        mutator._state = observed_state
        mutator_errors: list[Exception] = []

        def mutate() -> None:
            try:
                operation(mutator)
            except Exception as exc:
                mutator_errors.append(exc)

        before_commands = len(
            [
                path
                for path in (self.artifact / "events").glob("*.command.json")
                if read_json(path)["step"] == step
            ]
        )
        before_outputs = {path.name for path in (self.artifact / "outputs").iterdir()}
        mutator_thread = threading.Thread(target=mutate)
        mutator_thread.start()
        state_read_before_release = state_read.wait(0.5)
        release_prepare.set()
        prepare_thread.join(5)
        mutator_thread.join(5)

        self.assertFalse(prepare_thread.is_alive())
        self.assertFalse(mutator_thread.is_alive())
        self.assertFalse(prepare_errors)
        self.assertFalse(state_read_before_release)
        self.assertEqual(len(mutator_errors), 1)
        self.assertIsInstance(mutator_errors[0], taskctl.TaskctlError)
        self.assertIn("IMPLEMENTING", str(mutator_errors[0]))
        after_commands = len(
            [
                path
                for path in (self.artifact / "events").glob("*.command.json")
                if read_json(path)["step"] == step
            ]
        )
        self.assertEqual(after_commands, before_commands)
        self.assertEqual(
            {path.name for path in (self.artifact / "outputs").iterdir()},
            before_outputs,
        )

    def test_record_rechecks_state_after_concurrent_prepare_freezes(self) -> None:
        self.assert_mutator_rechecks_state_after_prepare(
            step="post_freeze",
            operation=lambda controller: controller.record(
                "post_freeze",
                [sys.executable, "-c", "raise SystemExit(0)"],
                self.repo,
            ),
        )

    def test_backend_rechecks_state_after_concurrent_prepare_freezes(self) -> None:
        self.assert_mutator_rechecks_state_after_prepare(
            step="test",
            operation=lambda controller: controller.backend_test(
                "test", ["tests/test_after_freeze.py"]
            ),
        )

    def test_governance_adopt_updates_digest_without_recapturing_baseline(self) -> None:
        controller = self.bootstrap()
        module = self.repo / "docs/agents/evidence.md"
        module.write_text(
            module.read_text(encoding="utf-8") + "\nchanged for adoption\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        change = read_json(self.artifact / "governance_change.json")
        baseline_before = (self.artifact / "baseline_allowlist.diff").read_bytes()
        approval = self.artifact / "governance_adoption.md"
        approval.write_text(
            f"Reviewed-Change-SHA256: {change['change_sha256']}\nReviewer-ID: governance-reviewer\n"
            "Verdict: APPROVED\nP0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        controller.governance_adopt(approval)
        self.delete_result_for_step("taskctl_governance_adopt")
        controller.governance_adopt(approval)
        self.assertEqual(
            (self.artifact / "baseline_allowlist.diff").read_bytes(), baseline_before
        )
        adopted = read_json(self.artifact / "state.json")
        self.assertEqual(adopted["state"], "IMPLEMENTING")
        self.assertEqual(adopted["governance_digest"], change["new"])

        module.write_text(
            module.read_text(encoding="utf-8") + "\nsecond adoption change\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        second_change = read_json(self.artifact / "governance_change.json")
        self.assertNotEqual(second_change["change_sha256"], change["change_sha256"])
        self.assertNotIn("governance_adoption", read_json(self.artifact / "state.json"))
        approval.write_text(
            f"Reviewed-Change-SHA256: {second_change['change_sha256']}\n"
            "Reviewer-ID: governance-reviewer-2\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        controller.governance_adopt(approval)
        self.assertEqual(
            read_json(self.artifact / "state.json")["governance_digest"],
            second_change["new"],
        )
        approval.unlink()
        with self.assertRaisesRegex(taskctl.TaskctlError, "approval"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)

    def test_second_governance_change_recovers_state_first_crash(self) -> None:
        controller = self.bootstrap()
        module = self.repo / "docs/agents/evidence.md"
        approval = self.artifact / "governance_adoption.md"

        module.write_text(
            module.read_text(encoding="utf-8") + "\nfirst adoption change\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        first_change = read_json(self.artifact / "governance_change.json")
        approval.write_text(
            f"Reviewed-Change-SHA256: {first_change['change_sha256']}\n"
            "Reviewer-ID: governance-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        controller.governance_adopt(approval)
        first_report = (self.artifact / "governance_change.json").read_bytes()

        module.write_text(
            module.read_text(encoding="utf-8") + "\nsecond adoption change\n",
            encoding="utf-8",
        )
        controller.fault = Fault(
            "after_governance_change_state", RuntimeError("state-first crash")
        )
        with self.assertRaisesRegex(RuntimeError, "state-first crash"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        blocked = read_json(self.artifact / "state.json")
        second_change = blocked["governance_change"]
        self.assertNotIn("governance_adoption", blocked)
        self.assertEqual(
            blocked["governance_change_report_pending"],
            taskctl.sha256_bytes(taskctl.canonical_json(second_change)),
        )
        self.assertEqual(
            (self.artifact / "governance_change.json").read_bytes(), first_report
        )

        controller.fault = None
        state_before_tamper = (self.artifact / "state.json").read_bytes()
        tampered_report = b'{"tampered":true}\n'
        (self.artifact / "governance_change.json").write_bytes(tampered_report)
        with self.assertRaisesRegex(taskctl.TaskctlError, "recoverable authority"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertEqual(
            (self.artifact / "governance_change.json").read_bytes(),
            tampered_report,
        )
        self.assertEqual(
            (self.artifact / "state.json").read_bytes(), state_before_tamper
        )
        self.assertIsNotNone(controller.events.first_incomplete())
        (self.artifact / "governance_change.json").write_bytes(first_report)

        approval.write_text(
            f"Reviewed-Change-SHA256: {second_change['change_sha256']}\n"
            "Reviewer-ID: governance-reviewer-2\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.governance_adopt(approval)
        self.assertIsNone(controller.events.first_incomplete())
        governance_commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "taskctl_governance_change"
        ]
        self.assertEqual(len(governance_commands), 2)
        controller.governance_adopt(approval)
        adopted = read_json(self.artifact / "state.json")
        self.assertEqual(adopted["state"], "IMPLEMENTING")
        self.assertEqual(adopted["governance_digest"], second_change["new"])
        self.assertNotIn("governance_change_report_pending", adopted)
        self.assertEqual(
            (self.artifact / "governance_change.json").read_bytes(),
            taskctl.canonical_json(second_change),
        )

    def test_pending_governance_change_recovers_before_observing_newer_drift(
        self,
    ) -> None:
        controller = self.bootstrap()
        module = self.repo / "docs/agents/evidence.md"
        approval = self.artifact / "governance_adoption.md"

        module.write_text(
            module.read_text(encoding="utf-8") + "\naccepted change A\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        change_a = read_json(self.artifact / "governance_change.json")
        approval.write_text(
            f"Reviewed-Change-SHA256: {change_a['change_sha256']}\n"
            "Reviewer-ID: governance-reviewer-a\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        controller.governance_adopt(approval)

        module.write_text(
            module.read_text(encoding="utf-8") + "\npending change B\n",
            encoding="utf-8",
        )
        controller.fault = Fault(
            "after_governance_change_state", RuntimeError("change B crash")
        )
        with self.assertRaisesRegex(RuntimeError, "change B crash"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        pending_b = read_json(self.artifact / "state.json")["governance_change"]

        module.write_text(
            module.read_text(encoding="utf-8") + "\nnewer change C\n",
            encoding="utf-8",
        )
        controller.fault = None
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        recovered_b = read_json(self.artifact / "state.json")
        self.assertEqual(recovered_b["governance_change"], pending_b)
        self.assertNotIn("governance_change_report_pending", recovered_b)
        self.assertEqual(
            (self.artifact / "governance_change.json").read_bytes(),
            taskctl.canonical_json(pending_b),
        )
        self.assertIsNone(controller.events.first_incomplete())

        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        change_c = read_json(self.artifact / "governance_change.json")
        self.assertNotEqual(change_c["change_sha256"], pending_b["change_sha256"])
        approval.write_text(
            f"Reviewed-Change-SHA256: {change_c['change_sha256']}\n"
            "Reviewer-ID: governance-reviewer-c\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        controller.governance_adopt(approval)
        self.assertEqual(
            read_json(self.artifact / "state.json")["governance_digest"],
            change_c["new"],
        )

    def test_pre_effect_governance_command_replays_or_supersedes_safely(
        self,
    ) -> None:
        for index, live_state in enumerate(("same", "newer", "reverted")):
            with self.subTest(live_state=live_state):
                if index:
                    self.tearDown()
                    self.setUp()
                controller = self.bootstrap()
                module = self.repo / "docs/agents/evidence.md"
                original = module.read_bytes()
                module.write_text(
                    module.read_text(encoding="utf-8") + "\nchange B\n",
                    encoding="utf-8",
                )
                controller.events.fault = Fault(
                    "after_create_dir_fsync_command_event",
                    RuntimeError("pre-effect command crash"),
                )
                with self.assertRaisesRegex(RuntimeError, "pre-effect command crash"):
                    controller.prepare_review(
                        kernel=self.kernel, manifest=self.manifest
                    )
                self.assertNotIn(
                    "governance_change", read_json(self.artifact / "state.json")
                )
                self.assertIsNotNone(controller.events.first_incomplete())

                if live_state == "newer":
                    module.write_text(
                        module.read_text(encoding="utf-8") + "\nchange C\n",
                        encoding="utf-8",
                    )
                elif live_state == "reverted":
                    module.write_bytes(original)
                controller.events.fault = None
                if live_state == "reverted":
                    with self.assertRaises(taskctl.TaskctlError):
                        controller.prepare_review(
                            kernel=self.kernel, manifest=self.manifest
                        )
                else:
                    with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
                        controller.prepare_review(
                            kernel=self.kernel, manifest=self.manifest
                        )
                self.assertIsNone(controller.events.first_incomplete())
                commands = sorted(
                    [
                        path
                        for path in (self.artifact / "events").glob("*.command.json")
                        if read_json(path)["step"] == "taskctl_governance_change"
                    ]
                )
                self.assertEqual(len(commands), 2 if live_state == "newer" else 1)
                results = [
                    read_json(
                        self.artifact
                        / "events"
                        / path.name.replace("command", "result")
                    )
                    for path in commands
                ]
                self.assertEqual(
                    [result["rc"] for result in results],
                    (
                        [125, 0]
                        if live_state == "newer"
                        else ([125] if live_state == "reverted" else [0])
                    ),
                )
                if live_state in {"newer", "reverted"}:
                    self.assertEqual(
                        results[0]["reason"],
                        (
                            "governance_reverted_before_effect"
                            if live_state == "reverted"
                            else "governance_changed_before_effect"
                        ),
                    )

    def test_governance_adopt_rejects_invalid_or_non_controller_approval(self) -> None:
        controller = self.bootstrap()
        module = self.repo / "docs/agents/evidence.md"
        module.write_text(
            module.read_text(encoding="utf-8") + "\nchanged for adoption\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        change = read_json(self.artifact / "governance_change.json")
        approval = self.artifact / "governance_adoption.md"
        valid = (
            f"Reviewed-Change-SHA256: {change['change_sha256']}\n"
            "Reviewer-ID: governance-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n"
        )
        invalid = (
            valid.replace("Reviewer-ID: governance-reviewer", "Reviewer-ID:"),
            valid.replace("governance-reviewer", "none"),
            valid.replace("governance-reviewer", "implementer"),
            valid.replace(str(change["change_sha256"]), "0" * 64),
            valid.replace("P1: 0", "P1: 1"),
            valid + "Review history: CHANGES_REQUESTED\n",
        )
        for content in invalid:
            with self.subTest(content=content[-48:]):
                approval.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(taskctl.TaskctlError, "approval"):
                    controller.governance_adopt(approval)

        approval.write_text(valid, encoding="utf-8")
        outsider = taskctl.TaskController(
            self.repo,
            self.TASK_ID,
            actor="not-controller",
            implementer="implementer",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "recorded controller"):
            outsider.governance_adopt(approval)

    def test_governance_adopt_binds_the_exact_parsed_approval_bytes(self) -> None:
        controller = self.bootstrap()
        module = self.repo / "docs/agents/evidence.md"
        module.write_text(
            module.read_text(encoding="utf-8") + "\nchanged for adoption\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        change = read_json(self.artifact / "governance_change.json")
        approval = self.artifact / "governance_adoption.md"
        approval.write_text(
            f"Reviewed-Change-SHA256: {change['change_sha256']}\n"
            "Reviewer-ID: governance-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )
        original_parse = taskctl._parse_fields_text

        def parse_then_replace(text: str, fields) -> dict[str, str]:
            parsed = original_parse(text, fields)
            approval.write_text(
                text.replace("Verdict: APPROVED", "Verdict: CHANGES_REQUESTED"),
                encoding="utf-8",
            )
            return parsed

        with mock.patch.object(
            taskctl, "_parse_fields_text", side_effect=parse_then_replace
        ):
            with self.assertRaisesRegex(taskctl.TaskctlError, "approval.*changed"):
                controller.governance_adopt(approval)
        state = read_json(self.artifact / "state.json")
        self.assertEqual(state["state"], "BLOCKED")
        self.assertNotIn("governance_adoption", state)

    def test_governance_adopt_rejects_tampered_change_report_or_digest(self) -> None:
        controller = self.bootstrap()
        module = self.repo / "docs/agents/evidence.md"
        module.write_text(
            module.read_text(encoding="utf-8") + "\nchanged for adoption\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        state_path = self.artifact / "state.json"
        change_path = self.artifact / "governance_change.json"
        accepted_state = state_path.read_bytes()
        accepted_change = change_path.read_bytes()
        change = read_json(change_path)
        approval = self.artifact / "governance_adoption.md"
        approval.write_text(
            f"Reviewed-Change-SHA256: {change['change_sha256']}\n"
            "Reviewer-ID: governance-reviewer\nVerdict: APPROVED\n"
            "P0: 0\nP1: 0\nP2: 0\n",
            encoding="utf-8",
        )

        tampered = copy.deepcopy(change)
        tampered["closure_impact"]["risk_tier"] = "LOW"
        change_path.write_bytes(taskctl.canonical_json(tampered))
        with self.assertRaisesRegex(taskctl.TaskctlError, "change report"):
            controller.governance_adopt(approval)

        blocked = read_json(state_path)
        blocked["governance_change"] = tampered
        state_path.write_bytes(taskctl.canonical_json(blocked))
        with self.assertRaisesRegex(taskctl.TaskctlError, "change digest"):
            controller.governance_adopt(approval)
        state_path.write_bytes(accepted_state)
        change_path.write_bytes(accepted_change)

    def test_governance_digest_change_blocks_and_preserves_baseline(self) -> None:
        controller = self.bootstrap()
        baseline_before = (self.artifact / "baseline_allowlist.diff").read_bytes()
        module = self.repo / "docs/agents/evidence.md"
        module.write_text(
            module.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "adoption"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        blocked = read_json(self.artifact / "state.json")
        self.assertEqual(blocked["state"], "BLOCKED")
        self.assertEqual(blocked["reason"], "GOVERNANCE_DIGEST_MISMATCH")
        change = read_json(self.artifact / "governance_change.json")
        self.assertIn("docs/agents/evidence.md", change["changed_inputs"])
        self.assertIn("GOV-EVIDENCE-001", change["changed_rules"])
        self.assertEqual(change["baseline_identity"], blocked["baseline"])
        self.assertIn(
            "docs/agents/evidence.md",
            change["closure_impact"]["changed_selected_inputs"],
        )
        self.assertEqual(
            (self.artifact / "baseline_allowlist.diff").read_bytes(), baseline_before
        )

    def test_activation_crash_points_recover_without_missing_or_duplicate(self) -> None:
        points = (
            "before_root_write",
            "after_root_write",
            "before_root_file_fsync",
            "after_root_file_fsync",
            "before_root_replace",
            "after_root_replace",
            "before_root_dir_fsync",
            "after_root_dir_fsync",
            "before_root_staged_validation",
            "after_root_staged_validation",
            "before_manifest_write",
            "after_manifest_write",
            "before_manifest_file_fsync",
            "after_manifest_file_fsync",
            "before_manifest_replace",
            "after_manifest_replace",
            "before_manifest_dir_fsync",
            "after_manifest_dir_fsync",
            "before_actual_hash_verification",
            "after_actual_hash_verification",
        )
        for index, point in enumerate(points):
            with self.subTest(point=point):
                if index:
                    self.tearDown()
                    self.setUp()
                active_root = self.repo / "AGENTS.md"
                active_manifest = self.repo / "docs/agents/manifest.json"
                pre_root = active_root.read_bytes()
                pre_manifest = (
                    active_manifest.read_bytes() if active_manifest.exists() else None
                )
                candidate_root = self.kernel.read_bytes()
                candidate_manifest = self.manifest.read_bytes()
                controller = self.ready_candidate()
                controller.fault = Fault(point, RuntimeError(point))
                with self.assertRaises(RuntimeError):
                    controller.activate(self.kernel, self.manifest)
                state = read_json(self.artifact / "state.json")
                self.assertNotEqual(state["state"], "PASS")
                self.assertTrue(active_root.is_file())
                self.assertIn(active_root.read_bytes(), {pre_root, candidate_root})
                if active_manifest.exists():
                    self.assertIn(
                        active_manifest.read_bytes(),
                        {pre_manifest, candidate_manifest},
                    )
                    if active_manifest.read_bytes() == candidate_manifest:
                        self.assertEqual(active_root.read_bytes(), candidate_root)
                else:
                    self.assertIsNone(pre_manifest)

                controller.fault = None
                controller.activate(self.kernel, self.manifest)
                self.assertEqual(
                    read_json(self.artifact / "state.json")["state"],
                    "GOVERNANCE_STAGED",
                )
                self.assertEqual(active_root.read_bytes(), candidate_root)
                self.assertEqual(active_manifest.read_bytes(), candidate_manifest)
                commands = [
                    path
                    for path in (self.artifact / "events").glob("*.command.json")
                    if read_json(path)["step"] == "taskctl_activate"
                ]
                self.assertEqual(len(commands), 1)

    def test_root_first_stage_rejects_missing_matching_and_mismatched_manifest(
        self,
    ) -> None:
        controller = self.ready_candidate()
        controller.fault = Fault(
            "before_manifest_write", RuntimeError("inspect root-first stage")
        )
        with self.assertRaises(RuntimeError):
            controller.activate(self.kernel, self.manifest)
        self.assertEqual(
            (self.repo / "AGENTS.md").read_bytes(), self.kernel.read_bytes()
        )
        contract = controller._contract()
        with self.assertRaises(taskctl.TaskctlError):
            controller._active_context(contract)

        active_manifest = self.repo / "docs/agents/manifest.json"
        active_manifest.write_bytes(self.manifest.read_bytes())
        with self.assertRaisesRegex(taskctl.TaskctlError, "staged"):
            controller._active_context(contract)

        mismatched = json.loads(self.manifest.read_text(encoding="utf-8"))
        mismatched["adapter_version"] = "0.0.0"
        active_manifest.write_text(json.dumps(mismatched), encoding="utf-8")
        with self.assertRaisesRegex(taskctl.TaskctlError, "mismatch"):
            controller._active_context(contract)

    def assert_activation_retry(self, crash_point: str) -> None:
        controller = self.ready_candidate()
        controller.fault = Fault(crash_point, RuntimeError(crash_point))
        with self.assertRaises(RuntimeError):
            controller.activate(self.kernel, self.manifest)
        self.assertNotEqual(read_json(self.artifact / "state.json")["state"], "PASS")
        controller.fault = None
        controller.activate(self.kernel, self.manifest)
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "GOVERNANCE_STAGED"
        )
        commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "taskctl_activate"
        ]
        self.assertEqual(len(commands), 1)

    def test_activation_retry_after_root_replace_reuses_same_ordinal(self) -> None:
        self.assert_activation_retry("after_root_replace")

    def test_activation_retry_after_manifest_replace_reuses_same_ordinal(self) -> None:
        self.assert_activation_retry("after_manifest_replace")

    def test_close_orders_review_task_atomic_and_pass_last_with_retry(self) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        order: list[str] = []
        gate_argv: dict[str, list[str]] = {}

        def fail_atomic(step: str, argv: list[str]) -> dict[str, object]:
            order.append(step)
            gate_argv[step] = argv
            return {"rc": 7 if step == "atomic_evidence" else 0, "executed": True}

        with self.assertRaises(taskctl.TaskctlError):
            controller.close(gate_runner=fail_atomic)
        self.assertEqual(order, ["independent_review", "task_gate", "atomic_evidence"])
        self.assertEqual(
            gate_argv["task_gate"],
            ["./scripts/task_validate.sh", self.TASK_ID],
        )
        self.assertEqual(
            gate_argv["atomic_evidence"],
            [
                "python3",
                "scripts/atomic_evidence_validate.py",
                self.TASK_ID,
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
        )
        self.assertEqual(read_json(self.artifact / "state.json")["state"], "FAIL")

        def pass_gate(step: str, _argv: list[str]) -> dict[str, object]:
            order.append(step)
            return {"rc": 0, "executed": True}

        controller.close(gate_runner=pass_gate)
        self.assertEqual(read_json(self.artifact / "state.json")["state"], "PASS")
        before = len(list((self.artifact / "events").glob("*.command.json")))
        controller.close(gate_runner=pass_gate)
        after = len(list((self.artifact / "events").glob("*.command.json")))
        self.assertEqual(before, after)
        candidate = read_json(self.artifact / "state.json")["candidate"]
        for event_path in (self.artifact / "events").glob("*.command.json"):
            event = read_json(event_path)
            if event["step"] in {
                "independent_review",
                "task_gate",
                "atomic_evidence",
            }:
                self.assertIn(candidate["fingerprint"], event["argv"])
                self.assertIn(candidate["patch_sha256"], event["argv"])
                self.assertIn(candidate["governance_digest"], event["argv"])

    def test_close_revalidates_all_reviewed_bytes_after_gate_chain(self) -> None:
        for index, drift in enumerate(
            ("summary", "source", "review", "installed_governance")
        ):
            with self.subTest(drift=drift):
                if index:
                    self.tearDown()
                    self.setUp()
                controller = self.ready_candidate()
                controller.activate(self.kernel, self.manifest)
                changed = False

                def mutate_after_atomic(
                    step: str, _argv: list[str]
                ) -> dict[str, object]:
                    nonlocal changed
                    if step == "atomic_evidence" and not changed:
                        changed = True
                        paths = {
                            "summary": self.artifact / "summary.md",
                            "source": self.repo / "scripts/frozen_v1_acceptance.py",
                            "review": self.artifact / "review/governance_axis.md",
                            "installed_governance": self.repo / "AGENTS.md",
                        }
                        path = paths[drift]
                        path.write_text(
                            path.read_text(encoding="utf-8") + "\npost-gate drift\n",
                            encoding="utf-8",
                        )
                    return {"rc": 0, "executed": True}

                with self.assertRaises(taskctl.TaskctlError):
                    controller.close(gate_runner=mutate_after_atomic)
                self.assertNotEqual(
                    read_json(self.artifact / "state.json")["state"], "PASS"
                )

    def test_active_pass_binding_rejects_governance_byte_drift(self) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        controller.close(gate_runner=lambda _step, _argv: {"rc": 0, "executed": True})
        contract = controller._contract()
        controller._active_context(contract)

        paths = (
            self.repo / "AGENTS.md",
            self.repo / "docs/agents/manifest.json",
            self.repo / "docs/agents/evidence.md",
        )
        for path in paths:
            with self.subTest(path=path.relative_to(self.repo)):
                accepted = path.read_bytes()
                path.write_bytes(accepted + b"\n")
                try:
                    with self.assertRaisesRegex(
                        taskctl.TaskctlError, "active governance differs"
                    ):
                        controller._active_context(contract)
                finally:
                    path.write_bytes(accepted)

    def test_non_controller_cannot_activate_or_close(self) -> None:
        controller = self.ready_candidate()
        outsider = taskctl.TaskController(
            self.repo,
            self.TASK_ID,
            actor="not-the-controller",
            implementer="implementer",
        )
        with self.assertRaisesRegex(taskctl.TaskctlError, "recorded controller"):
            outsider.activate(self.kernel, self.manifest)
        controller.activate(self.kernel, self.manifest)
        with self.assertRaisesRegex(taskctl.TaskctlError, "recorded controller"):
            outsider.close(gate_runner=lambda _step, _argv: {"rc": 0, "executed": True})
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "GOVERNANCE_STAGED"
        )

    def test_non_controller_cannot_record_test_or_prepare_review(self) -> None:
        self.bootstrap()
        outsider = taskctl.TaskController(
            self.repo,
            self.TASK_ID,
            actor="not-the-controller",
            implementer="not-the-controller",
        )
        before = len(list((self.artifact / "events").glob("*.command.json")))
        with self.assertRaisesRegex(taskctl.TaskctlError, "recorded controller"):
            outsider.record("lint", ["git", "status", "--porcelain=v1"], self.repo)
        with self.assertRaisesRegex(taskctl.TaskctlError, "recorded controller"):
            outsider.backend_test("test", ["tests/test_any.py"])
        with self.assertRaisesRegex(taskctl.TaskctlError, "recorded controller"):
            outsider.prepare_review(kernel=self.kernel, manifest=self.manifest)
        self.assertEqual(
            len(list((self.artifact / "events").glob("*.command.json"))), before
        )

    def test_doctor_reports_known_failed_ordinal_and_resume_step(self) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        with self.assertRaises(taskctl.TaskctlError):
            controller.close(
                gate_runner=lambda step, _argv: {
                    "rc": 9 if step == "task_gate" else 0,
                    "executed": True,
                }
            )
        report = controller.doctor()
        self.assertEqual(report["live_state"], "KNOWN_FAILURE")
        self.assertIsInstance(report["failed_ordinal"], int)
        self.assertEqual(report["first_problem_ordinal"], report["failed_ordinal"])
        self.assertEqual(report["resume_from"], "task_gate")

    def test_activation_result_loss_recovers_without_reinstalling_or_new_ordinal(
        self,
    ) -> None:
        controller = self.ready_candidate()
        controller.fault = Fault(
            "after_activation_state_before_result",
            RuntimeError("lost activation result"),
        )
        with self.assertRaises(RuntimeError):
            controller.activate(self.kernel, self.manifest)
        self.assertEqual(
            read_json(self.artifact / "state.json")["state"], "GOVERNANCE_STAGED"
        )
        activate_commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "taskctl_activate"
        ]
        self.assertEqual(len(activate_commands), 1)
        ordinal = activate_commands[0].name.split(".", 1)[0]
        self.assertFalse((self.artifact / "events" / f"{ordinal}.result.json").exists())
        root_hash = hashlib.sha256((self.repo / "AGENTS.md").read_bytes()).hexdigest()
        controller.fault = None
        controller.activate(self.kernel, self.manifest)
        self.assertTrue((self.artifact / "events" / f"{ordinal}.result.json").is_file())
        self.assertEqual(
            hashlib.sha256((self.repo / "AGENTS.md").read_bytes()).hexdigest(),
            root_hash,
        )

    def test_pass_receipt_crash_reuses_durable_gates_and_passes_on_retry(self) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        calls: list[str] = []

        def pass_gate(step: str, _argv: list[str]) -> dict[str, object]:
            calls.append(step)
            return {"rc": 0, "executed": True}

        controller.fault = Fault("before_pass_receipt", RuntimeError("receipt crash"))
        with self.assertRaises(RuntimeError):
            controller.close(gate_runner=pass_gate)
        self.assertEqual(read_json(self.artifact / "state.json")["state"], "CLOSING")
        first_calls = list(calls)
        controller.fault = None
        controller.close(gate_runner=pass_gate)
        self.assertEqual(read_json(self.artifact / "state.json")["state"], "PASS")
        self.assertEqual(calls, first_calls)

    def test_scope_refresh_failure_is_known_and_retryable(self) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        real_run = subprocess.run

        def fail_scope(argv, *args, **kwargs):
            if list(argv[:3]) == [
                "python3",
                "scripts/evidence_scope.py",
                "finalize",
            ]:
                return subprocess.CompletedProcess(argv, 7)
            return real_run(argv, *args, **kwargs)

        with mock.patch.object(taskctl.subprocess, "run", side_effect=fail_scope):
            with self.assertRaisesRegex(
                taskctl.TaskctlError, "canonical scope refresh failed"
            ):
                controller.close(
                    gate_runner=lambda _step, _argv: {"rc": 0, "executed": True}
                )
        failed = read_json(self.artifact / "state.json")
        self.assertEqual(failed["state"], "FAIL")
        self.assertEqual(failed["resume_from"], "taskctl_scope_refresh")
        self.assertIsInstance(failed["failed_ordinal"], int)
        doctor = controller.doctor()
        self.assertEqual(doctor["live_state"], "KNOWN_FAILURE")
        self.assertEqual(doctor["resume_from"], "taskctl_scope_refresh")

        recovered = controller.close(
            gate_runner=lambda _step, _argv: {"rc": 0, "executed": True}
        )
        self.assertEqual(recovered["state"], "PASS")
        refresh_commands = [
            path
            for path in (self.artifact / "events").glob("*.command.json")
            if read_json(path)["step"] == "taskctl_scope_refresh"
        ]
        self.assertEqual(len(refresh_commands), 2)

    def test_close_recovers_exact_incomplete_gate_without_reusing_earlier_steps(
        self,
    ) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        calls: list[str] = []

        def crash_task_gate(step: str, _argv: list[str]) -> dict[str, object]:
            calls.append(step)
            if step == "task_gate":
                raise taskctl.PostEffectCrash("lost task gate result")
            return {"rc": 0, "executed": True}

        with self.assertRaises(taskctl.PostEffectCrash):
            controller.close(gate_runner=crash_task_gate)
        incomplete = controller.events.first_incomplete()
        self.assertIsNotNone(incomplete)
        self.assertEqual(
            controller.events._load_event(incomplete, "command")["step"], "task_gate"
        )
        earlier_calls = list(calls)

        def recover(step: str, _argv: list[str]) -> dict[str, object]:
            calls.append(step)
            return {"rc": 0, "executed": True}

        controller.close(gate_runner=recover)
        self.assertEqual(read_json(self.artifact / "state.json")["state"], "PASS")
        self.assertEqual(earlier_calls.count("independent_review"), 1)
        self.assertEqual(calls.count("independent_review"), 1)

    def test_after_pass_receipt_crash_is_durable_and_idempotent(self) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        controller.fault = Fault("after_pass_receipt", RuntimeError("transport loss"))
        with self.assertRaises(RuntimeError):
            controller.close(
                gate_runner=lambda _step, _argv: {"rc": 0, "executed": True}
            )
        self.assertEqual(read_json(self.artifact / "state.json")["state"], "PASS")
        controller.fault = None
        controller.close(
            gate_runner=lambda _step, _argv: (_ for _ in ()).throw(
                AssertionError("durable PASS must not rerun gates")
            )
        )

    def test_gvr3_pass_retry_rejects_installed_governance_drift(self) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        controller.close(gate_runner=lambda _step, _argv: {"rc": 0, "executed": True})
        paths = (
            self.repo / "AGENTS.md",
            self.repo / "docs/agents/manifest.json",
            self.repo / "docs/agents/evidence.md",
        )
        for path in paths:
            with self.subTest(path=path.relative_to(self.repo).as_posix()):
                accepted = path.read_bytes()
                path.write_bytes(accepted + b"\n")
                try:
                    with self.assertRaisesRegex(
                        taskctl.TaskctlError, "active governance|reviewed activation"
                    ):
                        controller.close(
                            gate_runner=lambda _step, _argv: (_ for _ in ()).throw(
                                AssertionError("PASS retry must not rerun gates")
                            )
                        )
                finally:
                    path.write_bytes(accepted)
        self.assertEqual(controller.close()["state"], "PASS")

    def test_gvr3_pass_retry_revalidates_two_axis_review_durability(self) -> None:
        controller = self.ready_candidate()
        controller.activate(self.kernel, self.manifest)
        controller.close(gate_runner=lambda _step, _argv: {"rc": 0, "executed": True})
        report = self.artifact / "review/governance_axis.md"
        accepted_report = report.read_bytes()
        report.unlink()
        with self.assertRaises(taskctl.TaskctlError):
            controller.close()
        report.write_bytes(accepted_report)
        report.write_bytes(accepted_report + b"tamper\n")
        with self.assertRaises(taskctl.TaskctlError):
            controller.close()
        report.write_bytes(accepted_report)

        state_path = self.artifact / "state.json"
        accepted_state = state_path.read_bytes()
        for field in ("reviews", "review_leases"):
            with self.subTest(field=field):
                state = read_json(state_path)
                state[field].pop("governance")
                state_path.write_bytes(taskctl.canonical_json(state))
                with self.assertRaises(taskctl.TaskctlError):
                    controller.close()
                state_path.write_bytes(accepted_state)
        state = read_json(state_path)
        contract = controller._contract()
        for step in ("taskctl_scope_refresh", "task_gate", "atomic_evidence"):
            with self.subTest(step=step):
                log = self.repo / state["terminal_receipts"][step]["log"]
                accepted_log = log.read_bytes()
                log.unlink()
                with self.assertRaises(taskctl.TaskctlError):
                    controller.close()
                with self.assertRaises(taskctl.TaskctlError):
                    controller._active_context(contract)
                log.write_bytes(accepted_log)
        self.assertEqual(controller.close()["state"], "PASS")

    def test_doctor_is_read_only_and_reports_first_incomplete_ordinal(self) -> None:
        controller = self.bootstrap()
        with self.assertRaises(taskctl.PostEffectCrash):
            controller.events.run(
                step="opaque",
                argv=["opaque"],
                cwd=self.repo,
                classification="NON_SQLITE",
                runner=lambda: (_ for _ in ()).throw(taskctl.PostEffectCrash()),
            )
        before = {
            path.relative_to(self.artifact): path.read_bytes()
            for path in self.artifact.rglob("*")
            if path.is_file()
        }
        tracked = self.repo / "AGENTS.md"
        tracked_info = tracked.stat()
        os.utime(
            tracked,
            ns=(tracked_info.st_atime_ns, tracked_info.st_mtime_ns + 1_000_000_000),
        )
        index = self.repo / ".git/index"
        index_info = index.lstat()
        index_before = (
            index.read_bytes(),
            index_info.st_ino,
            index_info.st_size,
            index_info.st_mtime_ns,
        )
        report = controller.doctor()
        after = {
            path.relative_to(self.artifact): path.read_bytes()
            for path in self.artifact.rglob("*")
            if path.is_file()
        }
        self.assertEqual(report["live_state"], "OUTCOME_UNKNOWN")
        self.assertEqual(report["first_incomplete_ordinal"], 2)
        self.assertEqual(before, after)
        index_info = index.lstat()
        self.assertEqual(
            (
                index.read_bytes(),
                index_info.st_ino,
                index_info.st_size,
                index_info.st_mtime_ns,
            ),
            index_before,
        )

    def test_doctor_uses_live_replay_process_marker_pid(self) -> None:
        controller = self.bootstrap()
        child = (
            "import importlib.machinery,importlib.util,pathlib,sys;"
            "loader=importlib.machinery.SourceFileLoader('tc_doctor_replay',sys.argv[1]);"
            "spec=importlib.util.spec_from_loader(loader.name,loader);"
            "module=importlib.util.module_from_spec(spec);"
            "sys.modules[loader.name]=module;loader.exec_module(module);"
            "store=module.EventStore(pathlib.Path(sys.argv[2]),sys.argv[3]);"
            "\ntry:\n store.run(step='replay',argv=['replay'],cwd=pathlib.Path(sys.argv[4]),"
            "classification='INTERNAL',runner=lambda:(_ for _ in ()).throw("
            "module.PostEffectCrash()),replay_safe=True,effect_verifier=lambda:False)"
            "\nexcept module.PostEffectCrash:\n pass"
        )
        created = subprocess.run(
            [
                sys.executable,
                "-c",
                child,
                str(TASKCTL_PATH),
                str(self.artifact),
                self.TASK_ID,
                str(self.repo),
            ],
            cwd=self.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        incomplete = controller.events.first_incomplete()
        self.assertIsNotNone(incomplete)
        assert incomplete is not None
        command = controller.events._load_event(incomplete, "command")
        self.assertNotEqual(command["pid"], os.getpid())
        marker = self.artifact / "process" / f"{incomplete:08d}.json"
        marker.parent.mkdir(exist_ok=True)
        marker.write_bytes(
            taskctl.canonical_json(
                {
                    "ordinal": incomplete,
                    "pid": os.getpid(),
                    "request_digest": command["request_digest"],
                }
            )
        )
        report = controller.doctor()
        self.assertEqual(report["live_state"], "RUNNING_COMMAND")
        self.assertEqual(report["first_unfinished_reason"], "RUNNING_COMMAND")

    def test_doctor_reports_first_unfinished_prerequisite_and_failed_result(
        self,
    ) -> None:
        controller = self.bootstrap()
        report = controller.doctor()
        self.assertEqual(report["first_unfinished_step"], "summary")
        self.assertEqual(report["first_unfinished_reason"], "MISSING")

        (self.artifact / "summary.md").write_text("# Summary\n", encoding="utf-8")
        report = controller.doctor()
        self.assertEqual(report["first_unfinished_step"], "test")
        self.assertEqual(report["first_unfinished_reason"], "MISSING_RESULT")

        test_log = self.artifact / "outputs/test-failed.log"
        test_log.write_text("failed\n", encoding="utf-8")
        controller.events.run(
            step="test",
            argv=list(taskctl.GVR3_LEGACY_RED_ARGV),
            cwd=self.repo,
            classification="NON_SQLITE",
            runner=lambda: {
                "rc": 1,
                "executed": True,
                "log": str(test_log.relative_to(self.repo)),
            },
        )
        report = controller.doctor()
        self.assertEqual(report["first_unfinished_step"], "test")
        self.assertEqual(report["first_unfinished_reason"], "LATEST_RESULT_NONZERO")

        passed_log = self.artifact / "outputs/test-passed.log"
        passed_log.write_text("passed\n", encoding="utf-8")
        controller.events.run(
            step="test",
            argv=list(taskctl.GVR3_LEGACY_RED_ARGV),
            cwd=self.repo,
            classification="NON_SQLITE",
            runner=lambda: {
                "rc": 0,
                "executed": True,
                "log": str(passed_log.relative_to(self.repo)),
            },
        )
        report = controller.doctor()
        self.assertEqual(report["first_unfinished_step"], "shell_check")
        self.assertEqual(report["first_unfinished_reason"], "MISSING_RESULT")

    def test_controller_marks_opaque_missing_result_blocked_without_replay(
        self,
    ) -> None:
        controller = self.bootstrap()
        argv = ["python3", "-c", "pass"]
        with self.assertRaises(taskctl.PostEffectCrash):
            controller.events.run(
                step="test",
                argv=argv,
                cwd=self.repo,
                classification="NON_SQLITE",
                runner=lambda: (_ for _ in ()).throw(taskctl.PostEffectCrash()),
            )
        with self.assertRaisesRegex(taskctl.TaskctlError, "OUTCOME_UNKNOWN"):
            controller.record("test", argv, self.repo)
        blocked = read_json(self.artifact / "state.json")
        self.assertEqual(blocked["state"], "BLOCKED")
        self.assertEqual(blocked["reason"], "OUTCOME_UNKNOWN")

    def test_prepare_review_blocks_opaque_incomplete_before_candidate_writes(
        self,
    ) -> None:
        controller = self.bootstrap()
        self.install_required_results(controller)
        with self.assertRaises(taskctl.PostEffectCrash):
            controller.events.run(
                step="opaque",
                argv=["opaque"],
                cwd=self.repo,
                classification="NON_SQLITE",
                runner=lambda: (_ for _ in ()).throw(taskctl.PostEffectCrash()),
            )
        candidate = self.artifact / "candidate/virtual.patch"
        self.assertFalse(candidate.exists())
        with self.assertRaisesRegex(taskctl.TaskctlError, "OUTCOME_UNKNOWN"):
            controller.prepare_review(kernel=self.kernel, manifest=self.manifest)
        state = read_json(self.artifact / "state.json")
        self.assertEqual(state["state"], "BLOCKED")
        self.assertEqual(state["reason"], "OUTCOME_UNKNOWN")
        self.assertFalse(candidate.exists())

    def test_wrong_action_does_not_block_recoverable_internal_transition(self) -> None:
        controller = self.bootstrap()
        self.delete_result_for_step("taskctl_start")
        before = (self.artifact / "state.json").read_bytes()
        with self.assertRaisesRegex(taskctl.TaskctlError, "RECOVERABLE_INTERNAL"):
            controller.record(
                "lint",
                [sys.executable, "-c", "raise SystemExit(0)"],
                self.repo,
            )
        self.assertEqual((self.artifact / "state.json").read_bytes(), before)
        with mock.patch.object(taskctl, "legacy_task_pass", return_value=True):
            recovered = controller.start(
                self.task_file,
                bootstrap_kernel=self.kernel,
                bootstrap_manifest=self.manifest,
            )
        self.assertEqual(recovered["state"], "IMPLEMENTING")
        self.assertIsNone(controller.events.first_incomplete())


if __name__ == "__main__":
    unittest.main()
