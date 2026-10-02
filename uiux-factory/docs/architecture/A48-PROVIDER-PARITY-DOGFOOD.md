# A48.5 — Provider Parity + Opt-in Compatibility Dogfood

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A48.4 Managed Provider Compatibility Adapter

## 1. Purpose

A48.5 validates the A48.4 migration bridge before any Factory manager/default integration.

It intentionally separates two evidence classes:

1. **offline provider-contract parity** — deterministic regression evidence for the Factory completion contract and adapter behavior;
2. **project-profile compatibility smoke** — deterministic checks that Nova/Lumen/CENNEXT/LuxRoom canonical task/routing context survives use of the adapter boundary.

Neither class is live-provider, rendered UI, user-validation or product-outcome evidence.

Real project/runtime evidence remains owned by A13/A14/A20 and the canonical QA/evidence stack.

## 2. Benchmark surfaces

Corpus:

```text
benchmarks/provider-parity-v1.json
```

Evaluator:

```text
core/benchmarks/provider_parity_regression.py
```

Validator:

```text
scripts/validate_provider_parity_benchmark.py
```

Main UIUX Factory CI runs the validator before the full pytest suite.

## 3. Legacy caller-contract parity

The benchmark validates the current legacy Factory entrypoint without importing its `aiohttp` transport.

It parses `core/runtime/free_provider.py` with AST and requires:

```text
async complete(self, stage, system, prompt, *, json_mode)
```

It also requires the legacy provider to consume the dependency-light shared compatibility contract for:

```text
80k context ceiling
20-call run ceiling
stage token budgets
stage timeout budgets
```

This catches signature/budget drift without making canonical Flow OS tests depend on legacy network packages.

## 4. Offline completion-contract cases

The benchmark covers:

- plain text/Markdown artifact preservation;
- JSON design-contract artifact preservation;
- frontend-bundle JSON artifact preservation;
- stage preferred-provider ordering;
- bounded transient retry then fallback;
- rejection of malformed JSON object mode;
- rejection of lifecycle `PASS` as a compatibility completion;
- rejection of evidence-bearing compatibility carriers.

Every successful adapter history row must retain:

```text
compatibility_mode = managed_artifact_carrier
```

so migration provenance is visible.

## 5. Project-profile compatibility smoke

The benchmark covers every currently registered cross-project dogfood profile:

```text
Nova
Lumen
CENNEXT
LuxRoom
```

For each project it:

1. loads the canonical `ProjectDogfoodProfile`;
2. compiles the task contract through the canonical `GoalInterpreter`;
3. routes through the canonical `FlowPlanner`;
4. verifies expected change surface and flow;
5. sends that compiled context through the A48.4 compatibility adapter using a deterministic managed provider;
6. verifies project identity and flow survive the adapter boundary.

This does **not** claim that the model designed or rendered the project correctly. The result detail explicitly says `not product evidence`.

## 6. Why no live provider secret is required

A48.5 is a deterministic regression suite. CI must not require private Groq/Gemini credentials or make network quality a merge prerequisite.

Live provider behavior depends on account tier, model availability, rate limits and external service state. That belongs to environment-specific verification, not a deterministic repository benchmark.

A48.5 therefore proves interface/parity invariants offline while A13/A14/A20 continue to protect real repository/runtime behavior.

## 7. Authority boundary

Provider parity benchmark output cannot:

- become a runtime `EvidenceRecord` automatically;
- satisfy stage gates;
- mark a rendered UI PASS;
- stand in for browser QA;
- stand in for real-user validation;
- authorize merge/deploy/release by itself;
- justify a provider default migration by itself.

The benchmark report labels its scope:

```text
offline_contract_parity_not_live_provider_or_product_evidence
```

## 8. Acceptance criteria

A48.5 is complete when:

- [x] legacy `complete()` shape is regression-checked without importing network transport;
- [x] shared context/call/token/timeout compatibility boundaries are checked;
- [x] representative plain/JSON/frontend completion contracts are covered;
- [x] provider preference and bounded transient fallback are covered;
- [x] malformed JSON and authority/evidence-bearing carriers fail closed;
- [x] every registered real-project dogfood profile has an offline adapter smoke;
- [x] project smoke is explicitly not product evidence;
- [x] provider parity validator runs in Main CI;
- [x] manager/default provider remains unchanged;
- [ ] final head passes UIUX Factory CI, A20, A13 and A14.

## 9. Handoff

Only after A48.5 is green should A48.6 consider a **controlled manager opt-in integration**. That task must retain the legacy default, require an explicit feature flag, preserve immediate rollback, record which provider lane was used and run the same cross-project verification before any default migration decision.