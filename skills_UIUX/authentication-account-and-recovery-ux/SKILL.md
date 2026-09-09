---
name: authentication-account-and-recovery-ux
description: Design sign-in, account creation, verification, MFA and recovery flows that balance security, accessibility and completion. Use for member areas, admin tools, SaaS or transactional services.
---

# Authentication, Account & Recovery UX

## Workflow
1. Verify that an account is truly required.
2. Support password managers, paste and autofill.
3. Design validation without leaking sensitive account state unnecessarily.
4. Offer clear MFA choices and fallback/recovery.
5. Design recovery around verified identity, not trivia questions.
6. Preserve pre-auth user context after successful authentication.
7. Provide understandable security/error feedback.

## Quality gate
Authentication does not block password managers; recovery has a realistic accessible path; errors avoid unnecessary account disclosure; high-friction checks are justified.
