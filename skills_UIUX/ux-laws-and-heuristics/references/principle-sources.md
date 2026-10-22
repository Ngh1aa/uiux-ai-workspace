# Principle sources and applicability

Last checked: 2026-10-22. Recheck primary sources when adopting a time-sensitive
standard; this date is not a promise that a future standard is unchanged.

| Decision | Source / kind | Applicability and boundary | Verification |
|---|---|---|---|
| Web pointer target minimum | [WCAG 2.2 SC 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), AA requirement | 24×24 CSS px or a documented exception. Spacing uses the specified 24 CSS px circle test, not a blanket padding value. Inline/equivalent/UA/essential have separate conditions. | Inspect hit area, adjacent targets and actual exception at declared viewports. |
| Enhanced web pointer target | [WCAG 2.2 SC 2.5.5](https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html), AAA requirement | 44×44 CSS px with its own exceptions. A project can choose larger targets without claiming AAA conformance for the whole product. Native pt/dp require platform guidance. | Measure the interactive area, not only the visible icon. |
| Target acquisition | [MacKenzie, Fitts' Law](https://www.yorku.ca/mack/hhci2018.html), HCI model | Distance, target width, input method and calibrated coefficients matter. This does not choose a universal CTA size or position. | Evaluate reach, error and acquisition in the actual interaction context. |
| Recognition, consistency, feedback, recovery | [Nielsen's heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), author guidance | General review principles, not a required page layout or evidence of observed user success. | Walk through tasks; record observed friction separately from interpretation. |
| Chunking | [NN/g, Chunking](https://www.nngroup.com/articles/chunking/), practice guidance | Organize meaningful relationships. Memory experiments do not prescribe a visible menu count. The local IA owner explicitly rejects a 7-item navigation rule. | Inspect recall burden, labels and findability; test with users when the decision warrants it. |

For other named effects, use the name as a hypothesis prompt until the relevant
primary study and task fit are checked. Do not infer effect magnitude, a universal
threshold or product impact from an effect name.

Decision record:
`task → requirement/heuristic/hypothesis → source + version/level + checked date →
scope + exception → adopted value/behavior → trade-off → verification → remaining unknown`.

Example: a dense desktop toolbar has 28×28 CSS px targets. This is not automatically
a WCAG AA failure because it is below 44px. Inspect 2.5.8 and actual spacing, then
separately judge usability for the audience. A touch booking action may intentionally
use 48 CSS px as a project choice, not a clinical or universal standard.
