# Profile — Pixel Faithful

Use only when the goal explicitly requires high-fidelity reconstruction from an authoritative live/reference source.

## Required output sections

Use **11 sections numbered 0–10**:

0. Invariants
1. Assets & provenance
2. Document/application shell
3. Exact DOM/component/source order when material
4. Tokens/custom properties/theme values
5. Detailed visual mechanics / layer positioning
6. Responsive/breakpoint behavior
7. Interaction/state/motion implementation evidence
8. Choreography / perceptual acceptance criteria
9. QA checklist
10. Deliverables

Do not call this a universal schema.

## Evidence rules

Every concrete value carries one of:
`VERIFIED / INFERRED / ASSUMED / UNKNOWN / PROPOSED / N/A_JUSTIFIED`.

For a faithful reconstruction, most preserved values should be `VERIFIED`. A visually estimated timing/easing is `INFERRED`, not `VERIFIED`.

## Assets

Do not assume remote-only assets. For every material asset specify when known:
- local/remote;
- exact source/path/URL;
- ownership/license/provenance;
- dimensions/crop role;
- replacement policy;
- transformation policy.

## Structure

Preserve exact DOM/component/source order only where evidence shows it is contractually or visually material. Source order can affect paint/stacking, but stacking contexts and top-layer rules must be verified in rendered output rather than simplified to “source order always equals paint order”.

## Motion

Separate:
1. implementation evidence — state, variables, functions, event listeners, scroll sampling, keyframes; and
2. perceptual choreography — what a reviewer should see at each checkpoint.

This separation allows QA to catch implementations that are mechanically similar but visually wrong.

## QA

Use exact representative viewports/checkpoints/selectors when supported by evidence. Require rendered comparison for visual claims. Do not treat green build/tests as pixel-fidelity proof.