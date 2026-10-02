# A47.1 — Provenance-Aware Brain Scorecard

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A42 Evidence Integrity + A44 Critics + canonical `RunEvaluation`

## 1. Purpose

A47.1 fills the remaining A40 evaluation-aggregation gap without creating a second QA or gate system.

Canonical implementation:

```text
core/brain_os/scorecard.py
```

The scorecard aggregates already-produced outputs from existing owners:

```text
canonical RunEvaluation
+ A44 critic reports
+ A42 EvidenceIntegrityReport
→ BrainScorecard
```

It does not run those evaluators itself.

## 2. Canonical runtime outcome remains authoritative

The runtime channel is supplied as an existing:

```text
core.evaluation.run_evaluator.RunEvaluation
```

A47.1 copies these fields verbatim:

```text
run_id
flow_id
managed_state
outcome
evaluated_at
effective_evidence_count
```

`runtime_outcome` is therefore a mirror of the canonical evaluator result. The scorecard does not recompute, upgrade or downgrade it.

For example, `insufficient_evidence` remains `insufficient_evidence` even when every advisory critic has zero findings.

## 3. Critic aggregation

A47.1 accepts existing A44 reports:

```text
CoreCriticReport
ProductTruthCriticReport
```

For each explicitly provenance-addressed report it records only bounded summary data:

```text
source_ref
critic_id
source_owners
reviewed_artifacts
issue_count
severity_counts
status_counts
issue_ids
```

The scorecard does not confirm, resolve, synthesize or repair critic issues.

## 4. Evidence-integrity aggregation

A47.1 accepts existing A42:

```text
EvidenceIntegrityReport
```

and mirrors:

```text
graph_id
integrity_valid
lineage_complete
ERROR count
WARNING count
finding codes
```

It does not call integrity validators and does not create or upgrade evidence trust.

## 5. Provenance contract

Every aggregated channel must provide a unique explicit `source_ref`.

The final `BrainScorecard.source_refs` must exactly cover:

```text
runtime source
all critic sources
all integrity sources
```

Duplicate source refs are rejected so two distinct channels cannot collapse into ambiguous provenance.

## 6. No synthetic overall verdict

`BrainScorecard` intentionally has no:

```text
passed
release readiness flag
numeric overall score
```

It exposes the canonical runtime outcome alongside advisory review channels instead of inventing a second terminal verdict.

Every scorecard declares:

```text
advisory_only = true
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## 7. Authority boundary

`core/brain_os/scorecard.py` does not import/call:

```text
RunEvaluator.evaluate(...)
effective_evidence(...)
gate_evidence_errors(...)
ProviderManagedRunner
ManagedFlowController
ProductionReleaseController
run_target_command
release_action
merge_pull_request
```

It cannot:

- execute a flow;
- collect new runtime evidence;
- pass/fail a canonical runtime gate;
- confirm or resolve critique issues;
- upgrade evidence trust;
- decide release readiness;
- merge, deploy or release.

## 8. Acceptance criteria

A47.1 is complete when:

- [x] canonical `RunEvaluation.outcome` is preserved verbatim;
- [x] A44 core/product/truth reports can be summarized with explicit source refs;
- [x] A42 integrity metadata can be summarized without rerunning validators;
- [x] duplicate/empty provenance refs are rejected;
- [x] zero critic findings cannot upgrade an `insufficient_evidence` runtime outcome;
- [x] scorecard has no PASS/release-readiness/overall-score field;
- [x] scorecard has no authority/gate/evidence/release effect;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 9. Handoff

After A47.1 is green and merged, A47.2 should add a deterministic scorecard benchmark covering mixed runtime outcomes, critic severity distributions, evidence-integrity states and provenance collisions. The benchmark must remain read-only and must prove that scorecard aggregation cannot change canonical runtime outcomes or source artifacts.
