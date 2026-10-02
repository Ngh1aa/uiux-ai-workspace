# A48.3 — Provider Artifact Bridge Contract

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A48.2 Provider Capability Reconciliation

## 1. Purpose

A48.2 proved that the existing Factory provider lane and managed provider lane cannot be substituted directly because Factory callers require raw artifact text while the canonical managed `ProviderStageResponse` had no artifact field.

A48.3 removes only that contract blocker. It extends the canonical response envelope so a managed provider can optionally carry bounded raw output without weakening evidence, gate, routing or release semantics.

Canonical owner remains:

```text
core/runtime/flow_os/provider.py::ProviderStageResponse
```

No third provider response type is introduced.

## 2. Contract

`ProviderStageResponse` now supports:

```text
artifact: str | None = None
```

The field is:

- optional;
- raw text, preserved exactly when present;
- bounded by `MAX_PROVIDER_ARTIFACT_CHARS = 4_000_000`;
- rejected when present as an empty string;
- rejected when non-string;
- omitted from `to_dict()` when `None`, preserving the legacy serialized shape.

`provider_response_schema()` exposes `artifact` as an optional nullable string with the same length bound. It is deliberately not added to the schema `required` list.

## 3. Truth / evidence boundary

Artifact content is provider/model-authored output. It is not runtime evidence.

Hard invariant:

```text
artifact != evidence
artifact != gate PASS
artifact != trusted observation
artifact != release readiness
```

A response with:

```text
status = PASS
artifact = "..."
evidence = []
```

continues to fail validation exactly as before because canonical PASS still requires concrete evidence.

A48.3 does not add artifact values to `response.evidence`, does not create `EvidenceRecord`, does not create provenance IDs and does not call any gate/release evaluator.

## 4. Backward compatibility

Existing providers are not required to emit `artifact`.

Legacy payload:

```json
{
  "status": "CONTINUE",
  "actions": [],
  "summary": "Need another observation.",
  "evidence": [],
  "replan_signal": null
}
```

still parses successfully and serializes back to the same five-field shape. This avoids forcing OpenAI, Anthropic, command and scripted provider fixtures to change before an adapter actually needs artifact output.

## 5. Provider prompt boundary

The canonical system/provider prompt now states that the optional artifact field is untrusted raw output and never counts as evidence or satisfies a gate.

This is guidance only. The executable truth remains the response validator and runtime evidence/gate machinery.

## 6. Non-goals

A48.3 does not:

- modify `core/runtime/free_provider.py`;
- replace `FreeProvider.complete(...)`;
- add an async/sync compatibility adapter;
- change manager provider construction;
- change provider defaults;
- change fallback/call-budget/history semantics;
- execute network calls;
- mark a generated artifact as verified;
- merge provider execution lanes.

Those concerns belong to A48.4+.

## 7. Acceptance criteria

A48.3 is complete when:

- [x] canonical `ProviderStageResponse` accepts optional artifact text;
- [x] legacy payloads remain valid and keep their serialized shape;
- [x] artifact text is preserved exactly;
- [x] artifact size is bounded;
- [x] empty/non-string/oversized artifacts fail closed;
- [x] schema exposes artifact as optional, not required;
- [x] artifact cannot satisfy the existing PASS evidence requirement;
- [x] provider prompt states artifact has no evidence/gate authority;
- [x] no Factory provider, manager or default path changes in this task;
- [ ] final PR head passes UIUX Factory CI, A20, A13 and A14.

## 8. Handoff

After A48.3 is green and merged, A48.4 may implement an **opt-in async compatibility adapter** that preserves the existing Factory `complete(...) -> str` contract while delegating to a managed provider.

That adapter must preserve async safety, call-budget/history semantics and raw artifact parity, and must remain opt-in until A48.5 parity/dogfood proves equivalence.