# FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPTS-20260826-10

Status: BLOCKED
Risk-Tier: HIGH
Closure-Tags: ["demo", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPTS-20260826-10.md
Chosen runbook: `P0-release-read-only`

## Exact Closure Slice

After Task 09 freezes and pushes one immutable candidate, accept exactly one fresh HUMAN receipt and
one different-account CODEX receipt from separate clones/runs/databases, then compare them with the
Task 08 comparator. This task writes no repository bytes.

## Explicit Non-Closure

No candidate mutation, replacement receipt fabrication, same-actor substitution, release, or repo
write. Any failed actor run is preserved and returns to the first failed implementation ordinal.

## Done Definition

Both strict receipts PASS and the comparator proves identical normalized facts with distinct actors,
runs, roots, and databases. An independent PROTECTED reviewer binds the immutable evidence roots.

## Rollback

Discard no failed receipt. Delete only a verified disposable clone after its evidence is retained.
