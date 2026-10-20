# UX-first visual upgrade

Scope: repair Factory design routing, task-first requirements, mobile reference
coverage and visual evaluation. Local branch `upgrade/ux-first-visual-quality`.
Baseline: remote main `8bbab11d41511ff9679fe2cd96283449d9888c6a`.
No commit, push, merge, deployment or Patient-Journey-App change is part of this work.

## Audit → implemented repairs

| Finding | Priority | Repair / canonical owner |
|---|---|---|
| Mobile design/preview did not activate visual direction or decision checks | P1 | Both mobile flows now route reference research, journey layout, visual direction, media and craft QA; v2 design/rendered checks are required |
| Task walkthrough could be omitted while visual records passed | P1 | Optional backward-compatible `ux` page record in `design_decisions.py`; all five flows using design integrity now require it through `ux_contract_required` |
| Record-only “resolved” UX blocker could pass without retest | P1 | Open blockers rejected; resolved findings require retest; whitespace-only task fields rejected |
| A forged UX coverage flag could substitute for actual records | P1 | Receipt acceptance recomputes current contract coverage under existing file/hash checks |
| Curated knowledge had six website roles and no patient-journey profile | P2 | Five app task roles, healthcare profile and three original synthetic anatomy references, retrieved through existing owner |
| No runnable mobile visual reference in this curated family | P2 | Three-task specimen with working filter, empty reset, inline validation and retained-input review; inspected captures and source hashes |
| Mobile eval weights lacked explicit task/craft dimensions | P2 | Two evals reweighted; new adversarial “UX before pastel” task; UX blockers cannot be averaged away |
| Visual rubric claimed to prove beauty and could reward unnecessary media | P2 | Corrected evidence boundary; task-first blocker rule and justified N/A media treatment |

Pre-existing seven-sign review changes were preserved. The seven signs remain
purpose-based, never blanket bans on neon, dark styles, gradients or cards.

## Working sequence

1. Read project truth, inventory actual screens/states and current owners.
2. Resolve current state, user question, information priority, action/destination,
   feedback and recovery; inspect a wireframe walkthrough.
3. Repair blocking UX findings before visual exploration.
4. Retrieve only relevant role/reference knowledge. Label gaps and hypotheses.
5. Compare materially different compositions on representative tasks using the
   same content/state; preserve explicit user constraints.
6. Record tokens, type, density, media purpose and capture-bound critique.
7. Inspect real renders, repair findings, then inherit the chosen direction for
   rollout. Keep human preference and product impact separate.

This is carried by existing Flow OS, design packet, lifecycle cards, schema,
checker and receipt owner. No second orchestrator, provider call or new production
dependency was added.

## Migration

Legacy v1/v2 records remain parseable. Newly gated page, website, portfolio and mobile
design work requires `pages[].ux`; rerun the canonical checker after adding truthful
records. Historical comparison evidence is not rewritten to manufacture coverage.
The lifecycle smoke creates explicitly synthetic UX records only in its temporary
fixture, not in historical project evidence.

Use `check-design-decisions.py --schema` for exact fields and
[the field guide](../skills_UIUX/visual-design-direction/references/mobile-ux-first.md)
for meaning. `ux_integrity=RECORDED` establishes record coverage, not authentic
human participation, successful usability or the actual chronological order of work.

## References and verification

- [Practice and sources](../skills_UIUX/visual-design-direction/references/mobile-ux-first.md)
- [Runnable example and inspected review](../skills_UIUX/visual-design-direction/examples/mobile-care/README.md)
- `uiux-factory/tests/test_mobile_visual_quality.py`: positive/negative routing,
  missing/conflicting knowledge, missing/forged UX coverage, open blockers,
  missing retest and blank recovery.
- Existing mobile, design integrity/comparison/receipt/provider, lifecycle and
  completion regression suites are rerun alongside the new tests.
- Browser example checks cover Chromium/WebKit at 320/390/1280 CSS px.
- Structural validation and eval harness smoke are separate from model outcome trials.

## Remaining evidence gaps

- No controlled before/after model trial proves this upgrade produces prettier apps.
  The new eval is ready for such trials; harness fixture smoke is not that experiment.
- The authored specimen is not a user-approved visual target. Store approved target
  renders/component sources and rationale when a project makes those decisions.
- App record and support roles currently provide candidate guidance, not inspected
  anatomy specimens; retrieval retains `NO_CURATED_REFERENCE_ANATOMY` for those roles.
- The curated healthcare addition is deliberately bounded. Other domains must still
  research references instead of silently borrowing healthcare or industrial styling.
- Native device/OS behavior and actual user preference remain separately unverified.

The repository can require better evidence and preserve visual decisions; it cannot
honestly guarantee beauty from a short style label or green technical tests alone.

## Final local verification (2026-10-20)

- Focused regression suite: **201 passed, 1 skipped**. Skip: inherited optional
  local rendered-image fixture absent; new UX/routing tests ran. See
  [pytest log](evidence/ux-first-upgrade/pytest.log) and
  [JUnit report](evidence/ux-first-upgrade/pytest.xml).
- Flow validation: 9 flows, 81 referenced skills, 4 roles, 12 routing smokes passed.
- Skill structure: 116 skills passed; existing prompt-compiler length warning.
- V5 structure: 114 eval tasks passed; existing broad-profile size warnings.
- [Eval harness smoke](evidence/ux-first-upgrade/eval-smoke.log) passed parsing and
  aggregation of its synthetic fixture. Its 2/3 sample result is not a result
  for the new visual evaluation and not a product-quality score.
- Browser specimen: six engine/viewport combinations passed; three final captures
  opened and visually inspected, with seven-sign review in the specimen README.
- Contrast pairs: navy/blue 12.16:1; navy/mint 12.99:1; secondary/white 5.35:1;
  secondary/canvas 5.02:1; white/action 18.72:1; error/error-surface 6.75:1.
- Background localhost launch was rejected by automatic policy without a detailed
  reason. The HTML file and recorded captures remain available for local review.

No production dependencies were added. Pytest was installed into a separate local
QA folder using the existing requirements-dev constraint; no project package files
were changed. Prior working-tree edits were preserved.


## Patient-Journey-App field trial: execution defect

The actual product has 47 canonical screens. The decision validator capped
`pages` at 30, so a complete per-screen UX rollout could not fit in one contract.
A reproducible synthetic 47-screen regression failed with the explicit 30-item
limit before repair (`evidence/ux-first-upgrade/47-screen-before.log`).
The bounded limit is now 100; the regression also rejects 101. Other validation,
file-size, reference and capture requirements remain intact. This repairs coverage
capacity; it does not establish visual quality or human usability.

The target trial also exposed a presentation fallback inventing a doctor on pending
requests, a dark selected-nav icon disappearing despite zero axe violations, and
uncompressed preview delivery missing the requested slow-network LCP target.
These were target/execution defects, not evidence that routing itself failed.
The mobile state skill now explicitly distinguishes canonical facts from decorative
fallbacks, and browser handoff requires a criterion/evidence matrix, lab conditions,
runner capability limits and retained failures. Screenshots still require actual
inspection; these instructions are not an automatic aesthetic acceptance receipt.


### Trial handoff recorded 2026-10-21

The Patient-Journey-App localhost trial runs on port 4186; the earlier 4190
background-launch rejection above concerned the separate synthetic specimen.
Latest focused Factory regression: **88 passed, 1 skipped** (inherited missing
render fixture), recorded in `docs/evidence/ux-first-upgrade/field-trial-regression.log`.
The target app records 467 latest passing browser cases and 5 explicit skips across
regression/repair phases, 49 model checks, and inspected screenshots for 47 states.
These are not participant or aesthetic scores and not one clean final-tree full run.
The lab retains its failed 4x CPU stress profile and some samples over the 100ms
feedback target. The target's explicit performance-budget check therefore returns
FAIL; the trial is reviewable, not QA-accepted against every requested criterion.
See `docs/ux-trial/review.md` and `performance-budget.json` in the target checkout.
No target or Factory changes were committed, pushed or merged in this trial.
