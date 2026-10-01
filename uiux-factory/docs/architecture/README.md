# Architecture Truth Index

Status: **A40.1 RECONCILED CURRENT TRUTH**  
Audit date: **2026-10-02**  
Baseline: `main@304baefb6999e552708150a20e5c01491aa3663e`

This directory contains the current architecture truth for UIUX Factory / Flow OS evolution.

Read in this order:

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, owners, evidence/memory surfaces and remaining convergence debt.
2. `MIGRATION-BOUNDARIES.md` — active post-A4 architecture contract and Brain OS boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` — A40.1 audit findings, capability/ownership matrix, duplicate-surface classification and roadmap corrections.

## Current architecture statement

A4 runtime consolidation is implemented. The shared executable Flow OS owner is:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas and runtime policy. Python modules under `skills_UIUX/runtime/` are compatibility shims, not a second executable Flow OS.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`, while the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain OS rule

Future Brain OS work may add reasoning, hypothesis/decision contracts, critique orchestration, evidence relationships, richer memory and unified evaluation **above** the canonical runtime.

It must not create a third execution runtime or a competing evidence/authority system.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

Historical documents remain useful audit history, but do not override current code.

## Next architecture task

A40.2 should convert the A40.1 invariants into executable architecture regression tests before Brain Core Contracts are introduced.
