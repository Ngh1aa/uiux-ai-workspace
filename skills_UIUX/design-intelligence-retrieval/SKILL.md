---
name: design-intelligence-retrieval
description: Retrieves focused product, style, color, typography, icon, motion, chart, UX and stack guidance from the pinned vendored design-intelligence corpus. Use after project truth, domain, audience and page/app role are known when a UI/UX decision benefits from broader design knowledge; query the smallest relevant subset instead of loading the whole database.
---

# Design Intelligence Retrieval

## Goal
Use the vendored UI UX Pro Max corpus as a searchable design-intelligence source while `skills_UIUX` remains authoritative for project truth, evidence discipline, Design Contract, implementation safety and QA.

## Source precedence
`current user request → project truth/source code → passed Design Contract/artifacts → routed local skills → retrieved design intelligence → generic model prior`

Retrieved recommendations are normally `EVIDENCE_BACKED_INFERENCE` or `PROFESSIONAL_HYPOTHESIS`, not universal `FACT`.

## Routing contract
Read `project-context` first. Identify product/domain, audience, business goal, platform, page/app role and actual stack before choosing a search mode.

Choose the **smallest mode that fits**:
1. New page/project or system-wide visual direction → `--design-system`.
2. Focused concern/component defect → one explicit `--domain`.
3. Implementation-specific question with a known stack → `--stack`; add a separate domain query only for a distinct design concern.

Do not route this skill for a trivial local fix when project truth already determines the answer.

## Query contract
- One dominant intent per query.
- Prefer 2–5 meaningful terms plus one useful product/platform/interaction constraint.
- Do not include secrets, private user data or unnecessary project content in queries or persisted output.
- Verify returned domain/category, top result identity and fit before adopting it.
- If output is empty or off-topic, retry **once** with a narrower query or explicit domain/stack.
- If the retry still fails, record `no verified match`; use local/project guidance as fallback and do not pretend the database returned evidence.
- Do not persist unverified retrieval output.

## Stack detection
Never assume a stack. Inspect project truth first, for example:
- `package.json` dependencies for React/Next/Vue/Svelte/Nuxt/Angular;
- `pubspec.yaml` for Flutter;
- `*.xcodeproj` / `Package.swift` for SwiftUI;
- `composer.json` for Laravel;
- `app.json` plus React Native dependency markers for React Native.

If stack-specific guidance is not material, do not spend context detecting it.

## Recommended workflow
1. Read project truth and relevant passed artifacts.
2. Decide whether external design intelligence can improve an active decision.
3. For broad direction, run one focused `--design-system` query.
4. Supplement only unresolved active gaps using `--domain` or `--stack`.
5. Keep only a small decision-ready result set.
6. Classify each meaningful candidate `ADOPT / ADAPT / REJECT`.
7. Reconcile with brand, accessibility, content density, platform conventions, actual component/tokens and implementation feasibility.
8. Record adopted principles in the Design Contract or implementation artifact with source, pinned upstream commit and adaptation rationale.
9. Verify the resulting decision in rendered/code/evidence checks appropriate to its owner phase.

## Default command
```bash
python design-intelligence-retrieval/scripts/query.py "<domain product audience role character>" --design-system
```

Focused examples:
```bash
python design-intelligence-retrieval/scripts/query.py "error summary validation" --domain ux
python design-intelligence-retrieval/scripts/query.py "editorial serif premium" --domain typography
python design-intelligence-retrieval/scripts/query.py "dashboard overflow nowrap" --stack nextjs
```

## Design-system persistence policy
The upstream engine can create `design-system/<project>/MASTER.md` and page overrides. In `skills_UIUX`:
- a persisted upstream `MASTER.md` is a **retrieved candidate artifact**, not a second canonical source of truth;
- the project Design Contract remains authoritative for adopted direction;
- read existing persisted artifacts before regenerating;
- never use upstream `--force` without explicit user authorization;
- page overrides may specialize an adopted direction but may not silently contradict the Design Contract.

Optional `--variance`, `--motion` and `--density` dials may be used only when the project direction needs those controls. They are tuning inputs, not quality scores.

## Synthesis contract
For each material result, capture only:
- query/context;
- returned candidate and upstream status when available;
- `ADOPT / ADAPT / REJECT`;
- reason;
- affected project constraint/decision;
- verification method.

Do not paste entire catalogs into prompt context.

## Hard gates
- External recommendations never silently override current user/project/brand/source truth.
- Deprecated/pending upstream records are not canonical recommendations without explicit review.
- A database recommendation is not proof of UX, conversion, accessibility or business performance.
- `design-intelligence-retrieval` augments, not replaces, `design-reference-research-and-benchmark` when real references are required.
- For substantial redesign, it does not replace the Design Contract, `visual-redesign-delta-gate`, `media-crop-and-layout-integrity`, responsive/accessibility verification or rendered visual QA.
- Stack guidance must be reconciled with the project’s actual framework/version/code before implementation.
- Keep upstream license, provenance and immutable version lock intact.

## Resources
- [Upstream integration contract](references/upstream-integration-contract.md)
- Vendored source: `../vendor/ui-ux-pro-max/`
- Augmentation prompt: `../DESIGN-INTELLIGENCE-AUGMENTED-REDESIGN-PROMPT.md`

## Verification
```bash
python scripts/validate-vendor-uiux-pro-max.py
python -B design-intelligence-retrieval/scripts/query.py "education admissions mobile" --design-system
python scripts/validate-skills.py
python scripts/validate-v2.py
python scripts/eval-harness.py smoke
```
