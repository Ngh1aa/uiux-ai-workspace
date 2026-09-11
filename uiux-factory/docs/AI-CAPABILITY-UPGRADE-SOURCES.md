# AI Capability Upgrade Sources — What to Find Next

This document lists the external capabilities and source material that would materially increase the UIUX Factory's ability to use its existing pipeline and `skills_UIUX` knowledge at full strength.

The goal is **not** to load every skill into every prompt. The Factory already routes and compiles stage-relevant skill evidence. The goal is to improve the intelligence, observation, visual judgment and remote-control surfaces around that routed knowledge.

## Priority model

- **P0** — major capability ceiling; solve before adding more prompt packs or decorative UI patterns.
- **P1** — strong quality/reliability multiplier after P0 is available.
- **P2** — useful workflow enhancement but not required for core design quality.

---

# P0 — Required for maximum practical leverage

## P0.1 Strong stage-routable reasoning + coding provider

### What to find

Official API/SDK documentation and working examples for a high-capability model that can be called from Python and supports:

- strong design/reasoning performance;
- high-quality frontend generation and repair;
- structured JSON output or reliable schema-constrained output;
- long-context input;
- stage-specific model selection;
- explicit token/cost/usage reporting;
- stable production API rather than a browser-only consumer interface.

A single provider may cover all stages, or different providers/models may own different stages.

### Factory integration target

Replace the current assumption that the AI layer is primarily a bounded free-tier refinement. Preserve explicit user configuration and never add a hidden paid fallback.

Desired routing example:

```text
research               -> reasoning/research model
ux_ia                   -> reasoning model
art_direction           -> strong multimodal/creative model
visual_composition      -> strong multimodal/creative model
implementation          -> strong coding model
repair                  -> strong coding + evidence model
visual_qa               -> vision-capable critic
```

### Acceptance criteria

- provider can be selected per stage;
- call/token/context budgets are configurable rather than hard-coded globally;
- usage is persisted without secrets;
- provider failure cannot silently fall back to an unapproved paid model;
- full structured artifacts still validate against Factory schemas;
- deterministic baseline remains available when AI is disabled.

---

## P0.2 Real multimodal Vision Creative Director

### What to find

Official multimodal API documentation/examples for a model that can inspect multiple screenshots/images and return structured feedback.

It must be able to reason about:

- hierarchy;
- composition;
- typography;
- spacing/rhythm;
- image crop and focal point;
- responsive transformations;
- brand fidelity;
- generic-template / generic-AI appearance;
- visible accessibility problems;
- visual regressions between before/after screenshots.

### Required output contract

The critic should return the existing Creative Director vocabulary:

```text
KEEP
REVISE
REMOVE
```

Every `REVISE` item should map to:

```text
priority
route
section
earliest_owner
problem
instruction
success_criteria
```

### Factory integration target

```text
BrowserQA screenshots
        -> Vision Creative Director
        -> CreativeDirective
        -> earliest owner stage
        -> regenerate/repair downstream
        -> BrowserQA again
        -> Vision review again
```

### Acceptance criteria

- consumes real screenshots, not only DOM heuristics;
- can compare at least desktop/tablet/mobile evidence for one route;
- produces schema-valid CreativeDirective data;
- visible P0/P1 defects override heuristic VisualCritic scores;
- every visual verdict cites screenshot/route/viewport evidence;
- no aesthetic PASS when screenshot evidence is unavailable.

---

## P0.3 Authenticated remote Factory connector

### Why it matters

The current Bridge is local. An external AI assistant cannot call `127.0.0.1` on the user's machine merely because the repository exists on GitHub.

### What to find

A secure reference implementation or platform for one of these patterns:

- authenticated remote MCP server;
- authenticated HTTPS API gateway to the local Factory;
- secure reverse tunnel plus signed API/session tokens;
- a ChatGPT-compatible connector/plugin that can invoke the Factory API.

The solution must not expose arbitrary local filesystem or shell access.

### Minimum remote actions

```text
health
start intelligence run
start build run
read job status/events
list artifacts
read/download safe artifacts
submit CreativeDirective
start revision run
cancel job (optional but desirable)
```

### Acceptance criteria

- TLS/HTTPS;
- strong authentication;
- allowlisted endpoints only;
- no secret/API key leakage to browser/model artifacts;
- rate limit / bounded queue;
- audit log;
- artifact path confinement;
- remote AI can prove the exact run id and runtime preset it operated on.

---

## P0.4 Model-readable browser evidence tools

### Current gap

The provider observation loop can read bounded artifacts and routed skill sources, but browser capabilities are primarily deterministic pipeline subsystems rather than rich read-only observation tools available to the reasoning model.

### What to find

Playwright/browser-agent examples that safely expose **read-only** observations such as:

- current route/title;
- screenshot;
- DOM excerpt;
- accessibility tree;
- computed style for selected elements;
- bounding boxes/intersections;
- console errors;
- failed network requests;
- image intrinsic/rendered dimensions;
- viewport metrics;
- element text/state.

### Acceptance criteria

- no arbitrary browser-side code execution from model text;
- allowlisted read-only tools;
- observations are bounded and persisted;
- model can request evidence before claiming PASS;
- tool calls are traceable in run evidence;
- BrowserQA remains deterministic owner of acceptance facts.

---

## P0.5 Just-in-time full-skill retrieval

### Principle

Do **not** put every `SKILL.md` into every prompt.

The correct target is:

> 100% of applicable skill knowledge is reachable, while only the necessary subset occupies active context.

### What to find

Agent-context or retrieval patterns that support:

- section-level skill indexing;
- exact source citations/hashes;
- model-requested expansion of an omitted section;
- retrieval only from skills already authorized/routed for the current stage unless the router explicitly expands scope;
- bounded multi-turn retrieval.

### Acceptance criteria

- mandatory rules always enter context first;
- omitted skill sections remain retrievable;
- model never claims an omitted section was read unless it was actually retrieved;
- coverage/evidence ledger records selected + retrieved sections;
- retrieval does not silently introduce a conflicting skill from another stage/domain.

---

## P0.6 Configurable provider budgets instead of a free-tier ceiling

### What to find

Patterns/config schemas for per-stage AI budgets:

- max calls;
- context size;
- output tokens;
- timeout;
- retry policy;
- provider/model preference;
- cost ceiling if the provider exposes cost data.

### Acceptance criteria

- `free`, `balanced`, and `quality-max` modes can be expressed without code changes;
- quality-max can allocate more observation/critique turns without stealing implementation budget;
- every run persists the selected budget policy;
- the user explicitly opts into any paid provider/budget.

---

# P1 — High-value quality multipliers

## P1.1 Evidence-rich reference browser

Find a browser/research implementation that can capture, for a reference URL:

- desktop + mobile screenshots;
- DOM/semantic outline;
- typography evidence;
- color evidence;
- layout measurements;
- media patterns;
- navigation/interaction patterns;
- source URL + capture timestamp.

Desired result: `ReferenceDNA` is grounded in visited pages rather than search snippets alone.

Do not auto-copy competitor assets or composition.

---

## P1.2 Lighthouse / Core Web Vitals laboratory gate

Find an integration for Lighthouse or equivalent lab performance tooling.

Target evidence:

- LCP;
- CLS;
- main-thread/blocking indicators;
- image/font loading opportunities;
- mobile/desktop profiles.

Keep field-vs-lab semantics explicit. Do not claim real-user CWV from local lab data.

---

## P1.3 Automated accessibility evidence

Find an `axe-core`/Playwright or equivalent integration for repeatable WCAG-oriented checks.

The machine gate should complement, not replace, keyboard/visual/manual review.

Useful evidence:

- accessible names;
- contrast where reliably measurable;
- landmark/heading structure;
- form labels;
- focusable controls;
- ARIA misuse;
- serious/critical violations.

---

## P1.4 Visual regression engine

Find a maintained screenshot comparison tool/library supporting:

- baseline/current comparison;
- configurable pixel threshold;
- masking dynamic areas;
- diff artifact output;
- viewport/route identity.

Use it for regression detection, not aesthetic scoring.

---

## P1.5 Media/art-direction asset pipeline

Find tooling or references for:

- image metadata inspection;
- smart crop/focal point storage;
- AVIF/WebP conversion;
- responsive `srcset` generation;
- image budget enforcement;
- duplicate/near-duplicate detection;
- broken/low-resolution asset detection.

If an image-generation provider is added, generated assets must be explicitly labeled as generated and must respect project/IP rules.

---

## P1.6 Design-token and component drift checker

Find a static/runtime approach that can detect:

- raw colors bypassing semantic tokens;
- repeated near-identical spacing/radius values;
- duplicate button/card variants;
- route-specific one-off components that should reuse shared contracts;
- CSS override-layer growth;
- obsolete selectors/components after redesign.

The tool should report drift; it should not auto-delete code without ownership evidence.

---

## P1.7 Real benchmark/evaluation corpus

Create or source a reusable evaluation set containing materially different website tasks, for example:

- luxury ecommerce;
- automotive/corporate;
- B2B SaaS;
- education;
- public service/government;
- editorial/media;
- service business;
- dashboard/application.

For each task preserve:

- brief;
- source truth;
- representative routes;
- required page roles;
- reference constraints;
- expected hard-rule evidence;
- human Creative Director verdict;
- final screenshot pack.

This is the only reliable way to know whether a new model/skill/provider actually improves the Factory.

---

# P2 — Workflow enhancements

## P2.1 Point-and-edit visual feedback

Find a safe browser overlay pattern that lets a human click a rendered element and create a structured revision containing route, selector/locator, screenshot crop and instruction.

Map the revision back to the earliest owning Factory stage instead of directly stacking CSS patches.

## P2.2 Figma/design-tool interoperability

Useful only after the web pipeline is stable.

Potential targets:

- export design tokens;
- export component inventory/spec;
- import approved brand tokens;
- attach screenshots/reference frames;
- preserve source/status of imported values.

Do not make Figma the source of truth automatically when code/runtime is the actual product owner.

## P2.3 Persistent artifact search

If run histories become large, add indexed search across approved run artifacts, decisions and benchmark evidence.

Do not use persistent retrieval as an excuse to inject unrelated old project context into a new project.

---

# Things NOT needed right now

Do not prioritize finding more of these until the P0 gaps are solved:

- generic landing-page template packs;
- bento/glassmorphism/aurora preset libraries;
- another giant master prompt that duplicates existing policies;
- more agent names without new tools/evidence/authority boundaries;
- heuristic aesthetic scores presented as human-quality judgment;
- large uncurated icon/animation libraries;
- a local model solely because it is local, unless it beats the current provider on the Factory benchmark.

The Factory already contains substantial orchestration and skill knowledge. The main ceiling is now **brain quality + visual observation + browser evidence + remote invocation + measurable evaluation**, not prompt quantity.

---

# Suggested sourcing order for the user

Find sources in this order:

1. **Strong reasoning/coding API** with structured output and long context.
2. **Strong multimodal vision API** suitable for screenshot critique.
3. **Secure remote MCP/connector pattern** so an external AI agent can invoke the local Factory.
4. **Read-only Playwright/browser tool server** suitable for agent observation.
5. **JIT context/skill retrieval pattern** with source-traceable section loading.
6. **Lighthouse integration**.
7. **axe-core + Playwright integration**.
8. **visual regression library**.
9. **image optimization/crop pipeline**.
10. **evaluation/benchmark framework** for comparing model/provider changes.

For every candidate source, record:

```text
name
repository/docs URL
license
maintenance status
language/runtime
API/tool contract
local vs cloud
supports images/vision?
supports structured output?
auth model
known limits
why it improves a specific Factory stage
```

Do not integrate a source only because it is popular. It must close a named capability gap and pass a benchmark before becoming canonical.
