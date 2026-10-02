# A54.1 — Flow 4 Final Regression & Cross-project Dogfood

Status: **ACTIVE / FINAL REGRESSION GATE / NO RELEASE AUTHORITY**  
Audit date: **2026-10-02**

## Purpose

Flow 4 is the final bounded regression/dogfood flow after Flow 3 closed the architecture-debt ledger for the current workspace upgrade.

It does not create new runtime capability. It verifies that the upgraded workspace still satisfies current architecture boundaries and that one project-agnostic Factory contract works across four materially different real repositories.

## Representative project matrix

| Project | Archetype | Pinned SHA |
|---|---|---|
| Nova | fintech / trust / data | `e206f51f2fda006adcf52497d8b827e048e157ec` |
| Lumen | visual / cultural experience | `219f3e49f9956290ef69a2e49cb91fefddd5f561` |
| CENNEXT | B2B / enterprise service | `273403accf8979608fbb16dbe2741cedb0430fb6` |
| LuxRoom | ecommerce / purchase flow | `37e6a8c4a2aecdb9cefd9fd4291b353252d5356b` |

The matrix intentionally spans product/domain differences. Project-specific behavior remains profile data under `core/dogfood/cross_project.py`; `RealProjectDogfoodRunner` stays project-agnostic.

## Executable owner set

```text
benchmarks/final-upgrade-regression-v1.json
core/benchmarks/final_upgrade_regression.py
scripts/validate_final_upgrade_regression.py
tests/test_final_upgrade_regression_a54.py
.github/workflows/a20-release-candidate.yml
```

## Two-stage fail-closed behavior

### Repository-only validation

Normal UIUX Factory CI has no external project checkouts. Therefore:

```text
python scripts/validate_final_upgrade_regression.py
```

must prove the Flow 4 contract and current Flow 3 architecture state are clear, but must derive:

```text
HOLD_FINAL_REGRESSION_EVIDENCE_REQUIRED
```

Missing real-project evidence is never interpreted as PASS.

### A20 final evidence aggregation

A20 checks out all four repositories at exact pinned SHAs and creates:

```text
release-audit.json
nova-generic.json
lumen-generic.json
cennext-generic.json
luxroom-generic.json
```

Then:

```text
python scripts/validate_final_upgrade_regression.py \
  --report-root "$REPORT_ROOT" \
  --output "$REPORT_ROOT/flow4-final.json"
```

aggregates the actual receipts.

Decision policy:

```text
missing receipt/report
→ HOLD_FINAL_REGRESSION_EVIDENCE_REQUIRED

present evidence with failed project, SHA drift or truth-boundary regression
→ FINAL_REGRESSION_FAILED

release audit + all four exact pinned dogfood reports pass
→ WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS
```

## Required Flow 3 state

Flow 4 re-evaluates Flow 3 from current executable source. It requires:

```text
decision = ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE
closed = 4
intentional_holds = 5
new_actionable_debt = 0
flow4_allowed = true
```

Flow 4 therefore cannot hide a later architecture regression behind stale dogfood receipts.

## Per-project contract

Each project report must prove:

```text
exact pinned target SHA
registered repository/profile identity
source truth resolved and loaded
required evidence paths present
adaptive change surface preserved
expected declarative Flow resolved
cross-project isolation clear
all generic runner checks passed
```

The final aggregator also rejects reports that manufacture evidence outside the generic lane. Required states remain:

```text
browser.status = NOT_RUN
provider_reasoning.status = NOT_RUN
human_review.status = pending
human_review.verdict = null
release.status = NOT_ATTEMPTED
```

A generic dogfood PASS is regression evidence about source grounding, task-contract inference, routing and isolation. It is not browser quality, provider quality, human aesthetic approval, usability evidence, deploy evidence or release authorization.

## Intentional holds remain intentional

Flow 4 does not clear the five Flow 3 holds:

1. provider-default migration still requires the real A51.1 8/8 live matrix;
2. lifecycle mutation convergence still has six A52.1 semantic blockers;
3. GenAI/NIST remains freshness-triggered;
4. vector/semantic retrieval still requires explicit product need + comparative benchmark evidence;
5. compatibility-shim removal still requires the fresh post-observation external/downstream audit no earlier than 2026-12-31.

## Non-authority boundary

Flow 4 preserves:

```text
provider_default_change_allowed = false
lifecycle_state_owner_change_allowed = false
routing_change_allowed = false
knowledge_index_mutation_allowed = false
vector_search_change_allowed = false
compatibility_shim_deletion_allowed = false
evidence_authority_change_allowed = false
gate_authority_change_allowed = false
release_authority_change_allowed = false
product_evidence = false
```

Effects remain:

```text
execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## Final owner review boundary

A Flow 4 PASS does not itself perform or fabricate the deferred broad owner review.

Only this decision:

```text
WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS
```

opens the final broad owner-review step that was intentionally deferred throughout A50–A53.

Until that exact final-head evidence exists:

```text
final_owner_review_status = PENDING_AFTER_FLOW4_PASS
```
