---
name: personalization-and-preference-ux
description: Design saved views, filters, defaults and personalized experiences with user control, transparency and safe fallback. Use when products remember user state or infer content/preferences.
---

# Personalization & Preference UX

## Goal and scope

Make remembered and inferred behavior feel helpful, predictable and reversible. Users should be able to tell what the product remembers, why it shows them something, and how to change or turn it off, and the product must still work well for someone it knows nothing about.

**When not to use**

- Consent banners, data retention, security and legal data handling in general: use `security-and-privacy`.
- AI capability boundaries, confidence and correction for generative or predictive features: use `human-ai-interaction-design`.
- Search ranking, facets and zero-result recovery: use `site-search-and-findability`.
- Saved views and column settings inside dense enterprise tables: use `data-tables-and-enterprise-ux`, then return here for persistence and sync rules.
- Manipulative defaults and pre-ticked opt-ins: use `ethical-ux-and-deceptive-patterns`.

**Prerequisites**

- Inventory of everything the product stores or infers about a user: settings, history, location, segments, model features.
- The legal basis and consent state for each data use, from the privacy owner. Verify current law for each market.
- The non-personalized experience defined as a real design, not an afterthought.

## Decisions

**Explicit versus implicit.** Classify every adaptation:
- Explicit preference: user set it (language, units, saved filter, followed topic). Persist it, show it, never override silently.
- Implicit personalization: system inferred it (recently viewed, recommended, ranked by predicted interest). Label it, explain it, make it dismissible.
- Contextual: derived from the current session or request (device, locale, referrer). Treat as a default the user can change.
Rule: when explicit and implicit conflict, explicit wins. A user who chose "Sort: newest" must not get "Recommended for you" order back on the next visit.

**What is safe to remember.** Remember by default only what saves effort and is low-risk if seen by another person on the same device (sort order, view mode, units). Ask or offer before remembering anything that reveals identity, health, finances, location history or relationships. On shared or public devices, provide a non-persistent mode.

**Sensitive-inference exclusions.** Do not infer or target on special categories (health, sexual orientation, religion, political opinion, ethnicity, union membership, biometric data) or on proxies for them (pharmacy purchases, clinic visits, religious holidays, support group pages) unless the user explicitly opted in for that purpose and the legal basis is confirmed. Also exclude inferences that could cause harm if wrong or exposed: pregnancy, financial distress, bereavement, minors. Maintain an exclusion list as part of the model spec.

**Explainability: "Why am I seeing this?"** Any implicitly personalized module or item offers a reason in plain language tied to user-visible inputs ("Because you saved 3 hiking trails near Da Lat"), plus actions: not interested, see less like this, edit the input, turn off. Do not give fake reasons; if the model cannot attribute, say the category of signal ("Based on your recent browsing on this site").

**Cold start.** First-visit experience uses editorial, popular-in-context, or user-chosen starting points, never an empty "Recommended" shelf or random items. Offer lightweight explicit onboarding (pick topics) only if it is skippable and the result is visibly used. Do not require a profile to see core content.

**Filter bubble guardrails.** Reserve part of every personalized list for diversity or exploration, decay old signals, cap repetition of the same source or item, and give an easy route to the unpersonalized view (e.g. "Latest" or "All" tab). Measure diversity and user-reported relevance, not only click-through.

**Profiling consent and rights (verify current law).**
- GDPR: profiling requires a lawful basis; users can object to profiling for direct marketing (Art. 21); decisions based solely on automated processing with legal or similarly significant effects are restricted (Art. 22). Special-category data needs explicit consent or another Art. 9 condition.
- EU Digital Services Act: online platforms must explain main recommender parameters and how to change them; very large platforms must offer at least one option not based on profiling. Verify current obligations for the product's designation.
- California CCPA as amended by CPRA: opt-out of sale or sharing for cross-context behavioral advertising, the right to limit use of sensitive personal information, and regulations on automated decision-making technology. Verify current rules and effective dates.
Design consequence: personalization toggles are real controls wired to data processing, not cosmetic switches.

**Persistence and sync.** State where each preference lives (device, browser, account) and show it in the setting ("Saved to your account, applies on all devices"). Signed-out preferences migrating to an account need a choice, not silent merging.

**Reset.** Provide per-item edit, per-category clear (history, interests), and a global reset to defaults. Reset must actually stop use of the cleared data.

## Workflow

1. Separate user-set preferences from inferred personalization (and contextual defaults).
2. Identify what can be safely remembered; apply the sensitive-inference exclusion list and confirm legal basis.
3. Provide sensible defaults without trapping users; design the cold-start state.
4. Show when personalization materially changes results or content, with a "why am I seeing this" explanation.
5. Allow reset, edit or disable for meaningful preferences; wire toggles to real processing.
6. Clarify cross-device and account sync expectations in the UI.
7. Define non-personalized fallback, used for cold start, opt-out, errors and model outages.
8. Set guardrail metrics: diversity, opt-out rate, "not interested" rate, complaints.

**Anti-patterns**

- Language or currency forced by IP location with no visible switch.
- "Personalized ads" toggle that changes nothing server side.
- Recommendations revealing sensitive life events (baby products after a pregnancy-related search) on a shared screen or in email.
- Saved filters silently lost after an app update or sign-in.
- Sort order reset to "Recommended" every visit despite user choosing otherwise.
- "Why am I seeing this" that only says "Because of your activity".
- Clearing history hides it from the user but the model keeps using it.
- Onboarding topic picker whose choices never visibly affect the feed.
- Personalized prices or eligibility with no disclosure.

**Resources**

- Need a personalization inventory template, explanation copy patterns, guardrail metrics or a worked example? Read [personalization patterns reference](references/personalization-patterns.md).
- Before release, run [personalization gate](checklists/personalization-gate.md).

**Output**

1. Personalization inventory:

| Adaptation | Type (explicit, implicit, contextual) | Input data | Sensitive? Exclusion check | Legal basis or consent | Where stored and sync scope | User control (edit, reset, off) | Explanation copy | Fallback | Guardrail metric |
|---|---|---|---|---|---|---|---|---|---|

2. Cold-start and non-personalized state designs.
3. "Why am I seeing this" copy set and controls.
4. Preference center spec: settings, defaults, sync indicator, reset scopes.

## Quality gate

Users can understand and change important preferences; personalization failure has a usable default; sensitive inference is avoided unless justified.

- PASS only if every adaptation in the inventory is classified explicit, implicit or contextual.
- PASS only if explicit preferences are never overridden by inferred behavior.
- PASS only if every implicitly personalized surface offers a reason and at least one control.
- PASS only if each meaningful preference can be edited, reset or disabled, and reset stops data use.
- PASS only if the non-personalized fallback is a designed, usable state for cold start, opt-out and outage.
- FAIL if any sensitive or proxy inference is used without documented opt-in and confirmed legal basis.
- PASS only if sync scope is shown for account-level preferences.
- PASS only if current law for each target market was verified by the privacy owner.

**Baseline and sources**

- Google People + AI Guidebook (explainability, user control, feedback).
- Microsoft Guidelines for Human-AI Interaction (Amershi and colleagues, 2019).
- NN/g research on personalization, customization and recommendation transparency.
- GDPR Articles 9, 21 and 22; EU Digital Services Act recommender provisions; CCPA as amended by CPRA and CPPA regulations. Verify current text; this is design guidance, not legal advice.
