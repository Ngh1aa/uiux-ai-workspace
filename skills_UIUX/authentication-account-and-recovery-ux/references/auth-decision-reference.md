# Auth Decision Reference

Read when you are specifying a concrete sign-in, MFA or recovery flow and need the rule table, the state matrix or a model of what a finished decision row looks like. The main skill holds the decisions; this file holds the detail.

## 1. Risk tier to friction

Pick the tier from what an attacker gains, not from how sensitive the brand feels.

| Tier | Example services | Minimum sign-in | MFA | Recovery strength |
|---|---|---|---|---|
| Low | Newsletter prefs, saved recipes | Password or magic link or passkey | Optional, offered | Email link to bound address |
| Medium | Consumer SaaS, ecommerce with stored cards | Password or passkey | Offered, encouraged after first sensitive action | Bound channel plus notification; recovery codes if MFA on |
| High | Admin consoles, financial, health records | Passkey or password plus MFA | Required, phishing-resistant preferred | Second factor or recovery codes; assisted path with identity proofing |

Map the tier to NIST authenticator assurance levels (AAL1 to AAL3) only after checking the current SP 800-63B revision; do not copy level requirements from memory into a spec.

## 2. Password rules (verify current SP 800-63B revision)

| Rule | Do | Do not |
|---|---|---|
| Length | Minimum per current NIST revision (Rev. 4: 15 single-factor, 8 when part of MFA); accept 64 or more | Cap at 12 or 16 |
| Characters | Any printable ASCII, space, Unicode; normalize Unicode before hashing | Reject spaces or emoji |
| Composition | None | "1 uppercase, 1 number, 1 symbol" |
| Blocklist | Breached, dictionary, repetitive, service-name and username-derived values | Silent rejection with no reason |
| Rotation | Only on evidence of compromise | Every 90 days |
| Hints / KBA | Never | "Your hint: dog's name" |
| Entry aids | Paste, show toggle, password managers | Paste blocking, confirm field without show toggle |

Strength meters are optional. If used, base them on the blocklist and length, not on character classes, and never block a long passphrase because it is "all lowercase".

## 3. Field markup that keeps managers and autofill working

| Field | `autocomplete` | Notes |
|---|---|---|
| Email or username on sign-in | `username` (plus `email` type input when it is an email) | Keep it in the DOM on the password step |
| Password on sign-in | `current-password` | Show toggle; no paste block |
| Password on sign-up / change | `new-password` | Lets managers generate a strong password |
| OTP | `one-time-code`, `inputmode="numeric"` | One input preferred; if split boxes, full-code paste fills all |
| Passkey | `username webauthn` on the username field for conditional UI | Offer passkey before asking for a password |

## 4. Flow state matrix

Every flow must specify each column. Empty cells are design debt.

| Flow | Happy path | Wrong input | Throttled / locked | Channel unavailable | Expired link/code | Context return |
|---|---|---|---|---|---|---|
| Sign-in | Lands on origin page | Generic "email or password is incorrect" | Delay plus step-up, state wait time | n/a | n/a | Origin URL kept through redirect |
| Magic link | Link signs in the requesting device | n/a | Rate limit sends per address | Offer password or code entry | Explain, one-tap resend | Code fallback for cross-device |
| MFA challenge | Remembered method first | Retry count shown | Fall back to other method | "Use another method" link always visible | Resend after cooldown | Same as sign-in |
| Reset request | Uniform confirmation | Same message as success | Same message, silent throttle | Link to assisted recovery | Explain, restart | Return to sign-in with email prefilled |
| Assisted recovery | Ticket with timeline | Plain refusal reason | n/a | Alternate contact route | n/a | Owner notified on completion |
| Session expiry | Warning before timeout, extend option | n/a | n/a | n/a | Re-auth in place | Draft and scroll position preserved |

## 5. Message patterns

- Sign-in failure: "That email and password do not match. Try again or reset your password."
- Reset request: "If an account exists for that email, we sent a reset link. It expires in 30 minutes." (Use your real expiry.)
- Throttle: "Too many attempts. Try again in 5 minutes, or sign in with another method." State the real wait.
- Recovery notification: what changed, when, from which device or location if known, and a single "This was not me" action that locks and starts recovery.

Avoid "invalid credentials", error codes without explanation, and blame language.

## 6. Worked example: sign-in plus recovery for a B2B admin console

**Before**

- Page 1: email. Page 2: password only, no username field in the DOM. Paste blocked on password.
- Rules: 8 to 16 characters, must include a symbol, rotate every 90 days.
- MFA: SMS only, enrolled once.
- Reset: "No account found for that email" on unknown addresses.
- Recovery after phone loss: three security questions.
- After sign-in: always lands on dashboard, losing the invite link the admin clicked.

**After**

- Passkey offered first via conditional UI; password fallback in a single form with hidden `username` on step 2; paste and show toggle allowed.
- Rules: length per current NIST revision, accept 64+, breached-password check, no rotation.
- MFA required (high tier): passkey or security key preferred, authenticator app fallback, SMS allowed only as a third option; enrollment completes only after a second method or recovery codes are saved.
- Reset: uniform confirmation message and similar response timing.
- Recovery: second registered factor or recovery code; if none, assisted recovery with an org-admin approval and a stated timeline; owner notified by email.
- Origin URL (the invite link) preserved through sign-in, MFA and recovery.

**Filled decision row**

| Flow step | Risk tier | Method / control | Error and edge states | Enumeration exposure | Accessibility check (SC) | Context returned to |
|---|---|---|---|---|---|---|
| MFA challenge | High | Passkey, then TOTP, then SMS | Wrong code: retry count; 5 fails: 10-minute delay plus "use another method" | None: challenge only after password success | 3.3.8: passkey and OTP autofill/paste satisfy the mechanism; 1.3.5 tokens set | Invite acceptance page from original link |

## 7. Test script additions

- Sign in using only a password manager, never typing.
- Sign in with a screen reader; confirm OTP field label, error announcement and focus placement.
- Complete recovery with the phone switched off.
- Start on a deep link on mobile, finish the magic link on desktop.
- Let the session expire mid-form and confirm nothing is lost.
