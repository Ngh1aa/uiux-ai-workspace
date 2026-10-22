# A5.7 — Provider Advisory Context Firewall

Status: **CANONICAL RUNTIME CONTRACT**

A5.7 adds a final provider-boundary sanitizer for historical advisory memory. It does not replace A5.5/A5.6 routing; it provides defense-in-depth at the point where provider requests are created.

## Problem closed by A5.7

A5.6 correctly routes post-render quality recall by stage, but provider requests still accept `task_context` as input. A stale, malformed or accidentally polluted advisory payload must not reach a model merely because it exists upstream.

A5.7 therefore treats provider-facing advisory memory as deny-by-default structured data.

## Executable ownership

```text
uiux-factory/core/runtime/flow_os/provider.py
```

The canonical `ProviderStageRequest` sanitizes its `task_context` during construction before any OpenAI, Anthropic, command or custom provider receives the request.

## Canonical boundary

```text
managed runtime / stage routing
→ candidate task_context
→ ProviderStageRequest
→ advisory context firewall
→ bounded provider-facing task_context
→ provider
```

The firewall is not a planner, evaluator or memory store.

## Evaluation-memory projection

`prior_evaluation_insight` is retained only when it is a structured advisory payload that declares:

```text
advisory_only    = true
authority_effect = none
gate_effect      = none
```

The provider receives a rebuilt allowlisted projection containing bounded aggregate fields only, such as:

- schema version;
- flow id;
- sample size;
- passed / failed-or-blocked counts;
- pass rate;
- average replans;
- bounded recurrent failure channels;
- bounded observed evidence types;
- bounded matched signature metadata.

Unknown fields and historical prose are discarded.

## Quality-memory projection

`prior_quality_insight` is additionally restricted by stage agent:

```text
implementation → allowed
qa             → allowed
research       → denied
```

A quality payload is retained only if it declares the canonical A5.5 trust metadata and all authority/flow/replan/gate/evidence/merge/release effects are `none`.

The provider receives only bounded categorical rows:

```text
evaluator
requirement_id
outcome
applicable
occurrences
```

The following never cross this boundary:

- rationale or model prose;
- prompts/provider summaries;
- screenshots or image paths;
- DOM/HTML;
- source code;
- test targets;
- raw evidence artifacts;
- fingerprints;
- arbitrary unknown fields.

## Poisoned-effect rejection

If an advisory payload claims any authority or release effect, the entire payload is dropped instead of partially trusting it.

Examples that must be rejected include:

```text
authority_effect = raise_to_production
release_effect   = auto_release
flow_effect      = change_flow
```

Current task context remains available; only the malformed historical advisory payload is removed.

## Relationship to A5.4–A5.6

```text
A5.4  learn safe normalized quality patterns
A5.5  recall bounded quality aggregates
A5.6  route quality recall only to relevant stages
A5.7  sanitize advisory memory again at provider boundary
```

A5.7 is intentionally redundant with earlier protections. The managed controller decides whether memory should be routed; the provider boundary independently guarantees what shape can leave the runtime.

## Authority boundary

The firewall cannot:

- choose or change the flow;
- alter role authority;
- alter tool permissions;
- enter canonical replanning policy;
- satisfy or waive gates;
- convert historical memory into current evidence;
- approve merge or release.

## Failure behavior

Malformed advisory memory is fail-open for execution and fail-closed for provider exposure:

```text
bad historical memory → drop memory payload → continue current stage
```

A malformed advisory payload does not fail an otherwise valid run.

## Verification

Regression coverage must prove at least:

1. research provider requests never contain quality memory;
2. implementation/QA requests retain valid bounded quality memory;
3. raw/unknown evaluation-memory fields are stripped;
4. raw/unknown quality-memory fields are stripped;
5. invalid authority/release effect declarations drop the payload;
6. malformed memory is removed without changing current task fields;
7. provider requests detach their sanitized top-level context from later upstream mutation.

## Trust model

```text
current task/source/runtime evidence = current-run truth inputs
historical evaluation memory         = bounded advisory aggregate
historical quality memory            = bounded stage-aware advisory aggregate
provider-facing historical memory    = sanitized projection only
```

Historical memory may guide inspection. It never proves current truth and never carries runtime authority.