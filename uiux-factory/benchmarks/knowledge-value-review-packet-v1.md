# A50.5 Knowledge Value Trial — Blind-First Review Packet

Status: **AWAITING INDEPENDENT HUMAN REVIEW**

Do **not** open `knowledge-value-trial-mapping-v1.json` until you have recorded scores, preference and rationale for all three cases. This is procedural repository blinding, not cryptographic blinding.

## Rubric

Score **A** and **B** separately on a 0–2 scale:

- `correctness` — 0 material problem, 1 acceptable/no clear advantage, 2 materially stronger.
- `specificity_actionability` — does it give concrete decisions/checks rather than generic advice?
- `relevance_noise` — is the added detail useful for this task without distracting scope creep?
- `unsupported_claim_risk` — does it avoid inventing product/source facts or overstating certainty?
- `decision_usefulness` — would it materially help the designer/product team make the next decision?

Then record one blind preference: `A`, `B`, `TIE`, or `INSUFFICIENT`, plus a short rationale and whether either option introduces a **material regression**.

---

## Case 1 — Nova amount display

**Repository:** `Ngh1aa/Nova`  
**Domain:** financial-services  
**Stage:** implementation

**Task**

Review Nova amount-display behavior for dashboard and transaction surfaces in a multi-currency context. Produce implementation decisions and QA checks without inventing which locales or currencies the product supports.

### Output A

1. Use one shared money-formatting utility rather than formatting amounts independently inside cards, tables and transaction rows.
2. Pass the transaction/account currency into the formatter and use the user's resolved display locale when the product has one; otherwise use the project's explicit fallback rather than browser punctuation assumptions.
3. QA positive, zero, negative, large-value and decimal amounts across dashboard totals and transaction rows, including at least one non-default currency example.
4. Keep currency identity visible when two currencies could otherwise look ambiguous; do not rely on a bare symbol if project truth shows that ambiguity is possible.
5. Do not change rounding, exchange-rate or accounting behavior as part of a visual formatting fix unless those rules are documented elsewhere in the product.

### Output B

1. Model display input as numeric value + currency + locale/display context so formatting logic does not infer currency from punctuation or a symbol string.
2. Use locale/currency-aware number data or APIs for decimal and grouping separators, currency placement and negative forms; do not hard-code comma/period positions or assume the symbol always precedes the number.
3. For multi-currency surfaces, verify whether a localized symbol is unambiguous in context; where it is not, prefer an explicit currency code or another project-approved disambiguation treatment.
4. Build QA fixtures for positive, zero, negative and representative decimal values in each project-supported locale/currency combination, plus a same-symbol/different-currency ambiguity case when applicable.
5. Treat formatting as presentation only: rounding policy, exchange rates, tax/accounting rules and supported locale/currency combinations remain separate product truth and must not be inferred by the formatter.

---

## Case 2 — Lumen artwork metadata

**Repository:** `Ngh1aa/Lumen`  
**Domain:** art-culture  
**Stage:** research

**Task**

Define the information structure for a Lumen artwork-detail metadata area using only fields the collection actually provides. Preserve attribution and rights meaning without forcing the project to implement any particular collection protocol.

### Output A

1. Separate the artwork's human-readable label/title from its short summary and from the ordered descriptive metadata shown to visitors.
2. Keep publisher-required attribution or ownership text as its own required statement when the source provides one instead of burying it in a decorative caption.
3. Represent rights/license status separately from descriptive metadata, and preserve provider identity separately from creator or attribution text when the source distinguishes them.
4. Map only fields that exist in project/source truth; missing required-statement, rights or provider data should not be invented to fill the layout.
5. Lumen can still use its own visual hierarchy and immersive art direction; the reference model constrains semantic separation, not the page composition or a requirement to implement IIIF.

### Output B

1. Structure the detail area around title, artist/creator, date, medium, dimensions and source/collection fields when they are actually available.
2. Put long descriptive copy in a separate description block so the metadata list stays scannable.
3. Show attribution, credit-line or copyright/rights information near the artwork and avoid rewriting legal or ownership language supplied by the collection.
4. If the collection identifies the institution or provider, show it as provenance rather than making it look like the artist or creator.
5. Omit unknown fields or mark them unavailable according to the product's content policy; do not invent dates, rights or ownership details to make the layout feel complete.

---

## Case 3 — CENNEXT motor-service claims

**Repository:** `Ngh1aa/cennext-b2b-prototype`  
**Domain:** industrial-services  
**Stage:** research

**Task**

Define a credibility-safe claim framework for CENNEXT's industrial motor repair page. Keep the page useful for buyers while avoiding unsupported claims that a repair automatically improves efficiency or guarantees a business outcome.

### Output A

1. Separate service claims from outcome claims: describe what CENNEXT inspects, repairs, tests or documents, then state uptime, reliability, energy or savings outcomes only when project evidence supports them.
2. Attach technical claims to a traceable basis such as inspection findings, test results, repair specifications, equipment data or documented operating conditions.
3. Avoid guaranteed efficiency, savings or reliability language unless the project has evidence that supports that exact promise and scope.
4. Make the recovery/decision path visible: what the customer receives after assessment, what requires approval, and when repair versus replacement is discussed.
5. Use proof modules such as test documentation, process steps, service scope and qualified limitations instead of generic trust badges or unsupported superlatives.

### Output B

1. Distinguish five claim objects before writing copy: motor component condition, motor/drive efficiency, load or system performance, repair/rewind quality, and the repair-versus-replace decision.
2. Do not turn a repair or rewind action into an automatic efficiency-gain claim. A repair service can be real even when no measured system-level efficiency improvement has been established.
3. For every performance or savings statement, name the available basis from project truth: measured condition, test result, repair specification, equipment selection, operating profile or another traceable source.
4. Keep the service outcome hierarchy explicit: the customer may buy repair work while broader business outcomes concern uptime, reliability, energy use or system performance; those are related but not interchangeable promises.
5. When repair-versus-replace appears in the journey, frame it as a decision requiring qualified assessment and current equipment facts rather than a generic sales recommendation.

---

## Review recording contract

Record the blind results in `benchmarks/knowledge-value-human-reviews-v1.json` only after reviewing all cases. Do not change the A/B mapping, seed records or retrieval policy to fit a preferred outcome.

Until all three reviews are complete, governance must remain:

```text
expansion_recommendation = HOLD_PENDING_HUMAN
expand_allowed = false
auto_mutation_allowed = false
```

Even a later `CONSIDER_EXPANSION` verdict is advisory governance only. Adding new knowledge still requires a separate source/ownership review and explicit repository change.
