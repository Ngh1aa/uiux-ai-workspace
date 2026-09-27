# Evidence Provenance Contract

## Purpose

A `VERIFIED` label is not sufficient by itself. Material measured facts used by a compiled spec should retain a path back to the browser evidence that produced them.

The provenance chain is:

```text
reference-evidence.v1.json
        ↓ SHA-256
stable evidence catalog
        ↓ catalog SHA-256 + EVID-* anchors
02-FULL-BUILD-SPEC.md
        ↓ SHA-256
spec-manifest.json
        ↓
implementation / browser QA / visual QA / repair
```

`spec-manifest.json` does not need to duplicate the entire catalog. Its frozen-spec hash transitively binds the source artifact hash and catalog hash because those values are embedded in the frozen spec.

## Stable evidence IDs

Each measured fact receives an ID:

```text
EVID-0123456789abcdef
```

The ID is derived from the normalized measurement identity:

- evidence status;
- kind/source type;
- source URL;
- viewport;
- state/checkpoint;
- selector/target;
- property;
- measured value;
- source locator inside `reference-evidence.v1.json`.

The following are deliberately excluded from the ID:

- capture timestamp;
- local artifact path;
- source artifact hash.

Therefore an equivalent rerun can retain the same evidence ID even though the run directory or timestamp changes.

## Evidence status rules

- browser DOM/computed-style/runtime measurements: `VERIFIED`;
- screenshot palette clustering: `INFERRED`;
- new design choices: `PROPOSED`;
- missing context required only to proceed: `ASSUMED`;
- insufficient evidence: `UNKNOWN`;
- irrelevant requirement: `N/A_JUSTIFIED`.

Never use an `INFERRED` evidence ID as if it proves authored CSS, animation math, brand tokens, or source ownership.

## Scope rule

An evidence anchor proves only its recorded scope.

Example:

```text
[[evidence:EVID-...]] VERIFIED — `.hero-title` font-size=168px @ desktop:1440x1000
```

This does **not** prove that 168px is used:

- at 390px;
- in another route;
- after a state transition;
- in the source stylesheet rather than as the resolved computed value.

The Spec Writer must not silently generalize scope.

## Tamper/staleness rule

`ReferenceBoard.evidence_sha256` must match the current bytes of the declared deep evidence artifact before a catalog can be compiled.

If the digest does not match:

```text
STALE / TAMPERED
→ reject provenance
→ do not emit VERIFIED anchors from that artifact
→ continue only with other grounded sources or UNKNOWN
```

Do not regenerate a matching hash merely to make the gate pass.

## Prompt contract

When deep evidence is available, `02-FULL-BUILD-SPEC.md` must contain:

- deep evidence artifact path;
- source artifact SHA-256;
- evidence catalog SHA-256;
- bounded high-priority `[[evidence:EVID-*]]` anchors;
- a rule forbidding evidence-scope widening.

Implementation and QA prompts must carry the same artifact/catalog lineage.

## Profile policy

Provenance does not change profile semantics.

- `pixel_faithful`: measured reference anchors may become strict fidelity requirements when the spec explicitly promotes them into the preserve contract.
- `preserve_and_extend`: anchors constrain only protected owners/surfaces; new work remains `PROPOSED`.
- `redesign`: anchors preserve product/content/behavior truth when relevant but do not make old pixels a visual target.
- `original_design`: reference evidence is inspiration/research evidence only unless the project contract explicitly adopts a fact.

Reference evidence is never permission to copy proprietary media, code, copy, or composition.
