# UX feedback, Factory repair and regression prevention

This is the canonical policy for turning verified feedback into reusable prevention.
It extends the existing A5 advisory memory; it does not create a second memory store,
grant mutation authority, train a model, or turn old results into a current QA PASS.

## Repair order

When using the Factory exposes routing, skill, source-discovery, capture or QA friction:

1. Reproduce it, identify the Factory owner and distinguish it from a target bug.
2. Repair the Factory owner first on a separate branch/PR with regression evidence.
3. Run the repaired Factory against the target. Then repair the target's canonical
   component/token/state source and regenerate derived bundles through its own tooling.
4. Re-run all affected target routes/templates and critical flows, including the exact
   reported state. Missing coverage stays UNKNOWN; do not infer product PASS from fixtures.
5. Record normalized results and promote reusable prevention through a reviewed Factory PR.

Before target edits, map entry renderer → shared owner → canonical source → generator
→ generated artifact → affected routes. Historical directory names and built bundles
are not source authority. Record uncertainty rather than guessing the owner.

On Windows, initialize pinned submodules with `git -c core.longpaths=true submodule update --init --recursive`
when the checkout lives under a long generated workspace path. Pass the option to the
command so nested clones inherit it; a parent repository setting alone may not reach them.

## Three different kinds of learning

- **Human feedback:** a request/finding, not an automatically verified evaluator outcome.
  Reproduce it and produce current evidence before treating it as observed quality history.
- **Project memory:** `EvaluationMemoryStore` persists bounded evaluator/requirement/outcome
  metadata in `.uiux-agent-runs/memory/evaluation-memory.json`. The external manifest now
  recalls the same advisory history after Flow selection. Disabled or corrupt memory
  remains DISABLED/UNKNOWN and cannot block routing, select flows or grant evidence/authority.
- **Cross-project prevention:** `skills_UIUX/runtime/ux-regression-lessons.json` contains
  reviewed, versioned lessons linked to real source/QA evidence. New lessons require a
  Factory code/skill/test change through PR review. Raw chat, project colors, copied UI
  and provider prose are never automatically promoted into global rules.

This is evidence-driven software learning, not automatic model weight training or a
promise that every future UX defect is impossible.

## Executable rendered checks

`uiux-factory/qa/scripts/ux-regression.mjs` runs inside the existing browser-evidence lane.
Every declared route uses desktop + mobile by default. `QA_VIEWPORTS_JSON` may override
that matrix explicitly. `QA_MOTION_MODES` can declare `reduce,no-preference`.

The default scan inspects all visible DOM text (bounded to 5,000 candidates), composites
known solid ancestor surfaces, and fails catastrophic contrast below 1.2:1, horizontal
document overflow and broken visible images. It uses winning computed styles rather
than source declarations. Gradient, media, pseudo surfaces, unsupported colors and
compositing remain UNKNOWN and require visual inspection. This is not WCAG certification.

Targets may declare `uiux-ux-regression.json`; the harness auto-loads it from `QA_TARGET_DIR`,
or accepts an explicit `QA_UX_CONTRACT` path. The closed schema supports at most 64 checks:

```json
{
  "schema_version": 1,
  "checks": [
    {"id": "PRIMARY-CTA-RADIUS", "kind": "style-range", "selector": ".primary-action", "property": "border-top-left-radius", "min": 12},
    {"id": "SWITCH-HIT", "kind": "hit-target", "selector": "label.preference-switch", "min": 44},
    {"id": "SWITCH-ALIGN", "kind": "right-aligned", "selector": ".preference-switch", "within": ".preference-row", "tolerance": 2},
    {"id": "DEMO-PREFERENCE", "kind": "toggle-persistence", "selector": "#demo-alerts", "route": "/settings.html"},
    {"id": "ACTION-EXPOSED", "kind": "unobscured", "selector": ".primary-action"},
    {"id": "NO-REVIEWER-OVERLAY", "kind": "absent-or-hidden", "selector": "#reviewer-tools"}
  ]
}
```

These are examples, not universal styles. Square buttons are valid when the target's
design contract says so. Toggle tests opt into keyboard/reload interaction for local/demo
preferences only and restore the original value. Do not declare them for destructive or
remote account changes. Focus/hover and state-dependent summaries still require target
flow tests / State Coverage; a generic browser scan cannot infer business semantics.

Missing required selectors, hidden targets, unsupported computed ranges and inspection
errors fail the declared check; empty selector coverage is never a PASS. Reports remain
`scope=automated_checks_only`, `visual_review=UNKNOWN`, with route/viewport/motion and
limitations. Inspect screenshots and document coverage before making broader claims.

## Recording and recalling feedback

After browser QA (including failures that produced receipts):

```bash
python skills_UIUX/scripts/record-ux-feedback.py \
  --project-root /path/to/target \
  --reports-dir uiux-factory/qa/artifacts/ux-regression
```

This reuses A5's categorical allowlist. Raw DOM, screenshot contents, feedback prose and
prompts are discarded. The next `prepare-external-task.py --target-root ...` reads that
target's bounded history, without changing routing or current evidence status.

Cloud QA also records available receipts even when browser assertions fail; it preserves
the original QA exit status. Actions checkouts are ephemeral: uploaded report artifacts
must be explicitly imported into a persistent target checkout to survive later runs.
The checked-in reviewed catalog persists across projects without that import step.

## Maintaining prevention

Each verified feedback repair needs: source evidence, owning layer, smallest reproducible
failing case, a regression that fails before/pass after, applicable route/state/motion
coverage, and a target dogfood receipt. Promote general mechanisms, never a project's
visual taste. Update existing skills/evaluators rather than adding competing orchestration.
Factory fixtures prove tooling; separate target evidence proves product behavior.
