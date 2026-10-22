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
