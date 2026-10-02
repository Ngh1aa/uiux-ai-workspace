# A51.1 — Provider Default Migration Readiness

Status: **IMPLEMENTED AS READINESS GATE / DEFAULT NOT MIGRATED**  
Date: **2026-10-02**

## Goal

Determine what evidence is required before `managed_compat` may even be considered as the Factory AI provider default.

A51.1 does **not** change the default. Current truth remains:

```text
unset UIUX_FACTORY_PROVIDER_LANE -> legacy
UIUX_FACTORY_PROVIDER_LANE=legacy -> legacy
UIUX_FACTORY_PROVIDER_LANE=managed_compat -> managed_compat (explicit opt-in)
invalid value -> fail closed
```

There is no automatic cross-lane fallback.

## Why this task exists

A48 established compatibility and offline provider parity, but the canonical benchmark explicitly says:

```text
offline_contract_parity_not_live_provider_or_product_evidence
```

That is enough to keep the compatibility lane testable, but not enough to change the default used by real AI runs. A default migration needs live transport evidence without weakening the existing evidence/gate/release boundary.

## Readiness matrix

The canonical live-trial matrix is deliberately small but complete across every currently supported free-tier transport:

```text
providers: groq, gemini
lanes: legacy, managed_compat
modes:
  plain_text  -> research      -> json_mode=false
  json_object -> implementation -> json_mode=true
```

Required total:

```text
2 providers × 2 lanes × 2 modes = 8 sanitized receipts
```

All eight rows must exist and pass their transport/contract check before A51.1 may derive:

```text
READY_FOR_DEFAULT_MIGRATION_GOVERNANCE
```

Anything incomplete or failed derives:

```text
KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED
```

## Important authority boundary

Even `READY_FOR_DEFAULT_MIGRATION_GOVERNANCE` means only that a **separate governance task may be opened**.

A51.1 always keeps:

```text
default_change_allowed = false
provider_migration_allowed = false
auto_migration_allowed = false
billing_or_account_change_allowed = false
routing_change_allowed = false
skill_activation_change_allowed = false
evidence_authority_change_allowed = false
gate_authority_change_allowed = false
release_authority_change_allowed = false
product_evidence = false
```

Provider transport success is not rendered UI evidence, user validation, product-quality evidence or release evidence.

## Canonical files

```text
benchmarks/provider-default-migration-readiness-v1.json
benchmarks/provider-live-trial-receipts-v1.json
core/benchmarks/provider_default_migration_readiness.py
scripts/validate_provider_default_migration_readiness.py
scripts/run_provider_live_trial.py
tests/test_provider_default_migration_readiness_a51.py
```

Existing A48 parity remains active:

```text
benchmarks/provider-parity-v1.json
core/benchmarks/provider_parity_regression.py
scripts/validate_provider_parity_benchmark.py
```

## Sanitized live receipts

A receipt may contain only bounded transport metadata:

```text
provider
model
lane
mode_id
stage
json_mode
success
contract_valid
request_sha256
artifact_sha256   # success only
artifact_chars    # success only
error_category    # failure only
automatic_cross_lane_fallback = false
authority/gate/evidence/release effects = none
```

It must not persist:

```text
API keys / authorization headers
account or billing identifiers
prompt/system bodies
response/artifact bodies
provider error bodies
cookies or environment dumps
```

The collector hashes the fixed bounded trial request and returned artifact, then discards their bodies from the receipt.

## Live-trial collector

Live collection is intentionally **not** required by CI and is never automatic.

Before running it, the operator must deliberately confirm both the existing free-tier guard and the A51 live-trial guard:

```text
UIUX_FREE_TIER_CONFIRMED=1
UIUX_PROVIDER_LIVE_TRIAL_CONFIRMED=1
```

Configured providers/models/keys continue to come from the existing local environment contract. The collector does not add a new credential store.

Example:

```bash
cd uiux-factory
python scripts/run_provider_live_trial.py \
  --output /tmp/provider-live-trial-receipts-v1.json
```

The script does **not** overwrite `benchmarks/provider-live-trial-receipts-v1.json`, does not change `UIUX_FACTORY_PROVIDER_LANE`, and does not make a governance decision. A sanitized output must be reviewed before any deliberate canonical receipt-ledger update.

## Current expected decision

The repository starts with:

```text
collection_status = NOT_RUN
receipts = []
```

Therefore the active A51.1 validator is expected to derive:

```text
KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED
migration_governance_allowed = false
```

This is a valid, intentional PASS state for CI: the readiness mechanism is working and the default remains protected.

## Failure behavior

The evaluator fails closed when:

- the readiness contract loosens migration/authority boundaries;
- the default lane no longer resolves to `legacy` when the flag is absent;
- `managed_compat` stops being explicit opt-in;
- an invalid lane no longer fails closed;
- offline provider parity regresses;
- a receipt contains extra/raw fields;
- receipt hashes or mode metadata are invalid;
- matrix rows are duplicated or mislabeled;
- `COMPLETE` is claimed without the exact 8-row matrix;
- any receipt permits automatic cross-lane fallback or authority effects.

## Next task rule

If live receipts are absent/incomplete/failed, there is **no default-migration task**; `legacy` remains current truth.

Only after a reviewed canonical receipt ledger yields `READY_FOR_DEFAULT_MIGRATION_GOVERNANCE` may a separate bounded governance task decide whether a controlled default migration trial should exist. That later task still cannot infer product quality from transport parity.
