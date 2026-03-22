# Batch Execution QA Ledger Template (2026-03-18)

## Purpose

This template prevents QA close audits from treating a representative slice as if it closed an entire cluster.

Every future batch close audit must include an item-to-slice ledger.

Without this ledger:
- no batch may be declared complete
- execution summary must not mark in-scope items as fully covered

## Required Ledger Columns

| Item | Required Slices | Implemented Task IDs | Evidence | Residual Gap | Close Decision |
|---|---|---|---|---|---|

Definitions:
- `Item`: one `Partially Implemented` item from the approved batch scope
- `Required Slices`: the minimum closure slices needed to claim the item is actually covered
- `Implemented Task IDs`: task IDs that produced those slices
- `Evidence`: specific artifact or test evidence
- `Residual Gap`: any remaining uncovered part
- `Close Decision`: `covered` / `partial` / `deferred` / `blocked`

## Mandatory Rules

1. Every in-scope `Partially Implemented` item must appear exactly once in the ledger.
2. No item may be marked `covered` unless all required slices are listed and evidenced.
3. If a task closed only a representative slice, the item must be marked `partial`.
4. If the narrowed interpretation was intentionally used, the ledger must say so explicitly.
5. If a residual gap exists, it must be named concretely, not described vaguely.

## Required Audit Sections

### 1. Batch Scope Confirmation

- covered items
- excluded items
- deferred items
- blocked items

### 2. Item-to-Slice Ledger

Use the required table format above.

### 3. Shared Ownership Review

State:
- which shared files were touched
- whether serialization was respected
- whether any scope contamination occurred

### 4. Gate Review

List every implementation task:
- task id
- task gate result
- artifact completeness

### 5. Batch Close Decision

The batch close section must state one of:
- `complete`
- `partial`
- `blocked`

If `complete`, the ledger must contain no `partial`, `deferred`, or `blocked` rows for in-scope items.

## Required Close Rules

A batch may claim `complete` only if:
- every implementation task is `PASS`
- every required artifact exists
- every task gate passed
- every in-scope item is `covered` in the ledger
- no residual gap remains inside the approved batch interpretation

Otherwise:
- the batch must remain `partial` or `blocked`

## Recommended Ledger Skeleton

```md
## Item-to-Slice Ledger

| Item | Required Slices | Implemented Task IDs | Evidence | Residual Gap | Close Decision |
|---|---|---|---|---|---|
| `US-XX-01` | slice A + slice B | `PE-BE-...`, `PE-FE-...` | test + artifact | none | `covered` |
| `FR-XX-02` | slice C | `PE-BE-...` | artifact only | FE visibility missing | `partial` |
```

## Enforcement

If the QA task lacks this ledger, the QA task itself should be treated as incomplete.
