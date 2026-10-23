# Money app reference (v0.2)

A personal-finance app, "Ví Xanh", in three task-led screens built **only** from design-system
tokens and components. It exists to show the quality bar in
[`quality-bar-rubric.md`](../../../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md)
applied to a real-feeling product, and to exercise the v0.2 components (segmented control, switch,
progress, skeleton, sheet, section header).

All people, banks, amounts and merchants are synthetic. Nothing is sent.

| Screen | User question | Decision object | Key patterns |
|---|---|---|---|
| Tổng quan | Tôi còn bao nhiêu, có gì cần chú ý? | Balance hero (the one brand-strong surface) | Hide balance, quick actions with one filled primary, budget progress with text status, recent rows |
| Giao dịch | Tôi đã tiêu vào đâu? | Day-grouped rows with day totals | Large title, search, segmented filter, summary stats, empty state with reset, skeleton for older data |
| Chuyển tiền | Chuyển có đúng người, đúng số, an toàn không? | Amount field + recipient | Bottom sheet over dimmed context, quick amounts, inline over-balance error with recovery, switch, fee reassurance, button label repeats the amount |

## Craft decisions worth copying

- **One brand surface per screen.** The balance card carries the brand; everything else is neutral,
  so the eye lands on the number first.
- **Numbers are typography.** Tabular figures everywhere amounts appear; signed amounts use a true
  minus (−) and `+` with success colour, never colour alone.
- **The primary action says what will happen.** "Chuyển 500.000 ₫", updated live as the amount
  changes, instead of a generic "Tiếp tục".
- **Errors recover.** Over-balance shows the limit and two ways forward, focus moves to the field,
  and choosing a valid quick amount clears the error immediately.
- **Status bar, home indicator and a scrollable screen** make the specimen read as an app; on
  narrow viewports the frame drops away and the screens fill the width.

## Evidence

`review/` holds Chromium captures at 320, 390 and 1280 px (light and dark at 1280) and the report
from `scripts/capture-money-app.cjs`. The local run was **PARTIAL**: Chromium only and axe-core was
unavailable offline. CI runs the same script strictly in Chromium, WebKit and Firefox with axe-core
(`.github/workflows/design-system.yml`); the CI artifact is the authoritative result.
No screen-reader session or participant study has been run; user preference is UNKNOWN.

## Reproduce

```sh
python3 design-system/scripts/build.py
NODE_PATH=<dir containing playwright and axe-core> \
  node design-system/scripts/capture-money-app.cjs artifacts/money-app
```
