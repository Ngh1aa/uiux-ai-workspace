# Spec-First Execution Contract

This contract defines how UIUX Factory must behave when a task is substantial enough that implementation should be preceded by an explicit, project-specific prompt/specification.

## Core rule

For substantial build, redesign, rebuild, extension, migration, or release work:

```text
PROJECT / REFERENCE / REPOSITORY
        ↓
AUDIT + RESEARCH + DESIGN INTELLIGENCE
        ↓
COMPILE PROJECT-SPECIFIC PROMPT PACK
        ↓
SELF-REVIEW + CONSISTENCY GATE
        ↓
FREEZE SPEC AS IMPLEMENTATION SOURCE OF TRUTH
        ↓
IMPLEMENTATION AGENT READS THE SPEC
        ↓
RENDERED QA / ROOT-CAUSE REPAIR
        ↓
RELEASE
```

The system must not jump directly from vague user intent to broad implementation when a concrete specification can materially reduce ambiguity or regression risk.

## Mostar is only a resolution example

`examples/mostar-guide.md` is a **quality-bar example for specificity, grounding, exactness, and acceptance criteria**.

It is NOT:

- a required sitemap;
- a required section list;
- a required technical stack;
- a default deployment target;
- a default visual direction;
- a source of selectors, routes, animations, assets, or file names for other projects.

Never copy Mostar-specific facts into another project unless the target repository itself contains them.

The transferable lesson is the **resolution of the specification**, not the content of the example.

## Execution modes

### `compile_only`

Use when the user explicitly asks only for a prompt/specification or says not to implement yet.

Output the prompt pack and stop.

### `compile_then_execute`

Use when the user asks the system to actually build/redesign/extend the project and the task is substantial.

The Factory must:

1. compile the prompt pack first;
2. run the pack consistency gate;
3. persist the pack as run artifacts;
4. mark the full build spec as the implementation source of truth;
5. feed the approved/frozen spec to implementation planning and code generation;
6. feed the QA/remediation prompt to the quality loop;
7. report any implementation deviation from the compiled spec explicitly.

No separate user approval is required between compile and implementation unless the user asks for a review gate or the compiled spec exposes a genuinely blocking UNKNOWN/conflict.

## Prompt pack

The canonical pack is:

```text
00-PROJECT-CONTEXT.md
01-RESEARCH-PROMPT.md
02-FULL-BUILD-SPEC.md
03-IMPLEMENTATION-PROMPT.md
04-QA-REMEDIATION-PROMPT.md
```

For simple work, the Factory may collapse the pack to `02-FULL-BUILD-SPEC.md` only when doing so does not remove material implementation or QA context.

## Detail-resolution contract

A compiled prompt must be **specific enough that a second capable agent can execute it without hidden chat history**.

The spec should include exact values and concrete snippets when those values are known or intentionally proposed.

### Repository and architecture

When applicable, include exact:

- repository root/canonical app root;
- entry points;
- routes;
- file paths;
- component/DOM owners;
- selectors/classes/IDs;
- functions/state owners;
- API/schema owners;
- build/runtime commands;
- protected files;
- allowed-change files;
- new files.

### Visual system

When applicable, include exact:

- typography families/weights/sizes/line heights/tracking;
- color tokens/hex values;
- spacing/grid/container values;
- breakpoints;
- media crop/focal rules;
- component states;
- motion timings/easing/ranges;
- hover/focus/keyboard/touch behavior;
- reduced-motion behavior.

### Deployment

If deployment is DUE NOW, do not write merely “deploy to Vercel/GitHub Pages”. Specify the actual contract, for example:

- config file path;
- config contents or exact keys;
- framework preset;
- build command;
- output directory;
- base/relative-path rules;
- GitHub Pages source setting;
- workflow path and steps;
- environment variables and ownership;
- release verification.

If a literal config snippet is appropriate, include it in the spec.

### SEO / metadata

If applicable, define exact:

- title/description ownership;
- OpenGraph tags;
- theme color/favicon;
- canonical behavior;
- `robots.txt`;
- `sitemap.xml`;
- structured data when justified.

Use literal markup examples when that removes ambiguity. Do not fabricate final marketing copy unless it is explicitly `PROPOSED`.

### Accessibility

If applicable, specify exact semantics and behaviors rather than “make accessible”, including:

- landmark/heading structure;
- skip-link placement;
- focus-visible behavior;
- keyboard interactions;
- aria/name relationships;
- alt/decorative-image rules;
- reduced-motion behavior;
- touch-target constraints;
- Axe/Lighthouse gates where due now.

### QA

QA items must be binary/verifiable where possible. Include concrete checkpoints such as:

- routes that must load;
- viewport widths;
- target selectors/states;
- scroll/animation checkpoints;
- console/network expectations;
- accessibility thresholds;
- deployment status;
- expected file/asset counts when they are part of the contract.

Bad:

```text
[ ] Looks polished
[ ] Animation is smooth
```

Good:

```text
[ ] No horizontal overflow at 390 / 768 / 1440 px.
[ ] All declared routes return <400.
[ ] No serious or critical Axe violations on representative routes.
[ ] No project-code console errors during the critical journey.
```

### Deliverables

The spec must list exact outputs when applicable:

- files to create/change;
- routes/pages/states;
- docs;
- assets;
- tests;
- screenshots/evidence;
- workflows;
- PR/release output.

Do not use vague deliverables such as “finished website”.

## Evidence labels

Use:

- `VERIFIED` — directly evidenced by source/runtime/tool/authoritative source;
- `INFERRED` — reasonable conclusion from evidence;
- `ASSUMED` — temporary assumption needed to continue;
- `UNKNOWN` — insufficient evidence;
- `PROPOSED` — new design/product/architecture decision intentionally introduced by the compiler;
- `N/A_JUSTIFIED` — intentionally not applicable.

A chosen design value is normally `PROPOSED`, not `ASSUMED`.

Example:

```text
PROPOSED — hero font-size: 96px
ASSUMED — primary review viewport is desktop because no responsive scope was declared
```

## Spec freeze and lineage

Before implementation begins in `compile_then_execute` mode:

1. persist the prompt pack;
2. record the compiled spec path;
3. record a content hash for `02-FULL-BUILD-SPEC.md` when the runtime supports hashing;
4. implementation must read that exact artifact;
5. QA must evaluate against that exact artifact;
6. if the spec changes materially, downstream implementation/QA evidence is stale and must be rerun from the earliest affected stage.

## Implementation consumption rule

The implementation agent must receive the compiled spec directly in its instruction/context.

It must not rely on:

- hidden conversation history;
- memory of earlier design discussion;
- a parallel interpretation of the original user request that conflicts with the spec.

Source-of-truth order during implementation:

1. user's latest explicit correction;
2. frozen compiled build spec;
3. project contracts/current repository truth;
4. upstream design artifacts;
5. inference;
6. assumption.

## QA consumption rule

The QA/repair stage must compare the rendered implementation against:

1. the frozen build spec;
2. preserve/change contract;
3. rendered/browser evidence;
4. declared responsive scope;
5. current release authority.

If implementation and spec disagree, do not weaken QA. Identify the earliest responsible owner, repair there, and rerun affected downstream gates.

## Compile gate

Before implementation is allowed to start, confirm:

- [ ] prompt pack exists;
- [ ] goal/scope is consistent across the pack;
- [ ] preserve/change contracts do not conflict;
- [ ] exact named selectors/functions/routes are VERIFIED or clearly PROPOSED;
- [ ] deployment assumptions match the real hosting model;
- [ ] responsive scope is explicit;
- [ ] QA criteria are measurable;
- [ ] current-phase UNKNOWNs are either non-blocking or surfaced as blockers;
- [ ] no Mostar/example-specific requirement leaked into an unrelated project;
- [ ] the implementation prompt explicitly instructs the agent to read `02-FULL-BUILD-SPEC.md` first.

Only after this gate passes may `compile_then_execute` continue into implementation.