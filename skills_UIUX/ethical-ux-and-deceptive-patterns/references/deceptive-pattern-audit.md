# Deceptive Pattern Audit Reference

Read when you are running a flow review and need pattern names to cite, the regulatory hook for each, the step-count method for symmetry, or a model of a finished finding. Regulatory hooks are pointers for legal review, not legal advice; verify current text and jurisdiction before quoting.

## 1. Taxonomy with detection test and hooks

Names follow the deceptive.design taxonomy (Brignull) with groupings used in Mathur et al. and the FTC 2022 report.

| Pattern | Detection test | Regulatory hook to check |
|---|---|---|
| Confirmshaming | Does the decline label guilt or mock the user? | FTC report; EDPB guidelines (emotional steering) |
| Preselection | Is any optional paid item or consent checked by default? | GDPR consent, CJEU Planet49; EU Consumer Rights Directive (pre-ticked boxes for extra payments) |
| Drip pricing / hidden costs | Do mandatory fees appear after the first price display? | FTC fee rules (verify scope); EU price indication rules |
| Sneak into basket | Does an item enter the cart without an explicit add action? | EU Consumer Rights Directive; UCPD |
| Forced continuity | Does a trial convert to paid without clear prior disclosure and easy cancel? | ROSCA; state auto-renewal laws (verify) |
| Hard to cancel (roach motel) | Is exit harder, longer or in a different channel than entry? | ROSCA simple cancellation; CPRA symmetry; DSA Art. 25 |
| Obstruction | Are extra steps added to the user's preferred path only? | DSA Art. 25; CPRA regs |
| Nagging | Does the prompt return after decline with no lasting "no"? | DSA Art. 25 (repeated requests) |
| Fake urgency | Does the countdown reset, or is the deadline untrue? | FTC Act Section 5; UCPD (false limited-time claims) |
| Fake scarcity | Is the stock or demand claim not tied to real data? | FTC Act Section 5; UCPD |
| Fake social proof | Are reviews, counts or activity notices fabricated or cherry-picked? | FTC rules on fake reviews and testimonials (verify) |
| Disguised ads | Is paid content styled as editorial, results or UI? | FTC endorsement guides; DSA advertising transparency |
| Trick wording | Double negatives or opposite-meaning checkboxes in one form? | CPRA regs (confusing language); EDPB guidelines |
| Visual interference | Is the choice the business prefers far more salient than an equal alternative? | CPRA symmetry; EDPB guidelines |
| Bait and switch | Does an action produce a different outcome than labeled? | FTC Act Section 5; UCPD |
| Privacy zuckering | Are users steered into sharing more data than they intend? | GDPR; CPRA; EDPB guidelines |
| Comparison prevention | Is pricing structured to block comparison of plans? | UCPD (misleading omission) |

## 2. Symmetry audit method

Count, do not estimate. Record on a real device, logged in as a typical user.

| Measure | Entry path | Exit path | Pass rule |
|---|---|---|---|
| Steps (screens requiring an action) | Count | Count | Exit no more than entry |
| Channels | Web, app, phone, chat | Same list | Exit available in every channel entry was |
| Layers to reach decline | Layer number of accept | Layer number of decline | Same layer |
| Visual weight | Size, fill, contrast of accept | Same for decline | Comparable; no ghost-link decline |
| Retention offers | n/a | Count | At most one, declinable in one step |
| Confirmation | Email and screen on signup | Email and screen on exit | Both present, exit states end date |

## 3. Severity scale

- **Block**: likely unlawful in a target market, or causes unwanted charges or consent. Do not ship.
- **Fix before launch**: materially steers choice or hides terms, but harm is recoverable.
- **Improve**: neutral but unclear; increases error or regret.

## 4. Business-conflict log entry

```
Finding ID:
Pattern and evidence:
Requested by (role):
Stated business reason:
User harm:
Regulatory hook (for legal review):
Decision: remove | modify | keep
Decision owner (named role) and date:
Re-review date and counter-metrics:
```

The designer records; the owner decides. A missing owner means the finding stays open.

## 5. Counter-metrics for flows reviewed here

- Refunds and chargebacks within the first billing cycle.
- Cancellations within a short window after conversion (accidental signups).
- Support contacts tagged billing surprise, cannot cancel, did not order.
- Consent withdrawal rate after initial consent.
- Complaint volume to regulators or app stores, where visible.

## 6. Worked example: streaming subscription trial

**Before**

- Landing: "Start your free trial" button; price "then 14.99/month" in light grey footnote.
- Checkout: card required; "Add premium sound for 2.99/month" preselected; "Send me offers from partners" pre-ticked.
- Timer: "Offer ends in 09:59" resets on reload.
- Decline on upsell: "No, I like bad audio".
- Cancellation: app only via web settings, 6 screens, mandatory chat, two retention offers.

**After**

- Button: "Start 7-day free trial". Directly beneath: "Then 14.99 per month from <date>. Cancel anytime in Account > Plan, two steps. We will remind you 3 days before you are charged."
- Add-on unchecked, labeled with its price; partner offers unchecked, separate, optional.
- Timer removed (no real deadline).
- Decline label: "No thanks".
- Cancellation: available in app and web, Account > Plan > Cancel, one optional retention offer with "Continue to cancel" equal in weight, confirmation screen and email with end date.

**Symmetry check after redesign**: signup 3 steps (web and app) versus cancel 2 steps plus 1 declinable offer (web and app). Pass.

**Filled finding row (from the before state)**

| ID | Screen / step | Pattern (taxonomy name) | Evidence (what the user sees) | User harm | Regulatory hook (verify) | Severity (block / fix before launch / improve) | Neutral redesign | Owner and decision |
|---|---|---|---|---|---|---|---|---|
| F-03 | Checkout, add-ons | Preselection; sneak into basket | "Premium sound 2.99/month" checked by default | Unwanted recurring charge | EU Consumer Rights Directive pre-ticked extras; ROSCA informed consent | Block | Unchecked add-on with price in label | Head of Growth: remove (agreed) |

## 7. Review tips

- Review emails, push notifications and receipts, not only screens; forced continuity often hides in the "trial ending" email that never arrives.
- Test as a returning user and as a user who already declined once; nagging only appears on repeat visits.
- Review on the smallest supported screen; truncation can hide material terms.
