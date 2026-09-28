---
name: research-evidence-pipeline
description: Turn a user-research need into an operational evidence pipeline: decision map, recruitment/screener, interview or usability protocol, consent/data handling, traceable evidence ledger, synthesis and decision log. Use for evidence-led or production-learning work. Never fabricates participants, quotes, findings, counts or validation.
---

# Research Evidence Pipeline

## Goal

Close the gap between “we should test this” and a research package that can actually be run, ingested and traced into product decisions.

This skill operationalizes — but does not replace — `real-user-validation`, `user-research-planning-and-recruitment`, and `research-synthesis-and-insight-management`.

## Evidence boundary

Allowed states:

- `PLANNED_VALIDATION` — protocol exists; no direct user evidence yet.
- `BLOCKED_USER_EVIDENCE` — research is needed but participant/access constraints block execution.
- `DIRECT_USER` — traceable observation/interview evidence from actual or likely target users.
- `LIVE_BEHAVIOR` — traceable production/service behavior.
- `PROXY` — support/sales/domain-expert evidence.
- `DESK_EVIDENCE` — documents/reference/market evidence.
- `HYPOTHESIS` — unvalidated belief.
- `UNKNOWN` — insufficient evidence.

Never convert `PLANNED_VALIDATION`, `HYPOTHESIS`, `PROXY`, or `DESK_EVIDENCE` into `DIRECT_USER` without a real session/evidence record.

## Pipeline

1. **Decision map** — write each consequential product/design decision and the uncertainty that could change it.
2. **Research questions** — convert uncertainty into answerable questions; do not ask users to choose design solutions for the team.
3. **Method** — choose interview, concept test, usability test, diary/field observation, or live-behavior review based on the question.
4. **Participants** — define behavioral criteria, exclusions, relevant accessibility needs, target count/range, recruitment channel and compensation/consent handling.
5. **Protocol** — instantiate the smallest useful template set from `templates/`.
6. **Run** — record session IDs and evidence references; avoid unnecessary personal data.
7. **Ingest** — append atomic evidence records to `docs/research/evidence-ledger.jsonl`; one observed claim per record when practical.
8. **Synthesize** — cluster evidence while preserving contradictory observations and source traceability.
9. **Decide** — update `docs/research/decision-log.md` with decision, evidence used, confidence, change made, owner and remaining UNKNOWNs.
10. **Verify** — before claiming validation, confirm every material finding points to real ledger evidence and the participant population fits the decision.

## Required package

For a substantial research round create only the files that are applicable:

```text
docs/research/
  research-plan.md
  screener.md
  interview-guide.md            # discovery/interview rounds
  usability-test-script.md      # task-based solution validation
  evidence-ledger.jsonl         # empty until evidence exists
  findings.md
  decision-log.md
```

Start from the templates shipped with this skill rather than inventing a new structure for every project.

## Evidence ledger contract

Each JSONL line must conform conceptually to `templates/evidence-ledger.schema.json` and include:

- stable `evidence_id`;
- evidence class/status;
- study/session/source reference;
- participant segment or source type (no unnecessary identifying detail);
- observation/claim;
- affected decision/hypothesis IDs;
- timestamp/date when available;
- confidence/limitations;
- artifact/source reference.

Quotes are optional. If used, they must come from a real source record and remain short/contextual.

## No-participant mode

If participant access does not exist:

- create the plan, screener and protocol;
- leave `evidence-ledger.jsonl` empty;
- mark the round `PLANNED_VALIDATION` or `BLOCKED_USER_EVIDENCE`;
- list what decision remains at risk;
- proceed only if project risk allows;
- never invent names, quotes, percentages, sample sizes, task success rates or findings.

## Quality gate

PASS only when:

- research questions map to explicit decisions;
- participant criteria map to the real audience/context;
- protocol avoids leading questions and solution-selling;
- privacy/consent/data handling is explicit enough for the project risk;
- evidence records are traceable to real sources;
- contradictory evidence is preserved;
- findings change, confirm, defer or reject a named decision;
- missing evidence remains visibly `PLANNED`, `BLOCKED` or `UNKNOWN`.

A polished research plan alone is **not** evidence that research occurred.
