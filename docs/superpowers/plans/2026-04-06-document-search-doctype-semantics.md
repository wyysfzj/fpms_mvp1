# Document Search DocType Semantics Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze `DocType` as the only remaining truthful residual for `#19`, and decide whether a carrier prerequisite is mandatory.

**Architecture:** Compare `SPEC 2.0`, current `documents` model/API/FE contract, and current `ref_no` aliasing. This wave is documentation-only and must end with a prerequisite decision.

**Tech Stack:** Markdown planning docs, task docs, evidence scripts.

---

- Story Shape Classification:
  - `shared_file_density`: `medium`
  - `prereq_dependency_density`: `high`
  - `be_fe_coupling`: `doctype semantics before implementation`
  - `evidence_cost`: `medium`
- `chosen_runbook`: `P0-prereq-heavy-story`

## Batch Manifest

### Wave 1 — `DOCSEARCH-DOCTYPE-SPEC-01`
- Closure slice:
  - freeze independent `DocType` semantics
  - decide whether carrier prerequisite is required
- Non-closure:
  - no product implementation

### Wave 2 — `DOCSEARCH-QA-DOCTYPE-SPEC-01`
- Closure slice:
  - audit semantics freeze evidence
  - confirm next story is `DOCSEARCH-DOCTYPE-PRE-DB-01`
- Non-closure:
  - no product implementation
  - no close update

## Follow-up Queue

- `DOCSEARCH-DOCTYPE-PRE-DB-01`
- `DOCSEARCH-DOCTYPE-BE-01`
- `DOCSEARCH-DOCTYPE-FE-01`
- `DOCSEARCH-DOCTYPE-QA-01`
- `DOCSEARCH-CLOSE-01`

