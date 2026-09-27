# Spec Writer Profile Routing

Prompt Compiler is universal; its output schema is **profile-aware**.

Do not force every project into a pixel-faithful HTML/CSS/JS reconstruction template.

## Profiles

### `pixel_faithful`
Use when a live/reference implementation is the authority and the requested goal is to reproduce it with minimal creative deviation.

Typical evidence:
- live site / Figma dev-mode / extracted DOM + computed CSS;
- exact motion/state samples;
- explicit clone/rebuild/fidelity request.

Primary emphasis:
- exact assets/provenance;
- DOM/component/source order when material;
- exact tokens/computed values;
- responsive breakpoints;
- interaction/motion math;
- choreography acceptance criteria.

Creativity is constrained. Unknown values stay `UNKNOWN` or `INFERRED`.

### `preserve_and_extend`
Use when part of an existing implementation must remain intact while new pages, states, content, interactions, or visual surfaces are added.

Primary emphasis:
- preservation levels;
- exact protected owners;
- safe extension boundaries;
- new surfaces marked `PROPOSED`;
- regression QA against protected behavior.

A single surface may contain VERIFIED preserved behavior and PROPOSED visual/content decisions. Evidence states attach to values/decisions, not whole sections.

### `redesign`
Use when product truth, data contracts, routes, or core journeys remain authoritative but UX/visual composition may materially change.

Primary emphasis:
- what product truth survives;
- verified pain points/gaps;
- research + art direction;
- revised IA/component/state system;
- explicit migration and regression boundaries.

Do not preserve DOM/CSS merely because it exists.

### `original_design`
Use when there is no authoritative existing implementation to preserve.

Primary emphasis:
- research and product framing;
- explicit design rationale;
- proposed tokens/layout/type/motion values;
- responsive behavior;
- prototype/production scope;
- QA and delivery contract.

Deliberate new design decisions are `PROPOSED`, not `ASSUMED`.

## Routing precedence

1. Explicit user instruction.
2. Existing preservation contract / project context.
3. Repository/reference evidence.
4. Goal language.
5. `original_design` only when no authoritative existing implementation is being preserved.

Do not infer `pixel_faithful` merely because a reference exists.

## Blocking unknowns

Most missing details should not stop compilation. Use `ASSUMED`, `PROPOSED`, `UNKNOWN`, or `N/A_JUSTIFIED` as appropriate.

Stop before implementation only when an unknown can materially change one of:
- architecture;
- preservation boundary;
- asset/legal ownership;
- core journey/product behavior;
- real-vs-simulated system behavior;
- release authority.

Label these as `BLOCKING_UNKNOWN` in the spec's unresolved section.

## Evidence vocabulary

- `VERIFIED` — direct project/runtime/source evidence.
- `INFERRED` — reasoned conclusion from evidence.
- `ASSUMED` — temporary context assumption needed to proceed.
- `UNKNOWN` — insufficient evidence.
- `PROPOSED` — deliberate new product/design/architecture decision.
- `N/A_JUSTIFIED` — not applicable to the declared scope.

Requirement lifecycle remains separate:
- `DONE_VERIFIED`
- `PENDING_FUTURE_PHASE`
- `BLOCKED`
- `N/A_JUSTIFIED`

## Universal rule

Mostar and every other example are quality-bar examples for **resolution and grounding only**. They are never routing defaults or content templates.