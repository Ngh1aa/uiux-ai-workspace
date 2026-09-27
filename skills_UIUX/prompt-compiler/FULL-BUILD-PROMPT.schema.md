# Full Build Prompt Schema

Use this schema for the compiled `02-FULL-BUILD-SPEC.md` output.

The result must stand alone. A second implementation agent should not need hidden chat history to understand the project.

# [PROJECT NAME] — Full Prototype / Product Build Prompt

> **Goal:** [One concise outcome statement.]
>
> **Mode:** specification only unless authority explicitly says otherwise.
>
> **Evidence rule:** distinguish VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED.

---

## 0. Mission

State:

- what the project is becoming;
- what must remain intact;
- the target experience/outcome;
- current phase;
- whether this is build, extension, redesign, or rebuild;
- declared responsive scope;
- declared release authority.

Avoid generic goals such as “make it modern.”

---

## 1. Source of truth

List in precedence order:

1. latest explicit user requirement;
2. target project contracts/context;
3. canonical code/design source;
4. tests/runtime/deploy evidence;
5. applicable UIUX Factory rules;
6. external authoritative sources;
7. inference/assumption.

Call out any conflicts.

---

## 2. Current verified architecture

Describe only material verified facts:

- repository root / canonical app root;
- stack/runtime;
- entry points;
- routes/sitemap;
- key files/modules;
- current DOM/component owners;
- design tokens;
- key animation/interaction owners;
- current responsive rules;
- deployment configuration;
- current known QA evidence.

Use exact names where available.

---

## 3. Immutable / preserve contract

This section is mandatory for extension/redesign of an existing working project.

Group by preservation level:

### 3.1 Byte-for-byte preserve

Use only when explicitly required and verifiable.

### 3.2 Behavior preserve

Functions/algorithms/interactions may move only if behavior remains identical and the requirement permits it.

### 3.3 API / DOM contract preserve

Selectors, IDs, routes, public contracts, data attributes, component inputs, URL behavior.

### 3.4 Visual-DNA preserve

Signature composition, typography, art direction, motion feel, imagery treatment.

### 3.5 Content / data preserve

Validated copy, facts, URLs, labels, assets, business/domain information.

For each item, state exact owner/file/selector/function when known.

Explicitly define what may be **added** without contaminating protected core logic.

---

## 4. Current problems and gaps

For each evidence-backed issue:

```text
CURRENT
→ PROBLEM
→ IMPACT
→ PROPOSED RESOLUTION
```

Separate:

- verified bugs;
- UX gaps;
- missing scope;
- technical/deploy gaps;
- accessibility gaps;
- content gaps;
- unknowns.

Do not manufacture issues to make the document appear more thorough.

---

## 5. Product / UX direction

Define only what is relevant:

- priority user/role;
- highest-value task;
- owner/business objective;
- critical journey;
- primary action/behavior;
- alternate/recovery paths;
- key decision objects;
- proposed product expansion;
- validation lane;
- evidence limitations.

For portfolio prototypes, be explicit about what is concept/proxy evidence versus real user evidence.

---

## 6. Sitemap and information architecture

Provide:

```text
Home
├── ...
└── ...
```

For every route/page/anchor include:

- role;
- source/owner;
- destination behavior;
- whether existing/proposed;
- whether material to the critical journey.

Do not create extra pages solely to inflate project size.

---

## 7. Page-by-page specification

For every material page/route:

### [Route/Page]

**Status:** EXISTING / PROPOSED / EXTENDED

**Purpose:** ...

**User goal:** ...

**Owner goal:** ...

**Content:** ...

**Section order:**
1. ...
2. ...

**Layout/composition:** ...

**Components:** ...

**Interactions:** ...

**Motion:** ...

**Responsive behavior:** ...

**Accessibility:** ...

**Link destinations:** ...

**Dependencies:** ...

**Preserve notes:** ...

Do not use lorem ipsum when content hierarchy or copy is part of the design.

---

## 8. Design system / visual direction

### 8.1 Art direction

- **3 adjectives:** [... / ... / ...]
- **Visual concept:** [...]
- **Signature motif:** [...]
- **Anti-template rule:** [...]

### 8.2 Color

Use exact existing tokens when preserved; clearly label proposed additions.

### 8.3 Typography

- families;
- sources;
- roles;
- scale;
- special display rules.

### 8.4 Grid and spacing

- content width;
- columns;
- gutters;
- spacing rhythm;
- composition exceptions.

### 8.5 Media direction

- hero/editorial;
- cards/listing;
- crop/focal treatment;
- iconography;
- remote/local asset policy.

### 8.6 Anti-AI-template guardrails

Call out patterns to avoid, e.g. universal rounded cards, decorative gradients without meaning, repeated fade-up sections, generic cream-serif-orange defaults, gratuitous glassmorphism, identical section shells.

---

## 9. Motion and interaction contract

For each material interaction define:

- exact owner/selector/function when existing;
- trigger;
- state changes;
- timing/range/easing;
- choreography order;
- hover/focus behavior;
- keyboard behavior;
- pointer/touch behavior;
- reduced-motion behavior;
- preserve level.

For protected engines, explicitly state what new code **must not** modify.

---

## 10. Responsive behavior

Declare one:

```text
responsive_scope = desktop_only
```

or

```text
responsive_scope = responsive_all
```

### desktop_only

Verify declared desktop pressure points. Mark mobile/tablet `N/A_JUSTIFIED`. Do not claim fully responsive.

### responsive_all

Define intentional transformation across representative mobile/tablet/desktop widths.

Include:

- content priority changes;
- layout stack/reorder rules;
- navigation changes;
- touch targets;
- media crop strategy;
- typography adjustments;
- overflow/clipping constraints.

---

## 11. Technical architecture and file structure

Provide the target file tree.

Example:

```text
project/
├── index.html
├── ...
```

Then define:

### Protected files
- [...]

### Files allowed to change
- [...]

### New files
- [...]

### Module ownership
- [...]

### Dependency policy
- [...]

### Path/base-path policy
- [...]

### Progressive enhancement
- [...]

### Framework/build restrictions
- [...]

Prefer isolated extension scopes over coupling new behavior into protected core engines.

---

## 12. Accessibility / performance / SEO

Use only applicable requirements.

### Accessibility

- semantic structure;
- keyboard/focus;
- skip links/landmarks;
- alt text;
- reduced motion;
- contrast;
- automated Axe/Lighthouse targets when due now.

### Performance

- media loading strategy;
- dependency budget;
- animation/runtime constraints;
- applicable Lighthouse/performance budget.

### SEO / metadata

- title/description;
- OG metadata;
- favicon/theme color;
- robots/sitemap;
- canonical/structured data when relevant.

Mark irrelevant categories `N/A_JUSTIFIED`.

---

## 13. Deployment

Inspect before prescribing.

For each applicable target define:

### GitHub Pages

- workflow;
- source;
- artifact path;
- relative-link/base-path rules;
- custom-domain implications if any.

### Vercel

- preset;
- build command;
- output directory;
- routing/clean URLs;
- environment requirements.

### Other

Only if applicable.

Never write “deployed” when this section only describes the proposed deployment contract.

---

## 14. QA checklist

Use the detailed `QA-CONTRACT.schema.md` and include only applicable gates.

At minimum for material UI work consider:

- functional behavior;
- representative rendered pages;
- responsive/declared-scope widths;
- interaction/motion;
- media integrity;
- accessibility;
- console/runtime errors;
- routing;
- deployment;
- visual review against Design Contract.

A build PASS is not a visual PASS.

---

## 15. Deliverables

List concrete outputs, for example:

- files to create/change;
- routes/pages;
- docs;
- tests/QA artifacts;
- workflows;
- screenshots;
- PR/release output if authorized.

Avoid vague deliverables such as “polished UI.”

---

## 16. Definition of Done

The milestone is DONE only when all DUE-NOW criteria are satisfied.

Use binary criteria where possible:

```text
[ ] ...
[ ] ...
```

Also report:

```text
DONE_VERIFIED = [...]
N/A_JUSTIFIED = [...]
PENDING_FUTURE_PHASE = [...]
BLOCKED = [...]
```

Do not hide unresolved blockers.

---

## Final compiler self-review

Before handing this prompt to an implementation agent, verify:

- [ ] no invented current facts;
- [ ] preserve/change contracts do not conflict;
- [ ] every named selector/function exists or is clearly labeled PROPOSED;
- [ ] sitemap and page specs agree;
- [ ] responsive scope is internally consistent;
- [ ] deploy paths fit the hosting model;
- [ ] QA criteria are measurable enough to verify;
- [ ] future-phase requirements are not accidental blockers;
- [ ] the document can be understood without conversation history.
