# UIUX Factory Prompt OS v1

Prompt OS v1 is the stable spec-first contract for turning a short project goal plus repository/reference evidence into an executable prompt pack, implementation, rendered QA and root-cause repair loop.

## Minimal invocation

Compile only:

```text
@GitHub use uiux-ai-workspace.

repo = https://github.com/OWNER/PROJECT
goal = [1–3 sentences]
mode = compile_only
```

Compile then execute:

```text
@GitHub use uiux-ai-workspace.

repo = https://github.com/OWNER/PROJECT
goal = [1–3 sentences]
mode = compile_then_execute
```

The user does not need to pre-author a multi-thousand-word Mostar-style prompt. Prompt OS compiles project-specific detail from evidence and approved design intelligence first.

## Stable v1 pipeline

```text
repo / brief / reference
→ reference analysis + deep evidence extraction
→ motion / interaction sampling when applicable
→ research / UX / art direction
→ profile-aware Spec Writer
→ canonical five-file prompt pack
→ consistency gate
→ freeze 02-FULL-BUILD-SPEC.md
→ implementation reads frozen spec
→ BrowserQA
→ profile-aware reference visual QA
→ semantic VisualCritic
→ evidence contract
→ root-cause repair / re-render
→ release within authority
```

## Four specification profiles

### `pixel_faithful`
Use only when exact reconstruction is explicitly requested. Verified reference evidence dominates. Comparable authoritative reference screenshots are required to claim visual fidelity.

### `preserve_and_extend`
Protect proven existing owners/behaviors while adding or changing scoped surfaces. A reference alone does not turn the entire page into a pixel-match target.

### `redesign`
Preserve product/data/journey truth required by the frozen spec while allowing material UX/visual change. Old-reference pixel similarity is not a success metric.

### `original_design`
Greenfield/original work. Deliberate design values are `PROPOSED`, not `ASSUMED`; visual acceptance is driven by research, frozen art direction/spec, rendered QA and human review.

## Evidence model

Material claims use:

```text
VERIFIED
INFERRED
ASSUMED
UNKNOWN
PROPOSED
N/A_JUSTIFIED
```

Deep browser evidence records stable `EVID-...` IDs with source URL/artifact, viewport, runtime state, selector/property/value and evidence class. Inferred screenshot palette or choreography interpretation never silently becomes verified CSS/runtime truth.

## Canonical prompt pack

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

The Full Build Spec is the frozen implementation source of truth. Material spec changes invalidate affected downstream implementation/QA evidence.

## Reference Evidence Extractor

When a live reference can be inspected, Factory can record:

- sequential DOM/source order;
- selected computed styles and custom properties;
- asset/font URLs and intrinsic metadata;
- CSS media queries and declared colors;
- screenshots + hashes;
- screenshot-derived palette as `INFERRED`;
- scroll checkpoints;
- sampled transform/opacity/filter/geometry/custom-property state;
- Web Animations API observations;
- non-destructive interaction-listener evidence.

This is measurement, not permission to copy.

## Reference-aware visual QA

Profile determines whether reference distance matters:

```text
pixel_faithful      → strict reference gate
preserve_and_extend → strict only for explicit protected visual surfaces
redesign            → spec/new-art-direction gate
original_design     → spec/quality-rubric gate
```

Machine pixel metrics are browser-output heuristics. They do not replace semantic review or human visual veto.

## Four-profile benchmark

Run from `uiux-factory/`:

```bash
python scripts/run_prompt_os_v1_benchmark.py
```

The benchmark verifies all four profiles and prevents regressions such as `reference exists => clone` or negated wording such as `nothing to preserve` being misclassified.

## Release verifier

Run from `uiux-factory/`:

```bash
python scripts/verify_prompt_os_v1.py
```

The verifier checks the stable v1 capability manifest, required source/docs/contracts, profile set, pipeline ordering, canonical outputs and four-profile benchmark.

## v1 limitations

Prompt OS v1 deliberately does **not** claim:

- that arbitrary Figma URLs can always expose dev-mode DOM/CSS data;
- that screenshot metrics prove semantic/UX correctness;
- that visual QA can replace human review for subjective craft;
- that `preserve_and_extend` currently has universal per-selector target crop capture for every framework;
- that a build/deploy success proves rendered fidelity;
- that production/backend capability exists when a prototype only simulates it;
- that every task needs the full five-file prompt pack.

## Release discipline

A Prompt OS v1 capability is considered present only when its machine-readable manifest entry is backed by source + contract tests. Do not edit the manifest to claim a capability before its implementation/gates exist.

The release contract is intentionally narrower than the entire UIUX Factory: v1 stabilizes the **evidence → spec → implementation → rendered verification** chain, not every possible product-development workflow.
