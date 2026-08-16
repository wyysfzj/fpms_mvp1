from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TASKS = {
    "FPMS-DEMO-ABC-LOCAL-BOOT-DEPENDENCY-20260816-01": ("d8e249a", "c366dc4"),
    "FPMS-DEMO-ABC-BUNDLE-PREFLIGHT-20260816-01": ("5d43d67", "989a74d"),
    "FPMS-DEMO-ABC-FRESH-LOCAL-RUNNER-20260816-01": ("e76a84a", "d0fed70"),
    "FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01": ("2dff556", "652a64e"),
    "FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01": ("c7556c87", "5a256c9"),
    "FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01": ("9c33a8e", "c2cef33"),
    "FPMS-DEMO-ABC-FINANCE-UI-20260816-01": ("2ebe349", "69131b7"),
    "FPMS-DEMO-ABC-DRAFT-LOCK-RECONCILE-20260816-01": ("40bfe49", "174f2a7"),
    "FPMS-DEMO-ABC-CASE-NUMBER-LOOKUP-20260816-01": ("5b35acb", "7c083c1"),
    "FPMS-DEMO-ABC-BUNDLE-HARDENING-20260817-01": ("48ea46a", "f35a57b"),
    "FPMS-DEMO-ABC-BUNDLE-AUTHORITY-20260817-01": ("f1a1d4b", "dec431b"),
    "FPMS-DEMO-ABC-COMMAND-RECONCILIATION-20260817-01": ("b544ce2", "cfd56df"),
    "FPMS-DEMO-ABC-FINANCE-DECODER-20260817-01": ("be83ffd", "e95a435"),
}

EVIDENCE_ONLY = {
    "FPMS-DEMO-ABC-LIVE-E2E-20260816-01": "3ecd70b",
}


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def full_revision(revision: str) -> str:
    return git("rev-parse", revision).decode().strip()


def tree(revision: str) -> str:
    return git("show", "-s", "--format=%T", revision).decode().strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> int:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    candidate = full_revision("HEAD")
    candidate_tree = tree("HEAD")
    rebuilt: list[dict[str, object]] = []
    task_pairs = dict(TASKS)
    subject = git("show", "-s", "--format=%s", "HEAD").decode().strip()
    if subject != "chore(evidence): rebuild demo task patches":
        raise RuntimeError("evidence reconstruction must run from its committed implementation")
    task_pairs["FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01"] = (
        "HEAD^",
        "HEAD",
    )

    for task_id, (baseline_short, implementation_short) in task_pairs.items():
        baseline = full_revision(baseline_short)
        implementation = full_revision(implementation_short)
        parent = git("show", "-s", "--format=%P", implementation).decode().strip()
        if parent != baseline:
            raise RuntimeError(f"{task_id}: implementation is not the direct child of task freeze")
        patch = git("diff", "--binary", baseline, implementation, "--")
        if not patch:
            raise RuntimeError(f"{task_id}: implementation patch is empty")
        changed_files = git(
            "diff", "--name-only", "--diff-filter=ACDMRTUXB", baseline, implementation, "--"
        ).decode().splitlines()
        task_path = ROOT / "tasks" / "postdemo" / f"{task_id}.md"
        if not task_path.is_file():
            raise RuntimeError(f"{task_id}: task card is missing")
        artifact_git = ROOT / "artifacts" / task_id / "git"
        metadata = {
            "task_id": task_id,
            "baseline_commit": baseline,
            "baseline_tree": tree(baseline),
            "implementation_commit": implementation,
            "implementation_tree": tree(implementation),
            "task_card": task_path.relative_to(ROOT).as_posix(),
            "task_card_sha256": sha256(task_path.read_bytes()),
            "changed_files": changed_files,
            "patch_sha256": sha256(patch),
            "patch_bytes": len(patch),
            "reconstructed_at": now,
            "current_candidate_commit": candidate,
            "current_candidate_tree": candidate_tree,
        }
        write(artifact_git / "diff.patch", patch)
        write(
            artifact_git / "allowlist.json",
            (json.dumps(changed_files, ensure_ascii=False, indent=2) + "\n").encode(),
        )
        write(
            artifact_git / "reconstruction.json",
            (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode(),
        )
        write(artifact_git / "patch.sha256", f"{sha256(patch)}  diff.patch\n".encode())
        rebuilt.append(metadata)

    for task_id, revision_short in EVIDENCE_ONLY.items():
        revision = full_revision(revision_short)
        artifact_git = ROOT / "artifacts" / task_id / "git"
        marker = {
            "task_id": task_id,
            "classification": "EVIDENCE_ONLY_NO_PRODUCT_DIFF",
            "task_commit": revision,
            "task_tree": tree(revision),
            "current_candidate_commit": candidate,
            "current_candidate_tree": candidate_tree,
            "reconstructed_at": now,
            "superseded_by": "FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-01",
        }
        write(artifact_git / "diff.patch", b"")
        write(
            artifact_git / "no-product-diff.json",
            (json.dumps(marker, ensure_ascii=False, indent=2) + "\n").encode(),
        )

    status = git("status", "--porcelain=v1")
    output = {
        "status": "PASS",
        "reconstructed_at": now,
        "candidate_commit": candidate,
        "candidate_tree": candidate_tree,
        "worktree_status": status.decode().splitlines(),
        "implementation_task_count": len(rebuilt),
        "evidence_only_task_count": len(EVIDENCE_ONLY),
        "tasks": rebuilt,
    }
    output_path = (
        ROOT
        / "artifacts"
        / "FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01"
        / "reconstruction-report.json"
    )
    write(output_path, (json.dumps(output, ensure_ascii=False, indent=2) + "\n").encode())
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
