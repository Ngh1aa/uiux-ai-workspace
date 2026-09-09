# DeepSeek Harness lessons adopted by UIUX Factory

This document records the architectural ideas studied from the public `deepseek-ai/deepseek-harness` repository and how they were adapted into the existing Python/MetaGPT UIUX Factory. It is an architecture study, not a source-code vendor or a claim of API compatibility.

## Study baseline

- Upstream repository: `https://github.com/deepseek-ai/deepseek-harness`
- Studied revision: `b2e3b2a0125854567a4a5fcba75782e42fe84901`
- Upstream release at that revision: `dsh@0.1.5-alpha.2`

Primary source areas inspected:

- `docs/cordis-primer.md`
- `docs/subsystems/extensions.md`
- `packages/core/session/README.md`
- `packages/preset/agent-presets/README.md`
- `packages/preset/agent-presets/presets/cordis/agent.cordis.yml`
- `packages/preset/agent-presets/presets/standard/agent.cordis.yml`
- `packages/skill/skill/README.md`
- `packages/skill/tool-skill/README.md`

## 1. Plugin architecture

### DeepSeek lesson

Cordis treats a context as a service repository. Plugins declare stable service dependencies instead of depending on manual boot order, communicate through typed events, and install reversible effects so reload/teardown can unwind registrations predictably.

### Factory adaptation

`core/runtime/plugin_runtime.py` adds a deliberately small Python plugin kernel:

- `PluginSpec` declares `provides`, `requires`, tools, and stage skill contributions.
- Dependencies are resolved through stable capability names rather than concrete imports.
- Mount order is dependency-derived.
- Activation may return a disposer; disposal runs in reverse order.
- Duplicate/ambiguous capability providers and dependency cycles fail fast.
- No model-authored Python is evaluated.

The shipped Factory runtime plugins are capability owners:

- `session-events`
- `artifact-evidence`
- `skill-composition`
- `web-research`
- `browser-evidence`
- `semantic-visual-qa`
- `creator-inspector`

The goal is not to make every class a plugin. The goal is to put replaceable runtime seams around capabilities that benefit from composition.

## 2. Event/session log

### DeepSeek lesson

Harness sessions are append-only logs of typed events. Model-visible history and other views are projections from that record. The log supports inspect/replay/fork, and compaction or replacement does not erase historical evidence.

### Factory adaptation

`core/events/run_session_log.py` upgrades the existing `events.jsonl` into a first-class run/session record:

- contiguous sequence validation;
- append-only JSON events;
- immutable snapshots;
- `event_at`;
- replay;
- reducer-based projections;
- run-state projection;
- lineage-preserving fork to a child run log.

`RunContext` now writes lifecycle facts to the event log:

- `run.created`
- `stage.started`
- `stage.completed`
- `artifact.registered`
- `run.failed`
- `run.completed`

`run.json` remains the convenient current-state snapshot. The event log is the durable chronology that can reconstruct lifecycle state.

## 3. Creator mode

### DeepSeek lesson

Harness Creator mode is Standard mode plus runtime inspection, plugin experiments, and preset-authoring guidance. Its shipped Cordis preset explicitly distinguishes host-level capabilities from per-agent composition and treats self-modification as a strong trust boundary.

### Factory adaptation

The Factory adopts the useful introspection/authoring loop but deliberately narrows the trust boundary:

- inspect plugin and preset inventory;
- preview a resolved composition;
- validate a preset, including every composed skill path, before a run starts;
- copy an existing preset into a user-writable root;
- delete only user-authored presets;
- never mutate shipped presets;
- never evaluate arbitrary model-written Python plugins.

CLI:

```bash
python creator.py inventory
python creator.py preview visual-first
python creator.py validate research-heavy
python creator.py copy standard my-team-preset --name "My Team Preset"
python creator.py delete my-team-preset
```

User-authored presets live under:

```text
uiux-factory/.runtime-presets/
```

That directory is ignored by Git because it is local deployment/user configuration, not shipped product source.

## 4. Tool + skill composition

### DeepSeek lesson

A Harness agent preset is the plugin composition a session runs: the selected plugins determine tools, prompt sections, skills, and capabilities. Skill providers merge into a registry while model-facing consumers decide how to expose/load them.

### Factory adaptation

The Factory keeps its canonical `ProfessionalWebsiteFlow` and `AdaptiveSkillRouter`. Runtime composition is an additional bounded layer, not a replacement:

```text
canonical website flow skills
        +
runtime plugin stage skills
        +
runtime preset stage skills
        =
compiled stage skill context
```

Tool composition is enforced by the existing provider observation loop, not merely recorded as metadata:

- `artifact-evidence` enables `list_artifacts` and `read_artifact`;
- `skill-composition` enables `read_skill_source`;
- the active runtime exposes only the intersection of its composed tools and the bounded read-only provider tool contract;
- the specialist system prompt receives that exact runtime-enabled set;
- a request for a tool not enabled by the active preset is not executed and is recorded as `runtime_tool_not_enabled`.

Other tool names such as `web_search`, `browser_render`, `visual_review`, `session_inspect` and Creator operations remain capability inventory/seams for their owning deterministic subsystems; they are not silently exposed to the model observation loop.

A runtime capability must be present before the stage that needs it:

- `skills.compose` before specialist execution;
- `research.web` before Research;
- `browser.qa` before rendered QA;
- `visual.qa` before semantic visual acceptance.

A custom preset that removes a required pipeline capability fails explicitly instead of silently degrading. Missing composed skill paths are rejected during preset composition, before the pipeline consumes the preset.

## 5. Runtime presets

### DeepSeek lesson

Harness gives each session one preset composition. A running session does not freely swap presets after producing history because previously logged tool calls may refer to capabilities the new composition no longer contains. Shipped presets are treated as installation-owned definitions; authoring starts by copying rather than editing them.

### Factory adaptation

Every normal Factory run now has `runtime_preset` in `run.json` and `runtime-composition.json`.

Shipped presets:

### `standard`

Canonical Factory capabilities: session events, bounded artifact evidence, skill composition, live research, browser evidence and semantic visual QA.

### `visual-first`

Standard capabilities with additional visual-direction, signature-moment, media-art-direction and prototype-quality skill pressure.

### `research-heavy`

Standard capabilities with extra benchmark, UX-metrics, audience-intent and journey skill pressure before design.

### `creator`

Standard capabilities plus creator inspection/preset-authoring capability and Anthropic `skill-creator` guidance during research.

Select one on a new CLI run:

```bash
python run.py "Design a luxury fragrance ecommerce site" --runtime-preset visual-first
```

Creative-review revisions inherit the source run's runtime preset. They cannot swap composition mid-history through the CLI.

### Design Workbench

The Bridge now exposes the validated preset catalog in `/health`. The Workbench runtime selector is populated from that catalog and injects the selected `runtime_preset` into each `/run` or `/intelligence` request. The Bridge validates the preset by composing it before a job is accepted and passes the exact id to `run.py --runtime-preset`.

This closes the UI/backend contract: selecting `Visual First` in the Workbench cannot silently fall back to `standard`.

The live run card also exposes the active preset and direct runtime evidence links for:

- `runtime-composition.json`;
- `flow-plan.json`;
- `events.jsonl`.

## Evidence artifacts

A composed run now records:

- `events.jsonl` — append-only run/session chronology;
- `runtime-composition.json` — preset, mounted plugins, capabilities, tools and stage skill overlays;
- `flow-plan.json` — canonical flow plus the runtime composition snapshot;
- `run.json` — current run snapshot including `runtime_preset`.

These artifacts are intended to make the Factory inspectable without weakening its existing stage contracts or quality gates.

## Deliberate non-goals

This change does **not**:

- port Cordis into Python;
- vendor DeepSeek Harness source;
- execute arbitrary dynamic plugin code;
- replace MetaGPT roles;
- allow presets to skip canonical design/QA gates;
- let a runtime preset override explicit project/brand truth;
- claim DeepSeek API compatibility.

The architecture lesson is composability and traceability, not framework imitation.
