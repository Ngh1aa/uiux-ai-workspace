# Product Strategy & Prioritization — Pinned Synthesis

Source reviewed: `assimovt/productskills@66f9cee5868d6daf9cf106b4a74090428d6fa83e` (MIT).

This reference adapts the source's positioning, prioritization, scope and metric ideas to `skills_UIUX` evidence discipline. It is not a verbatim copy and does not turn any framework into project truth.

## Positioning chain

Use the five-step logic only when positioning is actually part of the decision:

1. alternatives the best-fit audience would use without the product;
2. concrete attributes that differ from those alternatives;
3. customer outcomes enabled by those attributes;
4. customers/contexts that care most;
5. category framing that makes the value easiest to understand.

Useful tests:
- Could the “unique attribute” be verified in source/product reality?
- Would the target audience immediately understand why the difference matters?
- Is “do nothing/manual process” the strongest alternative? If yes, urgency/proof may matter more than competitor comparison.

## Evidence-weighted prioritization

A RICE-style score can structure discussion:

| Dimension | Ask | Evidence expectation |
|---|---|---|
| Reach | How many relevant users/accounts/journeys are affected in a defined period? | analytics/research/known population; otherwise UNKNOWN |
| Impact | How strongly could this move the chosen outcome? | experiment/history/research rationale; avoid fake precision |
| Confidence | How strong is the evidence behind reach/impact? | explicit source quality, not optimism |
| Effort | What design/engineering/content/QA/coordination cost is expected? | owning-team estimate/range when available |

Do not compare scores built from incompatible time windows or invented inputs. If evidence is weak, a qualitative evidence matrix is better than arithmetic theatre.

### Blocker/enabler lens

Use after the first ranking pass:

- blocker: prevents adoption/task completion/trust/retention;
- enabler: improves depth/delight after core value already works;
- mandatory: cannot be traded away (legal, safety, accessibility, security, contractual/project truth);
- optional: useful but safe to defer.

A low numerical score does not justify dropping a mandatory requirement.

## Scope with appetite

Appetite answers “what is this problem worth?” rather than pretending to predict exact duration. The useful transfer into UI/UX work is:

`fixed/reviewed resource envelope → variable breadth → preserved quality`

Scope-hammering questions:

- Does v1 fail its main user outcome without this?
- Is this a full new surface that could be replaced by a sensible default?
- Is this edge behavior actually material due to risk, trust or frequency?
- Can one well-designed path prove value before multiple variants?
- What manual/operational fallback is honest and acceptable?

Do not apply consumer-feature frequency heuristics blindly to accessibility, destructive flows, payments, security, privacy or error recovery. Low frequency can still be high consequence.

## Metrics connection

Useful product decisions connect to an outcome tree rather than a pile of vanity metrics:

`core value outcome → acquisition/activation/engagement/retention inputs → observable leaf metrics`

Pair optimization metrics with guardrails/counter-metrics. Example: improving form-start rate is not useful if completion, lead quality or trust degrades.

## Handoff to UI/UX

Translate strategy into design inputs:

- positioning → first-screen message/proof/choice architecture;
- blocker → critical journey/remediation priority;
- enabler → optional enhancement after core path;
- scope IN/OUT → Design Contract preserve/change and page-role matrix;
- metric/counter-metric → verification/analytics plan;
- confidence → prototype/research/experiment requirement.
