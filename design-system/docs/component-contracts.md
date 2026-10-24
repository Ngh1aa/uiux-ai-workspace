# Component contracts

Each contract states what the component is for, its anatomy, variants, states, accessibility
obligations and the misuse it prevents. CSS lives in `components/components.css`; tokens in
`tokens/component/components.json`. A component change that breaks a contract below is a
**major** version change (see [governance](governance.md)).

State is carried by native HTML attributes, never by classes alone, so the visual state and the
accessibility tree cannot disagree.

| Component | Class | State attributes |
|---|---|---|
| Button | `.ds-button` | `disabled`, `aria-disabled`, `aria-busy`, `aria-pressed` |
| Icon button | `.ds-icon-button` | `aria-label` (required), `aria-pressed` |
| Field | `.ds-field` | `aria-invalid`, `aria-describedby`, `disabled` |
| Chip | `.ds-chip` | `aria-pressed` (filter) or `aria-selected` (inside `role="tablist"`) |
| Badge | `.ds-badge` | none, purely presentational text |
| Card | `.ds-card` | none; interactive variant is an `<a>` or `<button>` |
| List item | `.ds-list-item` | interactive only when the element is `<a>` or `<button>` |
| Tab bar | `.ds-tab-bar` | `aria-current="page"` on exactly one item |
| Banner | `.ds-banner` | `role="status"` or `role="alert"` by urgency, `hidden` |
| Toast | `.ds-toast` | `role="status"`, `hidden` |
| Empty state | `.ds-empty` | `hidden` |
| App bar | `.ds-app-bar` | none |
| Avatar | `.ds-avatar` | `aria-hidden` when the name is shown alongside |
| Link | `.ds-link` | none |
| Checkbox, radio | `.ds-check`, `.ds-check--radio` | native `checked`, `disabled`, `aria-invalid` |
| Tabs | `.ds-tabs` | `aria-selected` on one `role="tab"`, `hidden` on inactive panels |
| Dialog | `.ds-dialog` | native `<dialog open>` via `showModal()`, `aria-labelledby` |
| Menu | `.ds-menu` | trigger `aria-expanded`, `aria-haspopup="menu"`; menu `hidden` |
| Tooltip | `.ds-tooltip` | `role="tooltip"`, trigger `aria-describedby` |
| Table | `.ds-table` | wrap: `tabindex="0"`, `role="region"`, `aria-label`; `<caption>` and `<th scope>` required |

---

## Button

**Purpose.** Commit or trigger an action in the current context. Navigation to another page is a
link (`<a class="ds-button">` is allowed only when the destination is a page and the visual
weight of a button is justified).

**Anatomy.** Container, label (required), optional leading or trailing icon, optional busy spinner.

**Variants and hierarchy.**

| Variant | Use | Limit |
|---|---|---|
| `--primary` | The one action the screen exists for | One per view region. Two primaries mean the hierarchy decision was not made |
| `--secondary` | Alternatives and reversible actions | Any number |
| `--tertiary` | Low-emphasis actions inside cards and lists | Must still read as an action (verb label, icon or position) |
| `--danger` | Destructive commits (delete, cancel booking) | Pair with confirmation proportional to reversibility |

Sizes: `--sm` (36px, dense lists only), default (44px), `--lg` (52px, single bottom CTA).

**States.** default, hover, pressed, focus-visible, disabled, busy. Disabled buttons that hide the
reason are a dead end: prefer an enabled button that explains what is missing on press.

**Accessibility.** Label is visible text or `aria-label` for icon-only. Busy state sets
`aria-busy="true"` and keeps the label. Hit target at least 44x44 CSS px at default size.

**Do not.** Use a primary button for "Cancel". Put two buttons with equal weight side by side
for unequal choices. Use color alone to signal danger (label must say what is destroyed).

## Field (text input, select)

**Purpose.** Collect one value with its label, hint and error in a fixed order.

**Anatomy.** Label (always visible, above the control), control, hint (optional), error (hidden
until validation fails). Search fields may visually hide the label but must keep it in the DOM.

**States.** default, focus-visible, invalid (`aria-invalid="true"`, 2px danger border, error text
with icon), disabled.

**Rules.**
- Validate on submit or on blur, never on every keystroke for format rules.
- On submit failure move focus to the first invalid field; the error text is referenced from
  `aria-describedby` so it is announced with the field.
- Error copy says what to do ("Nhập số điện thoại từ 9 đến 16 ký tự"), not what went wrong
  ("Sai định dạng").
- Placeholder is an example, never the label. Placeholder color is `text.tertiary`, which meets
  4.5:1 because users still have to read it.
- Field height is 52px (taller than buttons) so 17px Vietnamese text with stacked diacritics
  never clips.

## Chip (filter)

**Purpose.** Toggle a filter or choose one view among a few siblings.

**Rules.** Filter chips use `aria-pressed`. A single-choice set inside `role="tablist"` uses
`aria-selected` and roving tabindex. Selected state changes background, text and border, not
color alone. Show counts (`.ds-chip__count`) when they help the user predict an empty result.

## Badge (status)

**Purpose.** Show a state the user did not just cause (confirmed, pending, failed).

**Rules.** Always icon plus text. Tone maps to meaning, not decoration:
`success` done or confirmed, `warning` needs attention or waiting on someone, `danger` failed or
blocked, `info` neutral information, default neutral for archived states. Badges are not buttons;
if tapping a status does something, use a chip or a list item.

## Card

**Purpose.** Group content about one object so it can be compared or acted on as a unit.

**Variants.** default (raised, subtle shadow), `--flat` (inside another surface), `--brand`
(subtle brand surface, at most one per screen for the hero object), `--interactive` (the whole
card is a link or button; nested interactive elements are then not allowed).

**Do not.** Nest cards more than one level. Use a card as a page section wrapper by default.
Mix card heights in a list meant for comparison.

## List and list item

**Purpose.** Scan and pick from a set of similar rows.

**Anatomy.** Leading (icon tile or avatar), body (title + metadata), trailing (chevron, value or
control). Row height at least 52px when interactive. Chevron only when the row navigates.

## Tab bar (bottom navigation)

**Purpose.** Switch between 3 to 5 top-level destinations on mobile.

**Rules.**
- Every item has an icon **and** a visible text label. Icons alone are ambiguous for many
  destinations (Material and Apple HIG both show labels in bottom navigation by default), and an
  icon-only item with no accessible name fails WCAG 1.1.1 and 4.1.2.
- Exactly one item has `aria-current="page"`. The active state uses three cues: indicator pill,
  selected text color and bold label.
- Tab bar height excludes the device safe area; padding adds `env(safe-area-inset-bottom)`.
- Not for actions ("Đặt lịch" is a destination screen here, not a submit button).

## App bar

**Purpose.** Name the current screen and hold at most one leading navigation control and two
trailing actions. **Rules.** The title is the screen's `h1`/`h2` in the heading order; the back
control is an `<a>` or `.ds-icon-button` with an `aria-label` naming the destination
("Quay lại lịch hẹn"), never just "Back" when the destination is not obvious.

## Avatar

**Purpose.** Identify a person at a glance. **Rules.** Initials or image are decorative when
the name is shown next to them (`aria-hidden="true"`); when the avatar stands alone it needs an
accessible name. Initials use two letters from the given and family name as the user writes them.

## Link

**Purpose.** Navigate. **Rules.** `.ds-link` uses `text.brand` (4.5:1 on every surface it is
declared for) and keeps the underline; color is not the only cue that text is a link
(WCAG 1.4.1). Links that look like buttons must still be links when they navigate.

## Banner and toast

**Banner.** Persistent, in-flow message about the current context. Use `role="alert"` only for
errors that block the task, `role="status"` otherwise. Include an icon and text; tone tokens
match the badge.

**Toast.** Transient confirmation of something the user just did. Inverse surface, polite live
region. Never put the only copy of important information or an undo-only path in a toast.

## Empty state

**Purpose.** Explain why nothing is shown and offer the next step. Always: what is empty, why
(filter, no data yet, error), and one recovery action ("Xóa bộ lọc").

## Segmented control (v0.2)

**Purpose.** Switch between 2–5 views of the same content (Tuần / Tháng / Năm, Tất cả / Chi / Thu).

**Anatomy.** Sunken track, equal-width items, the selected item is a raised surface.

**Rules.** Items are buttons with `aria-pressed`, grouped with `role="group"` and an accessible
name. Use it for views, never for navigation between destinations (use the tab bar) and never for
more than five options (use chips or a select). Selection changes surface, weight and elevation,
not colour alone. The content below updates without moving the control.

## Switch (v0.2)

**Purpose.** Turn a setting on or off with immediate effect.

**Anatomy.** Native `<input type="checkbox" role="switch">` followed by
`<span class="ds-switch__thumb" aria-hidden="true">` inside `.ds-switch`, with a visible text label in
the same `<label>`. The thumb is a real element because Firefox does not draw pseudo-elements on inputs.

**Rules.** No Save button: the change applies at once and is confirmed by the thumb position and
the setting's effect. If the change can fail (network), revert the switch and explain inline.
Off track has a 3:1 border; on track uses `action.primary.bg` with a contrasting thumb. Disabled
switches keep their label readable and, when possible, say why. Target area is the whole row.

## Progress (v0.2)

**Purpose.** Show how much of a known total is used or complete (budget spent, upload, steps).

**Rules.** `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`; add
`aria-valuetext` when the visible value says more than a number ("112%, vượt ngân sách").
Always show the value as text next to the bar. Tones: default, `--warning` (approaching a limit),
`--danger` (over a limit). Never rely on tone alone; the text says "sắp hết" or "vượt".

## Skeleton (v0.2)

**Purpose.** Placeholder that matches the final layout while content loads (> ~300 ms).

**Rules.** Shapes mirror the real content (avatar circle, two text lines of realistic widths).
Skeleton elements are `aria-hidden`; the container sets `aria-busy="true"` and an accessible
loading label. Pulse animation stops under reduced motion. Do not show skeletons for loads under
~100 ms, and replace them in place without layout shift.

## Sheet and scrim (v0.2)

**Purpose.** A focused sub-task over the current screen (transfer money, filters, quick create).

**Anatomy.** Grabber, header with title and close button, content, one primary action at the
bottom. `.ds-scrim` dims the page behind it with `surface.scrim` (dark in both modes).

**Rules.** `role="dialog"` with `aria-labelledby`, focus moves into the sheet and returns to the
trigger on close; Esc, close button and (on touch) drag-down dismiss. If the user has entered
data, confirm before discarding. One primary action; secondary actions as tertiary buttons.
Native apps use the platform sheet (`.presentationDetents` on iOS, `ModalBottomSheet` on Android)
with these tokens rather than this markup.

## Section header (v0.2)

**Purpose.** Title a group of content on a screen, with an optional trailing link ("Xem tất cả").

**Rules.** Title uses a heading element at the right level; the trailing action is a link or
tertiary button with a specific label, not a bare chevron.

## Checkbox and radio (v0.3)

**Purpose.** Checkbox: pick any number of independent options, or accept one statement. Radio:
pick exactly one of 2–6 visible options.

**Anatomy.** `<label class="ds-check">` holding the native input, a `.ds-check__box` sibling
(`aria-hidden`; the checkbox holds a `ds-i-check` icon) and the text label. Radio adds
`.ds-check--radio`. Group related options in `.ds-fieldset` with a `<legend>`.

**Rules.** The whole label is the target (≥ 44 px tall). The native input stays in the
accessibility tree, so keyboard and screen readers need no ARIA. Error on a group: set
`aria-invalid` on the inputs and put the message after the fieldset. More than six radio options
or a long list: use a select. A setting that applies immediately is a switch, not a checkbox.

## Tabs (v0.3)

**Purpose.** Switch between panels that share one page and one context (Sắp tới / Đã khám).

**Anatomy.** `role="tablist"` with `role="tab"` buttons, an indicator under the selected tab, and
`role="tabpanel"` regions linked with `aria-controls` / `aria-labelledby`.

**Rules.** Exactly one tab has `aria-selected="true"`; others have `tabindex="-1"` and arrow keys
move between tabs (Home/End jump). Inactive panels are `hidden`. Labels are short nouns, no icons
required. Not for site navigation (links with `aria-current`) and not for filters (chips). The
tab list scrolls horizontally on narrow screens rather than wrapping.

## Dialog (v0.3)

**Purpose.** Interrupt to confirm a consequential action or collect a short input on desktop and
web. On phones prefer the sheet.

**Anatomy.** Native `<dialog class="ds-dialog">` opened with `showModal()`; header with title and
close icon button, body text, actions row with the primary action last. `.ds-dialog--static`
only renders a dialog in documentation.

**Rules.** `aria-labelledby` points at the title. The browser provides the focus trap, Esc and
inert background; return focus to the trigger on close. Destructive confirmations name the
object and the consequence in the title and use a danger button whose label repeats the verb
("Huỷ lịch"), never "OK". Do not stack dialogs.

## Menu (v0.3)

**Purpose.** A short list of actions on one object (Đổi giờ, Huỷ lịch) behind a trigger button.

**Anatomy.** `.ds-menu-anchor` wraps the trigger (`aria-haspopup="menu"`, `aria-expanded`,
`aria-controls`) and `ul.ds-menu[role="menu"]` with `role="menuitem"` buttons; dividers use
`role="separator"`. `.ds-menu--end` aligns to the trigger's right edge.

**Rules.** Opening moves focus to the first item; arrow keys move, Esc closes and returns focus;
choosing an item closes the menu. Destructive items use `--danger` and come last after a divider.
Choosing a value from a list is a select, not a menu.

## Tooltip (v0.3)

**Purpose.** A short supplementary label for an icon button or a term, for pointer and keyboard
users.

**Rules.** One sentence at most. Shown on hover and focus, linked with `aria-describedby`. Never
the only place for information someone needs to finish a task: touch screens have no hover. Icon
buttons still need their own `aria-label`; the tooltip adds to it.

## Table (v0.3)

**Purpose.** Compare records across the same attributes.

**Anatomy.** `.ds-table-wrap` (scrolls horizontally on narrow screens) around `table.ds-table`
with a `<caption>`, `<th scope="col">` headers and optional `<th scope="row">`. The wrap carries
`tabindex="0"`, `role="region"` and an `aria-label` so keyboard users can scroll it (axe
`scrollable-region-focusable`).

**Rules.** Numbers and money right-aligned in tabular figures (`.ds-table__num`); dates in one
format. Header text is secondary colour, not uppercase. Row hover is a hint, not the only cue for
interactive rows: put a real link or button in the row. Large data sets, sorting, filtering and
bulk actions follow `data-tables-and-enterprise-ux`.

