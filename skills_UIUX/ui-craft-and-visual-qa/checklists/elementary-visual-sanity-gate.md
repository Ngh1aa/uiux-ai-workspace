# Elementary Visual Sanity Gate

Use this gate for substantial visual work, multi-page/whole-site UI changes, production-candidate/release work, and any remediation caused by an obvious rendered defect that previous QA missed.

This gate exists to catch elementary failures before deeper aesthetic scoring. A page that is elegant but contains invisible text, disappearing button labels, false-green empty-state coverage, or badly cropped primary media does **not** pass visual QA.

## 0. Coverage contract — hard gate

Before inspecting pixels, define the matrix that can actually expose the defect:

```text
all affected routes/templates
× declared viewports + pressure widths
× material data states (empty / populated / error / selected / authenticated when applicable)
× material interaction states (default / hover / focus-visible / active / disabled / selected)
```

Rules:

- [ ] Shared-owner elementary sanity covers **all affected routes/templates**, not a representative sample.
- [ ] Conditional controls must be rendered with the data/state needed to make them exist. An empty Cart that hides Checkout is **not** coverage of the Checkout CTA.
- [ ] Seed/mock data used only to expose UI state must be deterministic and must not be reported as proof of backend/system success.
- [ ] A selector whitelist is not sufficient when other visible text/actions can inherit the same CSS owner. Prefer semantic/all-visible discovery; any whitelist must have an explicit completeness rationale.
- [ ] The report records route, viewport, data state and interaction state so a green run cannot hide unexercised states.

A CI job that never rendered the reported defect state is a **false green**, not a PASS.

## 1. Surface / foreground pairing — hard gate

For every changed semantic surface (`page`, `raised`, `inverse`, `footer`, `nav`, `drawer`, `modal`, `summary`, `media overlay`, etc.):

- [ ] Inspect the **actual rendered background**.
- [ ] Inspect inherited/computed foreground for body text, headings, muted text, links, icons, dividers and controls on that surface.
- [ ] If a background changes light↔dark, foreground roles are reviewed in the same change; never change only the background and assume inherited text remains valid.
- [ ] No important text may be readable only after text selection/highlight.
- [ ] No foreground/background pair may collapse to effectively identical colors (for example `1:1` or visually equivalent).
- [ ] Normal interactive labels meet the project/accessibility contrast requirement in their rendered state. Automated contrast checks are regression signals, not a formal conformance claim.
- [ ] Disabled content may follow the project's accessibility policy, but if the label is intentionally visible it must remain perceptible and must not disappear into its surface.

### All-visible catastrophic scan

For production/release or regression remediation, add a deterministic browser scan over **all visible text-bearing elements outside genuinely variable media contexts**, not only named buttons/footer selectors.

The scan should:

1. read winning computed foreground;
2. composite the effective rendered ancestor background;
3. flag catastrophic near-equal foreground/surface pairs;
4. record selector/class/text/route/viewport for diagnosis;
5. treat the scan as a safety net, not as a substitute for human inspection.

This is specifically intended to catch white-on-white, light-on-light, dark-on-dark and inherited-color regressions on surfaces the author forgot to whitelist.

### Cascade/specificity check

When computed rendering differs from the intended token/component rule:

1. inspect the winning selector/cascade layer;
2. fix the true owner/specificity conflict;
3. keep foreground + background as one semantic state contract;
4. do not add a page-local `!important` patch unless the project contract explicitly requires it;
5. recapture the rendered state.

A rule that says `color: X` in source is not evidence if a more-specific selector wins in the browser.

## 2. Interactive-state visibility — hard gate

Discover semantic interactive elements from the rendered DOM (`a[href]`, `button`, form actions, `[role=button]`, project controls) rather than auditing only a hand-picked visual class list.

For every changed/shared semantic control variant, inspect applicable states on the real rendered component:

`default → hover → focus-visible → active/selected → disabled → loading → success/error`

- [ ] Label/icon remains readable in every visible state.
- [ ] A state that changes foreground also changes/retains a compatible background or border context.
- [ ] Hover must never turn a dark label white while leaving a white/light surface unchanged.
- [ ] Focus-visible remains perceivable and does not depend only on a subtle color shift.
- [ ] Selected/active state does not erase label/icon contrast.
- [ ] Disabled styling communicates disabled without becoming blank/invisible.
- [ ] Controls hidden until populated/selected/error state are explicitly rendered before state auditing.

For production-candidate/release work, require a rendered/computed-style regression for interaction contrast in addition to screenshots.

## 3. Shared-owner coverage — hard gate

Deep visual review may sample representative pages. **Elementary sanity for a changed shared owner may not.**

If the change touches a shared header/footer/nav/button token/theme/surface/component:

- [ ] Identify every route/template where that owner renders.
- [ ] Run route smoke + elementary visibility/state checks across **all affected routes/templates**.
- [ ] Inspect at least one real rendered instance for every semantic variant and every materially different surface context (light, dark/inverse, image/overlay, summary/card, disabled, etc.).
- [ ] Include conditional populated/error states when the shared owner is otherwise absent in default data.

This rule prevents a shared cascade change from silently breaking the same footer/button on an entire site while the test only exercised one convenient page.

## 4. Human-subject / focal-crop integrity — hard gate when applicable

For hero/feature media containing people or another obvious focal subject:

- [ ] Inspect the actual crop at every declared target viewport/pressure point.
- [ ] `object-fit: cover` is **unsafe by default** for primary human/focal media until a crop contract is verified.
- [ ] `object-position` values such as `center`, `top`, `20%` or `0%` are implementation candidates, not proof.
- [ ] Define the focal subject and no-cut zone before accepting a destructive crop.
- [ ] Do not cut through the face, eyes, top of head, product identity or other primary identifying feature unless intentional art direction is documented.
- [ ] Ensure overlays/panels do not hide the intended focal subject.
- [ ] If one source cannot survive all target ratios, use `contain`, a different composition, responsive art direction (`<picture>`), or alternate crop/asset rather than forcing one universal `cover` crop.

### Cover-crop regression contract

For production/release regression, primary/feature media using computed `object-fit: cover` must be discoverable by a deterministic check.

Default policy:

```text
primary/focal media + cover + no explicit verified crop contract
→ BLOCKED
```

If a project intentionally allows `cover`, record machine-readable or otherwise deterministic metadata tying it to:

- focal subject;
- no-cut zone / safe area;
- target viewports;
- the rendered evidence that was opened and inspected.

Metadata is traceability, **not** proof by itself. Human screenshot inspection remains required.

## 5. Variable media / text-on-image

Automated flat-background contrast math can be wrong over photography/video. Do not manufacture a PASS from an average or ancestor background color.

- [ ] Detect/label variable-media contexts separately.
- [ ] Inspect actual rendered crop behind the text.
- [ ] Verify stable scrim/backplate/gradient/safe-zone treatment when readability depends on variable imagery.
- [ ] Interactive text on media is checked in its changed states too.

If an automated scan cannot model the pixels behind the text, it must return `requires rendered inspection`, not silently PASS.

## 6. Rendered evidence rule

- [ ] Screenshot/capture exists for declared route/viewport/data-state coverage.
- [ ] Screenshot/capture was actually opened/inspected.
- [ ] Known reported defect state is explicitly recaptured after remediation.
- [ ] Populated/conditional UI used by the defect is visible in the evidence.
- [ ] A clean build/CI run is not substituted for visual inspection.
- [ ] If automated sanity scan and human screenshot disagree, the broken rendered screenshot wins and the phase is BLOCKED until resolved.

## 7. Failure promotion rule

If a user or reviewer catches an obvious visibility/state/crop defect that the current QA process should have caught:

1. fix the project root cause;
2. identify why previous verification returned a false green (missing route, missing viewport, missing data state, selector whitelist, cascade blind spot, crop assumption, uninspected artifact, etc.);
3. add a project-level deterministic regression where feasible;
4. add/update the owning library checklist/skill;
5. add a regression eval case when the failure mode is generalizable;
6. exercise the new guard on the project defect before closing remediation.

Do not claim “will never happen again.” The valid claim is that the known failure mode now has an exercised guard and is release-blocking when reproduced.

## Minimum PASS condition

`PASS` requires zero unresolved DUE-NOW P0/P1 findings from this gate **and zero unaccounted coverage cells required by the declared matrix**.

Any invisible critical text/control, disappearing interaction label, false-green conditional state, or unjustified primary-subject crop is a blocker regardless of aesthetic score or CI/build status.
