# WCAG Focus/Hover + Pseudo-localization Evidence V1

This integration strengthens the post-render evidence pipeline without claiming full WCAG conformance or localization certification.

## State / interaction crawler

The upgraded crawler adds rendered checks aligned with:

- WCAG 2.4.7 Focus Visible: keyboard-reached controls must expose a visible focus indicator.
- WCAG 2.4.11 Focus Not Obscured (Minimum): the focused component must remain at least partially visible; the implementation approximates this with viewport intersection and hit-testing.
- WCAG 1.4.13 Content on Hover or Focus: demonstrated author-controlled additional content is checked for the applicable dismissible, hoverable, and persistent behaviors.

Native user-agent tooltips are intentionally excluded. Automated results are evidence for the Factory contract, not a complete accessibility audit.

## Pseudo-localization stress

`RESPONSIVE-004` now includes disposable browser-only pseudo-localization stress profiles:

1. `expanded-accented-40` — accented pseudo text with roughly 40% expansion.
2. `vietnamese-heavy` — long Vietnamese strings, diacritics, currency and location text.
3. `accented-density` — high diacritic density without aggressive expansion.
4. `rtl-bidi` — mixed Arabic/Hebrew/numeric content with RTL direction.

Each profile is exercised independently across mobile, tablet, and desktop representative routes. Evidence captures clipping, horizontal overflow, off-screen content, text/control overlap, direction, and screenshots. Generated source files are never modified.

Passing this stress suite means the rendered layout survived these pseudo-localization fixtures. It does not prove that real translations are linguistically correct or that every locale will fit.
