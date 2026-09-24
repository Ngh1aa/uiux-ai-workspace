# Design-Intelligence-Augmented Redesign Prompt

Use this as a **conditional augmentation module** for page, multi-page, app or whole-site visual redesign when searchable design intelligence can improve an active decision. It does not replace `LATEST-3-PROMPT-REDESIGN-PIPELINE.md`, `PHASE-AWARE-GATING.md` or `website-delivery-pipeline/SKILL.md`.

## Activation

Activate when one or more apply:
- visual direction is weak/generic or the user asks for broader design intelligence;
- a new page/app/system needs a coherent style/color/type/layout direction;
- domain/product pattern knowledge is insufficient;
- a focused UX/icon/motion/chart/typography decision lacks guidance;
- implementation needs stack-specific UI guidance.

Skip when project truth already resolves a local defect and retrieval would add noise.

## Mandatory order

1. **Project truth first** — read source, route/page roles, components, tokens, content/data/API, constraints and passed artifacts.
2. **Classify** — Scope, Type, Risk, Mode and responsive scope.
3. **Route local skills** — use the smallest `skills_UIUX` graph. Vendor skills/data are not a replacement orchestrator.
4. **Research / Design Contract** — substantial redesign must satisfy the existing pre-design gate before implementation.
5. **Select retrieval mode** based on the actual decision:
   - new/system visual direction → `--design-system`;
   - focused concern → one explicit `--domain`;
   - implementation detail with detected stack → `--stack`.
6. **Query narrowly** — one dominant intent, 2–5 meaningful terms plus one product/platform/interaction constraint.
7. **Verify match** — confirm returned category/domain/top result fits the product/platform. Retry once with narrower wording or explicit domain/stack if empty/off-topic. After the retry, record `no verified match` rather than inventing data.
8. **Synthesize** — mark each material result `ADOPT / ADAPT / REJECT` against project truth, brand, accessibility, content density, page role and feasibility.
9. **Lock adopted direction** in the canonical Design Contract: hierarchy, composition families, typography logic, media behavior, interaction grammar and responsive transformation.
10. **Implement safely** — reuse/extend before duplicate; preserve unrelated behavior; reconcile stack recommendations with actual package/framework versions.
11. **Verify rendered reality** — OLD/NEW where applicable, representative routes/viewports, structural delta, media crop/focal integrity, accessibility and functional/system reality appropriate to scope.
12. **Record provenance** — material adopted design intelligence retains query mode + upstream commit + adaptation rationale + verification.

## Stack detection before `--stack`

Never assume a framework. Inspect project files first:
- `package.json` dependencies → React / Next / Vue / Svelte / Nuxt / Angular;
- `pubspec.yaml` → Flutter;
- Xcode project / `Package.swift` → SwiftUI;
- `composer.json` → Laravel;
- React Native markers (`app.json` and dependency).

If stack guidance is not material, do not spend context detecting it.

## Retrieval recipes

### A. New page/project/system direction
```bash
python -B design-intelligence-retrieval/scripts/query.py \
  "<domain> <product> <audience> <page/app role> <desired character>" \
  --design-system
```

Optional dials may be used when they reflect a real decision:
```bash
--variance <1-10> --motion <1-10> --density <1-10>
```
They tune candidates; they are not quality scores.

### B. Focused design/UX gap
```bash
python -B design-intelligence-retrieval/scripts/query.py \
  "<observable outcome or focused design intent>" \
  --domain <domain>
```

For accessibility and interaction issues, search the observable semantic outcome first, then stack implementation detail if needed.

### C. Stack implementation guidance
```bash
python -B design-intelligence-retrieval/scripts/query.py \
  "<specific implementation concern>" \
  --stack <detected-stack>
```

Do not replace semantic UX reasoning with framework keywords.

## Candidate decision table

| Candidate | Retrieval mode | Upstream status | Project fit | Decision | Adaptation | Verification |
|---|---|---|---|---|---|---|
| ... | design-system/domain/stack | active/supplemental/etc. | high/medium/low | ADOPT/ADAPT/REJECT | ... | rendered/code/evidence check |

Only keep decision-relevant rows.

## Persistence rule

If using upstream `--persist`:
- always point `--output-dir` at the project root;
- read an existing `design-system/<project>/MASTER.md` first;
- do not use `--force` without explicit user authorization;
- treat generated MASTER/page files as **candidate retrieval artifacts**;
- the `skills_UIUX` Design Contract remains canonical after synthesis.

Never maintain two competing sources of truth silently.

## Evidence interpretation

- Database match/recommendation → normally `EVIDENCE_BACKED_INFERENCE` or `PROFESSIONAL_HYPOTHESIS`.
- It does **not** prove usability, conversion, accessibility, business performance or production suitability.
- Real production/reference research is still required when the active question depends on actual market/product behavior.

## Non-negotiable anti-patterns

- loading the full vendor database into prompt context;
- activating all seven vendor skills on every UI task;
- choosing a style only because it ranks first;
- treating color/font/product recommendations as facts;
- overriding existing tokens/components/brand without rationale;
- persisting an off-topic or unverified result;
- assuming a stack;
- using vendor design-system output as a parallel canonical Design Contract;
- replacing structural redesign with font/color/spacing/animation changes;
- skipping `visual-redesign-delta-gate`, `media-crop-and-layout-integrity` or rendered visual QA when applicable.

## Outcome

The vendored UI UX Pro Max corpus is a **Design Knowledge Engine**. `skills_UIUX` remains the **UI/UX Operating System** that decides when to retrieve, what to adopt, how to adapt, how to implement and what evidence is required to call the result successful.
