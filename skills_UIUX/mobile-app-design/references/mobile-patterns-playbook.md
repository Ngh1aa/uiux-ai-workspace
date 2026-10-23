# Mobile patterns playbook

Opinionated, cross-platform guidance for the patterns that decide whether an app feels
professional. Use with the [iOS spec sheet](../../ios-app-design/references/ios-spec-sheet.md) and
[Android spec sheet](../../android-app-design/references/android-spec-sheet.md): **shared meaning,
platform-native chrome.** Each pattern lists the default, the common failure, and the check.

## 1. App structure

**Default**: 3–5 top-level destinations in a bottom tab/navigation bar; each tab keeps its own stack
and scroll position. Home answers "what needs my attention now?", not "here is everything".

- Fail: a hamburger menu hiding primary destinations on phones; tabs used as actions ("+ New");
  resetting a tab's stack when the user switches away and back.
- Check: from any screen, can the user tell where they are and get back to a top-level destination
  in one tap?

## 2. Onboarding

**Default**: get to value in under 60 seconds. Skip feature carousels; show the product working.
Ask for only what the first task needs. Defer account creation until value is shown when the domain
allows (guest mode, "try first").

- Fail: 4-slide intro carousel; mandatory sign-up before seeing anything; asking all permissions at
  launch.
- Check: count taps from install to first meaningful result. Target ≤ 5 for consumer apps.

## 3. Authentication

**Default**: passkeys or Sign in with Apple/Google first, email magic link or OTP second, password
last. Autofill for OTP (`one-time-code` / SMS retriever). Biometrics to re-enter, not to create.

- Fail: custom password rules shown only after failure; OTP field split into 6 boxes that break
  paste; no "Forgot?" on the same screen.
- Check: whole flow works with the system password manager and with screen reader.

## 4. Permissions

**Default**: request in context, at the moment of need, after a one-line in-app explanation of the
benefit ("Allow location to show clinics near you"). Design all three outcomes: allowed, denied,
limited/approximate (photos, location).

- Fail: system prompt on first launch with no context; dead end after denial.
- Check: denied path still lets the user complete the task manually (e.g. type an address).

## 5. Home and feeds

**Default**: one primary card or module answering the user's top task, then secondary modules in
priority order. Pull to refresh; show last-updated time when data is time-sensitive.

- Fail: equal-weight grid of 8 cards; marketing banners above the user's own data.
- Check: squint test — the top task wins.

## 6. Lists and detail

**Default**: rows with a clear primary line, one secondary line, optional leading visual and
trailing meta/chevron. Swipe actions as accelerators only. Detail opens with push; edits in sheets.

- Fail: cards for everything (cards are for heterogeneous content; rows for homogeneous lists);
  chevrons on rows that do not navigate.
- Check: list remains scannable at largest text size; rows don't jump when images load.

## 7. Search and filters

**Default**: search field reachable from the top level; recent searches and suggestions on focus;
results update as you type with debounce (~250 ms); filters in a sheet with a live result count on
the apply button ("Show 24 results"). Active filters visible as removable chips.

- Fail: filters that reset when returning from a result; "No results" with no suggestion.
- Check: zero-results state offers a correction, a broader query or clearing filters.

## 8. Forms and input

**Default**: one column, labels above fields, correct keyboard type, autofill hints, inline
validation on blur (not per keystroke), error text below the field with the fix. Long forms split
into steps with a progress indicator and saved drafts. Primary action sticky above the keyboard.

- Fail: placeholder as the only label; disabling Submit without saying why; losing data on back.
- Check: complete the form with keyboard only (external keyboard) and with VoiceOver/TalkBack.

## 9. Feedback, loading and errors

| Situation | Pattern |
|---|---|
| < 100 ms | No indicator |
| 100 ms – 1 s | Subtle inline indicator, keep layout stable |
| > 1 s, content | Skeleton matching final layout |
| > 3 s, task | Progress with explanation; allow leaving |
| Success of minor action | Inline change or toast/snackbar (with Undo for destructive) |
| Recoverable error | Inline message + retry; keep user input |
| Blocking error | Full-state screen: what happened, what to do, one primary action |
| Offline | Banner + cached content + queued actions with clear sync status |

Prefer **optimistic UI with Undo** over "Are you sure?" dialogs for reversible actions. Use
confirmation dialogs only for irreversible, high-cost actions, and name the consequence in the button
("Delete 3 photos").

## 10. Empty states

Three different empties, three designs:
1. **First use** — explain value + one primary action ("Add your first account").
2. **No results** — say why and how to broaden.
3. **Cleared / done** — positive, light ("All caught up").

Fail: a grey icon and "No data".

## 11. Notifications and badges

Default: user-controlled categories; every notification is actionable and deep-links to exact
content; badges count items needing action, not marketing. Ask notification permission after the
user has seen value and at a moment the benefit is obvious (e.g. after booking: "Get a reminder?").

## 12. Settings

Default: grouped list, most-used first; toggles apply instantly; destructive account actions at the
bottom, separated. Mirror system settings (appearance, text size) instead of duplicating them unless
the app needs an override.

## 13. Paywalls and monetisation (ethics required)

Default: show the value and price plainly, the trial end date and how to cancel, a visible close
control, and restore purchases. Follow `ethical-ux-and-deceptive-patterns`.

Fail: hidden close button, pre-selected most-expensive plan with misleading per-week framing,
confirmshaming copy.

## 14. Gestures and motion

Every gesture has a visible alternative. Motion explains spatial relationships (push = from right/
trailing, sheet = from bottom, container transform for card → detail). Keep durations within the
[craft standards](../../ui-craft-and-visual-qa/references/craft-standards.md#8-motion) and support
Reduce Motion.

## 15. Platform divergence table

| Concern | iOS | Android |
|---|---|---|
| Primary nav | Tab bar | Navigation bar (rail on medium+) |
| Back | Edge swipe + nav bar back | System back (predictive) + top-bar Up |
| Primary create action | Nav bar "+" or inline button | FAB |
| Secondary actions | Context menu, action sheet | Overflow menu, bottom sheet |
| Selection controls | Switch, segmented control | Switch, chips, segmented buttons |
| Transient feedback | Inline change, HUD-style toast (custom) | Snackbar |
| Typeface | SF Pro (or brand) on Dynamic Type styles | Roboto Flex / brand on M3 roles |
| Units | pt | dp / sp |

Shared across both: information architecture, copy, iconography meaning, colour roles, states,
data formatting and brand moments.

## 16. Review questions before handoff

1. Does every screen have a defined empty, loading, error and offline state?
2. Does the app survive largest text size, dark mode and one-handed use?
3. Are system conventions (back, sheets, share, permissions) respected on both platforms?
4. Is there exactly one primary action per screen region?
5. Can a first-time user finish the top task without help?
