# Task-led mobile specimen

Open `index.html` directly or serve this directory. No build, external images,
remote fonts, credentials or backend is required.

This original, synthetic example demonstrates reusable reasoning, not an approved
CareFlow redesign or a universally beautiful template:

| Screen | UX decision | Visual consequence | Do not transfer |
|---|---|---|---|
| Overview | Find the next confirmed appointment | Time-led ticket, contextual action, quieter preparation tiles | Clinic identity, appointment data, default hero on every screen |
| Selection | Compare and find an appointment | Stable rows, state filters, search and reset | Different card sizes that make comparison harder |
| Task | Check contact details and correct input | Input-first composition, inline error, review and back retaining input | Decorative photo above fields, simulated submission claims |

The clinic, people and dates are synthetic. No request is sent. State changes and
input validation demonstrate interactions; they are not healthcare policy.
System font is intentional for a portable specimen, not a replacement for any
project's approved typeface. Palette and dimensions are hypotheses to adapt.

## Reproduce the browser checks

Use an existing Playwright installation, with Chromium and WebKit available.
Point `NODE_PATH` to that installation if needed; do not change a target's package
versions merely to run the specimen.

```sh
node skills_UIUX/visual-design-direction/examples/mobile-care/capture.cjs artifacts/mobile-care
```

The script checks search/filter/empty reset, invalid input, back with retained
input, visible feedback, console errors and horizontal overflow at 320/390/1280.
It also applies an enlarged-text stress style; this is not native Dynamic Type or
a formal browser-zoom accessibility audit. Capturing does not mark images inspected.

## Recorded visual review

Reviewer: agent heuristic, 2026-10-20. No human preference study.
Opened `review/chromium-1280.png`, `review/chromium-320.png` and
`review/webkit-390.png`; see `review/manifest.json` for source/capture hashes.
Browser matrix: `review/browser-report.json`. Color pairs: `review/contrast.json`.

Observed fixes:

- Muted ticket labels on pastel changed to navy; navy/mint 12.99:1 and navy/blue
  12.16:1 at palette endpoints.
- Search placeholder now explicitly uses the text-secondary token with full opacity.
- Pending, confirmed and completed use distinct semantic surfaces plus text/symbol.
- Hidden form/review uses explicit hidden behavior; back preserves contact input.

The examples retain the same header family for navigation consistency; their
decision objects differ. A real visual-direction exploration must still compare
alternatives on the same task/content and test brand fit. These three different
tasks do not constitute an A/B comparison or an aesthetic benchmark.

| Sign | Verdict | Location / role |
|---|---|---|
| AI-01 competing neon | không xuất hiện | All three screen surfaces in the opened captures; muted blue/mint, one dark action |
| AI-02 dark/glow | không xuất hiện | Header, ticket and action areas; no glow or dark page theme |
| AI-03 emoji controls | không xuất hiện | Preparation controls and navigation; simple text symbols support named controls |
| AI-04 default purple gradient | không xuất hiện | Headers/ticket; blue/mint only |
| AI-05 cards/nesting | có mục đích rõ | Overview groups next visit and preparation; selection uses comparable rows, form uses one summary group |
| AI-06 colored left bars | không xuất hiện | All list and summary regions |
| AI-07 status dots | không xuất hiện | Appointment badges use named fixture states and symbols, no online/live dots |

Remaining limitations: narrow/desktop browser evidence only; no native device,
screen-reader session, independent human review, real clinic data or proven product
impact. No imagery is needed to complete these three sample tasks. Photo-led
directions require a separately inspected, licensed asset reference.
