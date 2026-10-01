# A44.2 — Product & Truth Critics

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A41 Brain contracts + A42 Evidence Integrity + A44.1 Core Design Critics

## 1. Purpose

A44.2 adds three advisory critics:

```text
Product Critic
Runtime Critic
Evidence / Truth Critic
```

They extend the critique surface without creating a second gate, evidence or execution system.

Canonical implementation:

```text
core/brain_os/critics/product_truth.py
```

Tests:

```text
tests/test_brain_product_truth_critics_a44.py
```

## 2. Product Critic

`ProductCritic` reads A41 contracts only:

```text
BrainTaskFrame
Hypothesis
Decision
Uncertainty
```

It can observe bounded product-thinking/governance gaps such as:

- missing success criteria;
- broad REDESIGN/PRODUCT work without hypotheses;
- broad work without explicit Decision records;
- low-confidence broad task framing;
- BLOCKED/CONFLICTED uncertainties;
- high-risk hypotheses still unverified;
- selected decisions without evidence references;
- costly/irreversible selections still owned by `brain_advisory`;
- blocked hypotheses/decisions.

It does not invent product metrics, validate a hypothesis, select an alternative or execute a decision.

## 3. Runtime Critic

`RuntimeCritic` delegates current-state evidence selection to the canonical owner:

```text
core.runtime.flow_os.evidence.effective_evidence
```

This preserves the existing retry/supersession rule:

```text
latest trusted record per stage + evidence channel
```

Therefore an old failed validator result does not remain a false blocker after a later trusted PASS on the same channel.

The Runtime Critic can observe:

- an effective current runtime record with `status=FAIL`;
- an expected stage with no effective trusted evidence;
- caller-declared expected evidence types missing from the current effective set.

The last two are review expectations only. They are **not** converted into runtime gates.

The critic deliberately does not call:

```text
gate_evidence_errors(...)
```

and cannot mark a runtime stage passed/failed.

## 4. Evidence / Truth Critic

`EvidenceTruthCritic` reuses A42 validators directly:

```text
validate_evidence_integrity(...)
validate_end_to_end_lineage(...)
```

A42 findings are projected into A41 `CritiqueIssue(status=OBSERVED)` records.

Severity mapping:

```text
A42 ERROR   → P0 observation
A42 WARNING → P1 observation
```

The critic does not recalculate trusted-evidence flags, create canonical evidence, repair graph relationships or declare release readiness.

A complete trusted lineage may produce zero critic issues, but zero issues still does not mean QA PASS or release ready.

## 5. ProductTruthCriticReport

Every A44.2 critic returns a strict immutable report containing:

```text
critic_id
issues
reviewed_artifacts
source_owners
effective_evidence_refs (runtime only)
integrity_valid / lineage_complete (truth critic metadata)
advisory_only = true
authority_effect = none
gate_effect = none
evidence_effect = none
```

The report intentionally has no `passed` field.

## 6. Evidence handling

Runtime failures may carry an existing canonical runtime evidence ID in `CritiqueIssue.evidence_refs`.

Evidence/Truth findings deliberately do not copy arbitrary graph subject IDs into `evidence_refs`, because a graph node/edge ID is not automatically a canonical evidence reference.

Every issue remains `OBSERVED`. Stronger `CONFIRMED` / `RESOLVED` states still require the A41/A42 evidence + retest contracts.

## 7. Authority boundary

A44.2 does not import/call:

```text
ProviderManagedRunner
ManagedFlowController
ProductionReleaseController
gate_evidence_errors
release_action
run_target_command
merge_pull_request
```

It cannot:

- execute target commands;
- mutate flows/skills;
- evaluate canonical runtime gates;
- upgrade evidence trust;
- accept repairs;
- merge/deploy/release.

## 8. Acceptance criteria

A44.2 is complete when:

- [x] Product Critic detects reasoning/governance gaps from A41 contracts;
- [x] Runtime Critic uses canonical `effective_evidence()` semantics;
- [x] historical failures superseded by same-channel trusted PASS do not create false findings;
- [x] effective current failures remain visible;
- [x] Evidence/Truth Critic reuses both A42 integrity and end-to-end lineage validators;
- [x] every critic issue begins as `OBSERVED`;
- [x] zero findings cannot be represented as a runtime/release PASS;
- [x] critics do not import gate/release/execution owners;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 9. Handoff

After A44.2 is green and merged, the next architecture step should connect A44 critic outputs to the existing A41 repair contracts through a **bounded critique → root-cause → repair-proposal orchestrator**.

That orchestrator must remain proposal-only: it may create `RootCause`, `RepairDirective` and `RetestRequirement` objects, but it must not execute repairs or mark issues resolved without canonical retest evidence.
