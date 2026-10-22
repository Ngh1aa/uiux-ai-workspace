---
name: authentication-account-and-recovery-ux
description: Design sign-in, account creation, verification, MFA and recovery flows that balance security, accessibility and completion. Use for member areas, admin tools, SaaS or transactional services.
---

# Authentication, Account & Recovery UX

## Goal and scope

Get the right person into the right account with the least friction the risk allows, and get a locked-out legitimate user back in without opening a door for an attacker. Authentication is judged on three axes at once: completion (people finish), security (attackers do not), and accessibility (nobody is excluded by memory, vision, motor or cognitive demands). A flow that wins one axis by sacrificing another is not done.

**When not to use**

- General data handling, encryption, consent storage or threat modelling beyond the auth UI: use `security-and-privacy`.
- Long multi-step onboarding or KYC forms after the account exists: use `complex-forms-and-wizards`.
- Field-level validation and input patterns not specific to credentials: use `interaction-patterns-and-form-ux`.
- Generic loading, error and retry states: use `state-feedback-and-error-recovery`.
- Deciding whether a signup wall or forced account creation is manipulative: use `ethical-ux-and-deceptive-patterns`.

**Prerequisites**

- Risk tier of the service (what an attacker gains: content, money, admin power, personal data). This sets the assurance level and how much friction is justified.
- Who signs in (consumers, staff, admins, shared devices, assistive technology users, people without a smartphone).
- Which identity provider, MFA methods and recovery channels engineering can actually support.

## Decisions

**Is an account needed at all?**
- Guest checkout, magic-link continuation or a saved-progress code beats an account when the user's goal is a one-off transaction. Require an account only when the user benefits from persistence or the law/risk demands identity. Defer account creation until after the value moment where possible ("save your order history" after purchase).

**Passwords (NIST SP 800-63B; verify current revision)**
- Length is the control, composition rules are not. Revision 4 sets a 15-character minimum for single-factor passwords and 8 when the password is one factor of MFA; accept at least 64 characters. Do not require mixed character classes.
- Accept all printing ASCII, spaces and Unicode. Do not silently truncate.
- Check new passwords against a blocklist of breached, common and context-specific values; explain the rejection in plain words.
- No forced periodic rotation; force a change only on evidence of compromise.
- No password hints and no knowledge-based questions ("mother's maiden name") for authentication or recovery.
- Allow paste and offer a show-password toggle.

**Password managers and autofill (WCAG 2.2 SC 1.3.5, 3.3.8)**
- Mark fields with `autocomplete="username"`, `current-password`, `new-password`, `one-time-code`. Keep username and password in one `<form>` with a submit, even when shown on separate steps (keep a hidden or read-only username field on the password step).
- SC 3.3.8 Accessible Authentication (Minimum, AA): no step may require a cognitive function test (remembering, transcribing, solving a puzzle) unless an alternative exists or a mechanism helps (paste, autofill, password manager). Blocking paste into a password or OTP field is a failure.
- Split OTP boxes are acceptable only if paste of the full code into the first box fills all of them and autofill works.

**MFA choice**
- Prefer phishing-resistant methods (passkeys/WebAuthn, platform or roaming security keys). Offer an authenticator app as the common fallback. SMS and voice OTP are treated as a restricted, phishable method in 800-63B (verify current revision): allow as fallback where the audience needs it, never as the only strong option for admin or financial accounts.
- Require at least two registered methods, or one method plus recovery codes, before MFA is considered set up for high-risk accounts.
- "Remember this device" is a risk decision: state the duration and let users revoke remembered devices.

**Error messages and enumeration (OWASP Authentication and Forgot Password guidance)**
- Sign-in failure: one message for wrong username or wrong password. Reset request: "If an account exists for that address, we sent a link" for every input, with similar response time.
- Signup is the honest exception: telling someone an email is taken is usually necessary; mitigate with rate limits and by sending a "someone tried to register" email instead of revealing it on screen when risk is high.
- Throttle failed attempts per account (800-63B caps consecutive failures at 100 before lockout; verify current guidance). Prefer progressive delays and step-up checks over hard lockout that becomes a denial-of-service tool.

**Recovery**
- Recovery is an authentication path and must be at least as strong as the weakest factor it replaces. Use a verified channel (email or phone already bound), recovery codes, or a second registered authenticator. Never security questions.
- Notify the account owner on every recovery, factor change and new-device sign-in, through a channel other than the one just used where possible.
- Provide a human-assisted path for users who lost every factor, with identity proofing proportional to risk and a stated timeline.

**Context preservation**
- Return users to the exact page, cart, draft or deep link they started from after sign-in, signup, verification and recovery. Session expiry must save in-progress input (WCAG 2.2 SC 2.2.1 Timing Adjustable, level A: users can turn off, adjust or extend a time limit, for example a warning with at least 20 seconds to extend, unless an exception applies; SC 2.2.5 Re-authenticating, AAA: continue without data loss after re-authenticating).

## Workflow

1. Verify that an account is truly required; record the guest or deferred alternative considered and why it was rejected.
2. Support password managers, paste and autofill: autocomplete tokens, single form, no paste blocking, show-password toggle, passkey offer.
3. Design validation without leaking sensitive account state unnecessarily: uniform sign-in and reset messages, inline password-rule feedback on the new-password field only.
4. Offer clear MFA choices and fallback/recovery: name each method in plain language, explain what the user needs (phone, key, app), require a backup.
5. Design recovery around verified identity, not trivia questions: bound channels, recovery codes, second factor, assisted path, owner notification.
6. Preserve pre-auth user context after successful authentication, including across email-link round trips and different devices.
7. Provide understandable security/error feedback: what happened, what to do next, how long a lock lasts, who to contact.
8. Walk every path with a screen reader, keyboard only, a password manager, and a user who has lost their phone.

**Anti-patterns**

- Username on page one, password on page two with no username field, so password managers cannot pair them.
- `onpaste="return false"` on password, confirm-password or OTP fields.
- Six separate OTP inputs that reject paste and break `one-time-code` autofill.
- "Password must contain an uppercase, a number and a symbol" with a 12-character maximum.
- Security questions as recovery, or as a "second factor".
- "No account found for jane@example.com" on the reset page.
- CAPTCHA puzzles on every sign-in with no accessible alternative (transcription or puzzle CAPTCHAs fail SC 3.3.8 unless an alternative exists; object-recognition CAPTCHAs are an AA exception that SC 3.3.9, AAA, removes).
- Magic link that opens in the email app's in-app browser, signs that browser in, and drops the original tab and cart.
- MFA enrollment forced with SMS only, then no way back in when the user changes number.
- Session timeout that discards a half-written form without warning.

**Resources**

- Need the full rule table, flow-by-flow state matrix or the worked before/after example? Read [auth decision reference](references/auth-decision-reference.md).

**Output**

Deliver an auth flow specification containing:

1. Account necessity decision (one paragraph, alternatives considered).
2. Flow map: sign-up, sign-in, MFA enroll, MFA challenge, recovery, assisted recovery, session expiry, sign-out.
3. Decision table with this header:

| Flow step | Risk tier | Method / control | Error and edge states | Enumeration exposure | Accessibility check (SC) | Context returned to |
|---|---|---|---|---|---|---|

4. Copy deck for every error, lock and notification message.
5. Test matrix: password manager, screen reader, keyboard only, no smartphone, lost all factors.

## Quality gate

Pass only if every statement is true:

- [ ] Authentication does not block password managers: correct `autocomplete` tokens, paste allowed in every credential and OTP field.
- [ ] No step requires a cognitive function test without an alternative or assisting mechanism (SC 3.3.8).
- [ ] Recovery has a realistic accessible path, including for a user with no phone and no remaining factor.
- [ ] No knowledge-based questions anywhere in authentication or recovery.
- [ ] Errors avoid unnecessary account disclosure: sign-in and reset responses are identical for existing and non-existing accounts.
- [ ] High-friction checks (CAPTCHA, step-up MFA, lockout) are justified by a named risk and have a documented alternative.
- [ ] Password rules follow length plus blocklist, with no composition or rotation rules.
- [ ] User returns to the pre-auth context after every flow, including email-link round trips.
- [ ] Owner is notified of recovery, factor changes and new-device sign-ins.

**Baseline / sources**

- NIST SP 800-63B Digital Identity Guidelines, Authentication and Lifecycle Management (verify current revision before quoting thresholds).
- W3C WCAG 2.2: SC 1.3.5, 2.2.1, 3.3.1, 3.3.3, 3.3.7, 3.3.8, 3.3.9; W3C WAI understanding documents for SC 3.3.8.
- OWASP Authentication Cheat Sheet and Forgot Password Cheat Sheet.
- W3C Web Authentication (WebAuthn) and FIDO Alliance passkey design guidance.
- HTML Living Standard autofill tokens.
