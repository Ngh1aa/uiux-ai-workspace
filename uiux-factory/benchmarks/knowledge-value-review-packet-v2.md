# A50.5R Knowledge Revision — Blind-First Review Packet (Round 2)

Status: **AWAITING ROUND-TWO HUMAN REVIEW**

Do **not** open `knowledge-value-trial-mapping-v2.json` until you have recorded scores, preference and rationale for all three cases.

This remains procedural repository blinding, not cryptographic blinding. The same reviewer saw round-one outputs, so carryover memory is a known limitation; round two compensates by swapping A/B labels and keeping the revised cases' baseline outputs fixed.

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

1. Use one shared money-formatting boundary across equivalent dashboard totals, cards, tables and transaction rows, with numeric value + currency + locale/display context as explicit inputs rather than deriving currency from punctuation or a symbol string.
2. Format with locale/currency-aware number data or APIs for decimal/grouping separators, currency placement and negative forms. Use the product's resolved display locale when project truth defines one; otherwise require an explicit project fallback instead of silently relying on browser-default punctuation.
3. Create a QA matrix covering positive, zero, negative, large grouped and representative decimal values across each project-supported locale/currency combination, plus at least one non-default currency and a same-symbol ambiguity case when applicable; compare equivalent values across dashboard totals and transaction rows for consistency.
4. Keep currency identity visible where a localized symbol is ambiguous in the actual product context; use a project-approved disambiguation treatment such as an explicit currency code rather than guessing from the symbol.
5. Treat this formatter as presentation-only: rounding, exchange-rate, tax/accounting rules and the supported locale/currency set remain separate product truth and must not be changed or inferred by a formatting implementation.

### Output B

1. Use one shared money-formatting utility rather than formatting amounts independently inside cards, tables and transaction rows.
2. Pass the transaction/account currency into the formatter and use the user's resolved display locale when the product has one; otherwise use the project's explicit fallback rather than browser punctuation assumptions.
3. QA positive, zero, negative, large-value and decimal amounts across dashboard totals and transaction rows, including at least one non-default currency example.
4. Keep currency identity visible when two currencies could otherwise look ambiguous; do not rely on a bare symbol if project truth shows that ambiguity is possible.
5. Do not change rounding, exchange-rate or accounting behavior as part of a visual formatting fix unless those rules are documented elsewhere in the product.

---

## Case 2 — Lumen artwork metadata (control)

**Repository:** `Ngh1aa/Lumen`  
**Domain:** art-culture  
**Stage:** research

**Task**

Define the information structure for a Lumen artwork-detail metadata area using only fields the collection actually provides. Preserve attribution and rights meaning without forcing the project to implement any particular collection protocol.

### Output A

1. Structure the detail area around title, artist/creator, date, medium, dimensions and source/collection fields when they are actually available.
2. Put long descriptive copy in a separate description block so the metadata list stays scannable.
3. Show attribution, credit-line or copyright/rights information near the artwork and avoid rewriting legal or ownership language supplied by the collection.
4. If the collection identifies the institution or provider, show it as provenance rather than making it look like the artist or creator.
5. Omit unknown fields or mark them unavailable according to the product's content policy; do not invent dates, rights or ownership details to make the layout feel complete.

### Output B

1. Separate the artwork's human-readable label/title from its short summary and from the ordered descriptive metadata shown to visitors.
2. Keep publisher-required attribution or ownership text as its own required statement when the source provides one instead of burying it in a decorative caption.
3. Represent rights/license status separately from descriptive metadata, and preserve provider identity separately from creator or attribution text when the source distinguishes them.
4. Map only fields that exist in project/source truth; missing required-statement, rights or provider data should not be invented to fill the layout.
5. Lumen can still use its own visual hierarchy and immersive art direction; the reference model constrains semantic separation, not the page composition or a requirement to implement IIIF.

---

## Case 3 — CENNEXT motor-service claims

**Repository:** `Ngh1aa/cennext-b2b-prototype`  
**Domain:** industrial-services  
**Stage:** research

**Task**

Define a credibility-safe claim framework for CENNEXT's industrial motor repair page. Keep the page useful for buyers while avoiding unsupported claims that a repair automatically improves efficiency or guarantees a business outcome.

### Output A

1. Distinguish the claim object before writing copy: motor component condition, motor/drive efficiency, load or system performance, repair/rewind quality, and the repair-versus-replace decision. Keep a repair action separate from any claim of measured efficiency, uptime, reliability or savings.
2. Attach every performance or savings statement to the project evidence actually available, such as inspection findings, test results, repair specifications, equipment data, operating conditions or another traceable source; no repair or rewind action should automatically become an efficiency-gain claim.
3. Make the buyer decision path visible when project truth supports it: reported problem/intake → assessment basis → documented finding → repair/rewind/replace options as applicable → customer approval point → performed work → test/verification evidence → return-to-service or follow-up information.
4. Prefer proof modules that expose traceable service evidence—inspection findings, before/after test documentation, repair scope/specification, measured condition, process checkpoints, qualified limitations and approval records—rather than generic trust badges or unsupported superlatives.
5. Frame repair-versus-replace as a decision requiring qualified assessment and current equipment facts. Explain what evidence the buyer receives and what still requires customer approval, while keeping business outcomes such as uptime, reliability, energy use and system performance distinct from the service itself.

### Output B

1. Separate service claims from outcome claims: describe what CENNEXT inspects, repairs, tests or documents, then state uptime, reliability, energy or savings outcomes only when project evidence supports them.
2. Attach technical claims to a traceable basis such as inspection findings, test results, repair specifications, equipment data or documented operating conditions.
3. Avoid guaranteed efficiency, savings or reliability language unless the project has evidence that supports that exact promise and scope.
4. Make the recovery/decision path visible: what the customer receives after assessment, what requires approval, and when repair versus replacement is discussed.
5. Use proof modules such as test documentation, process steps, service scope and qualified limitations instead of generic trust badges or unsupported superlatives.

---

## Review recording contract

Record the blind results in `benchmarks/knowledge-value-human-reviews-v2.json` only after reviewing all three cases. Do not change the A/B mapping, revised knowledge records, baseline outputs or governance threshold to fit a preferred outcome.

Until all three reviews are complete, governance must remain:

```text
expansion_recommendation = HOLD_PENDING_HUMAN
expand_allowed = false
auto_mutation_allowed = false
```

Round two may justify opening A50.6 only if the existing evaluator derives `CONSIDER_EXPANSION`: no material regression, no baseline preference, knowledge preferred in at least 2/3 cases, and the knowledge condition strictly stronger on both `specificity_actionability` and `decision_usefulness` in at least 2/3 cases.
