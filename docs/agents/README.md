# FPMS Agent Governance Modules

This directory contains the routed normative modules proposed by the Governance Reset.
They remain inactive until the activation task installs the reviewed root kernel and
`docs/agents/manifest.json`, then reaches terminal PASS.

### Rule GOV-MODULES-001 — Authority, routing, and rule identity

Instruction authority descends from current system/developer/user instructions, to root
`AGENTS.md`, to the active manifest and its selected modules, to approved exact contracts,
then to non-normative examples. Lower layers may not weaken higher layers. A missing or
inconsistent manifest, duplicate Rule ID, unresolved Rule-Ref, unsafe selector, or changed
governance digest fails closed for affected work.

Each canonical rule appears exactly once as:

```text
### Rule GOV-SCOPE-001 — Exact task ownership
```

Other documents may refer to it only as:

```text
Rule-Ref: GOV-SCOPE-001
```

The owner module must not reference its own Rule ID. The active manifest is the machine
authority for rule owners and selectors.

## Module routing

| Module | Sole concern |
| --- | --- |
| `domain-safety.md` | Product, legal, fee, lineage, permission, data, API, SQLite, and UI safety |
| `execution.md` | Atomic ownership, risk, runbooks, waves, liveness, lint, and reporting |
| `evidence.md` | Evidence state, independent review, scope, gates, and release acceptance |
| `source-authority.md` | Source precedence and the FPMS source index |
| `legacy-mvp1.md` | Phase 3/3.1/3.5 and one-time router compatibility |

`README.md`, `execution.md`, and `evidence.md` are always selected. Other modules are
selected by the manifest using task risk, task path, and closure tags.

Rule-Ref: GOV-BEHAVIOR-001
Rule-Ref: GOV-CUSTOMER-001
Rule-Ref: GOV-RELEASE-001
Rule-Ref: GOV-SKILLS-001
