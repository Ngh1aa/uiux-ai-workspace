# Thực hành chuyên sâu

Chỉ mở khi cần chi tiết trong mục dưới đây; WORKFLOWS.md vẫn là nguồn định tuyến duy nhất.

# Ethical UX & Deceptive Pattern Prevention

## Goal and scope

Make sure every commitment a user makes (paying, subscribing, consenting, sharing data, staying enrolled) is one they understood and chose, and that every exit is as available as the entrance. The test is not "is it legal somewhere" but "would this user make the same choice if the design were neutral and they saw all material terms". Findings are recorded as user harm and regulatory risk with an owner, never softened into "conversion optimization".

**When not to use**

- Persuasive but honest marketing structure, proof and CTA hierarchy: use `conversion-and-content`.
- Credibility, claims substantiation and organization transparency pages: use `trust-credibility-and-transparency`.
- Consent storage, data minimization and security controls: use `security-and-privacy`.
- Sign-in, MFA and recovery mechanics: use `authentication-account-and-recovery-ux`.
- Measuring whether a change harmed users: use `analytics-and-experimentation` with counter-metrics, then return here for the verdict.

**Prerequisites**

- The full flow as shipped (or prototype), including every screen, email and confirmation, across web and app.
- Pricing, renewal, trial and cancellation terms from the business, not from marketing copy.
- Target markets, since obligations differ by jurisdiction.

## Decisions

**Where to look first (high-consequence moments)**
- Money: price display, fees, add-ons, trials converting to paid, auto-renewal.
- Consent: cookies and tracking, marketing opt-ins, data sharing or sale, AI training use.
- Commitment: subscriptions, contracts, account creation, irreversible deletion or publishing.
- Exit: cancellation, downgrade, unsubscribe, account deletion, opt-out.

**Choice symmetry (CPRA regulations on symmetry in choice; EDPB guidelines on deceptive design patterns; verify current text)**
- The decline option must be as easy to find, reach and activate as accept: same number of steps, comparable visual weight, same layer. "Accept all" on layer one with "Reject" only on layer two fails.
- Neutral labels on both options. A decline worded to shame ("No, I prefer paying full price") is confirmshaming.

**Defaults and preselection**
- Paid add-ons, insurance, donations and marketing or data-sharing consent are never preselected. Under GDPR, consent requires an affirmative act; pre-ticked boxes do not count (CJEU Planet49).

**Price and terms**
- Show the total price, including mandatory fees, at the first point a price appears, not only at the final step (drip pricing). Verify current FTC fee rules (the 2025 rule is limited to live-event tickets and short-term lodging) and EU price indication requirements for the market.
- Material terms (recurring charge, amount, frequency, when the trial converts, how to cancel) appear next to the commitment control, before the user commits, not behind a link. For negative-option offers in the US, ROSCA requires clear disclosure, express informed consent and a simple cancellation mechanism; verify the current status of FTC negative-option rulemaking.

**Cancellation proportionality**
- Cancel through the same channel and with no more steps than signup. If signup is online, cancellation is online. One retention offer is acceptable if it can be declined in one step; repeated offers, required calls or chat-only exits are obstruction. Confirm cancellation on screen and by email with the end date.

**Urgency and scarcity**
- Timers, stock counts and "N people viewing" are allowed only if they are true and tied to real inventory or real deadlines. A timer that resets on reload is fake urgency.

**Social proof and reviews**
- Testimonials, ratings and activity notices must be genuine and representative. Verify current FTC rules on fake reviews and testimonials before approving review displays.

**Interface interference and sneaking**
- Do not use visual hierarchy, disguised ads, trick questions (double negatives) or bait-and-switch to steer a choice. Do not add items to the cart or change plan without an explicit action.

**Experiments**
- An A/B test that wins by increasing accidental purchases, unwanted subscriptions or failed cancellations is a harm, not a win. Require counter-metrics: refund rate, chargebacks, cancellation-within-N-days, support contacts, complaint volume.

## Workflow

1. Identify moments involving money, consent, privacy, subscription or irreversible commitment; list each with screen reference.
2. Compare prominence of accept versus decline/cancel choices: steps, layer, size, contrast, label tone.
3. Check hidden fees, forced continuity, preselection, fake urgency/scarcity and confirmshaming, plus nagging, obstruction, sneaking and disguised ads using the taxonomy in the reference file.
4. Make cancellation/reversal proportionate to signup effort: count steps and channels for both.
5. Surface material terms before commitment, adjacent to the control.
6. Document business-pressure conflicts as risk, not UX optimization: record the harm, the requesting stakeholder, applicable rule and the decision owner.
7. Propose a neutral redesign for each finding and the counter-metrics to watch after release.

**Anti-patterns**

- Cookie banner with a bright "Accept all" and a grey text link "Manage options" leading to 40 toggles.
- Free trial that requires a card, converts silently and discloses the price only in the terms.
- "Only 2 left!" shown on every product regardless of stock.
- Checkout that adds travel insurance by default, opt-out wording in a double negative.
- Cancellation hidden under Account > Billing > Plan > Manage > More, then a mandatory chat.
- Unsubscribe link that requires login, then asks for a reason, then "processes within 10 days".
- "No thanks, I don't want to save money" decline buttons.
- Fees for "service" and "processing" appearing only on the payment step.
- Repeated permission or upgrade prompts after the user declined, with no "don't ask again".
- Email "Your account will be deleted" used to drive re-engagement when nothing will be deleted.

**Resources**

- Need the full taxonomy with regulatory hooks, the step-count audit method or the worked before/after example? Read [deceptive pattern audit reference](../references/deceptive-pattern-audit.md).

**Output**

Deliver an ethics review containing:

1. Inventory of high-consequence moments with screen references.
2. Findings table with this header:

| ID | Screen / step | Pattern (taxonomy name) | Evidence (what the user sees) | User harm | Regulatory hook (verify) | Severity (block / fix before launch / improve) | Neutral redesign | Owner and decision |
|---|---|---|---|---|---|---|---|---|

3. Symmetry table: signup steps and channel versus cancellation steps and channel; accept versus decline steps.
4. Business-conflict log: findings where a stakeholder chose to keep the pattern, with the named decision owner.
5. Counter-metrics to monitor after release.

## Quality gate

Pass only if every statement is true:

- [ ] No fake urgency/scarcity: every timer, stock count and activity notice is traceable to real data.
- [ ] No hidden material cost: total price with mandatory fees appears at first price display; recurring terms sit beside the commit control.
- [ ] No manipulative consent: decline is as easy as accept, on the same layer, with neutral wording; nothing optional is preselected.
- [ ] No intentional obstruction of the user's preferred action: cancellation uses the signup channel and no more steps than signup.
- [ ] No confirmshaming, trick questions or sneaked items in any reviewed flow.
- [ ] Every retained risky pattern has a named decision owner in the conflict log.
- [ ] Experiments on these flows include harm counter-metrics.

**Baseline / sources**

- US FTC staff report "Bringing Dark Patterns to Light" (2022).
- US Restore Online Shoppers' Confidence Act (ROSCA), which still requires simple cancellation for online negative-option offers. The FTC's 2024 amended Negative Option Rule ("click to cancel") was vacated by the US Court of Appeals for the Eighth Circuit in July 2025; do not cite it as in force. State auto-renewal laws also apply (verify per state).
- EU Digital Services Act Article 25 (online interface design), which applies to online platforms and does not cover practices already governed by the Unfair Commercial Practices Directive or GDPR; for most commercial dark patterns the UCPD is the primary EU instrument. GDPR consent requirements and CJEU Planet49.
- EDPB Guidelines 03/2022 on deceptive design patterns in social media platform interfaces.
- California CPRA and CCPA regulations on symmetry in choice and dark patterns (verify current text).
- Harry Brignull, deceptive.design pattern taxonomy; Mathur et al., "Dark Patterns at Scale" (CSCW 2019); Gray et al. work on dark pattern ontologies.
