# A3 — Adaptive Flow / Change Surface

A3 converts the A2 Task Contract into the smallest credible execution lane. The classifier is deliberately conservative: a concrete change owner beats a broad verb, while product/site creation remains product-sized unless the user explicitly limits the work to one page or smaller surface.

## Change surfaces

| Surface | Meaning | Default managed stages |
| --- | --- | --- |
| `MICRO` | One atomic UI owner or visual defect: button, icon, image, spacing, single card, etc. | `implementation → qa` |
| `FOCUSED` | One section or tightly related component cluster: hero, nav, pricing block, modal, form cluster, etc. | `research → implementation → qa` |
| `PAGE` | One route/screen/page or several sections that form one page. | `research → design → implementation → qa` |
| `REDESIGN` | Multi-page/site-wide redesign of an existing experience. | professional flow |
| `PRODUCT` | New or product-wide experience spanning multiple surfaces/flows. | professional flow |

## Specificity rules

1. Explicit narrow scope beats a broad verb.
   - `Redesign hero section only` → `FOCUSED`
   - `Redesign homepage only` → `PAGE`
   - `Redesign the whole website` → `REDESIGN`
2. Atomic owner beats one container context for focused repair language.
   - `Fix icon in header` → `MICRO`
3. Related component vocabulary does not automatically widen the lane.
   - `Polish pricing cards` → `FOCUSED`
4. References and preserve/forbidden clauses do not expand the change surface.
5. A website/app/platform build remains `PRODUCT` when checkout/dashboard/search are product features.
   - `Build a SaaS platform with dashboard` → `PRODUCT`
   - `Tạo website bán hàng có checkout và tìm kiếm` → `PRODUCT`
6. Explicit single-page creation stays `PAGE`, even when it belongs to a product/platform.
   - `Create a landing page for a fintech platform` → `PAGE`

## Flow mapping

- `MICRO` → `flows/micro-ui-change.json`
- `FOCUSED` → `flows/existing-ui-improvement.json`
- `PAGE` → `flows/page-ui-work.json`
- `REDESIGN` / `PRODUCT` → `flows/professional-website-redesign.json`

`FlowResolver` normalizes legacy contexts that do not yet carry `change_surface`:

- `improve|fix|polish` → `FOCUSED`
- `redesign|rebuild` → `REDESIGN`
- `build` → `PRODUCT`

This preserves old callers while allowing A3-aware Goal Interpreters to route more precisely.

## Manual override

The managed CLI exposes:

```bash
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../my-project \
  --managed \
  --task "Polish the hero" \
  --change-surface FOCUSED
```

Allowed values are `MICRO`, `FOCUSED`, `PAGE`, `REDESIGN`, and `PRODUCT`.

## Boundary with later roadmap items

A3 owns change-size classification and declarative managed-flow selection. It does **not** consolidate the two current runtimes, change provider architecture, replace QA infrastructure, or implement reference-DNA semantics. Those remain later roadmap work.
