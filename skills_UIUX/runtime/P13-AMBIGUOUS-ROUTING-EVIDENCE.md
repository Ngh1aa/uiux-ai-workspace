# P1.3 Ambiguous Routing Evidence

## Purpose

P1.3 covers mixed-domain tasks where the prompt does **not** declare a primary product owner. P1.2 proved that explicit ownership can be respected; P1.3 proves that the router does not invent ownership when the language itself is genuinely ambiguous.

The stress corpus covers:

- AI + FinTech
- SaaS / enterprise software + ecommerce
- EdTech + enterprise operations

## Canonical behavior

When two or more credible domain signals remain after existing bounded disambiguation rules:

1. `GoalInterpreter` returns `routing_status=ambiguous`.
2. `domain` and `product_archetype` become `unresolved` instead of exposing a taxonomy-order winner as canonical truth.
3. `candidate_domains` contains the deterministic competing domain set.
4. inference confidence is reduced (`0.45` for two candidates, `0.35` for three or more).
5. provenance includes `domain_conflict:<domains>`, `routing_status:ambiguous`, and `routing_action:needs-evidence`.
6. `FlowPlanner` fails closed with `AmbiguousRoutingError` before flow selection or specialist composition.

## Target-project truth recovery

A caller that has source-of-truth evidence may pass:

```python
{
    "domain": "commerce-retail",
    "product_archetype": "checkout-commerce",
    "source": "repository-profile",
}
```

The truth is accepted only when its domain is one of the detected candidates. A matching truth produces:

- `routing_status=resolved`,
- `resolution_source=target-project-truth`,
- confidence `0.90`,
- retained `candidate_domains` and conflict provenance,
- `routing_resolution:target-truth-><domain>`,
- normal `FlowPlanner` + specialist composition.

A truth domain outside the observed candidate set is rejected and the contract remains ambiguous.

`ProfessionalWebsiteFlow` threads the same optional `target_truth` through the canonical interpreter and planner; it does not implement a second arbitration system.

## P1.1 / P1.2 compatibility

- Explicit `primary product is ...` language remains governed by P1.2 and is not marked ambiguous.
- Generic ecommerce checkout language containing only a weak payment token remains governed by the P1.1 commerce disambiguation rule; it does not manufacture a FinTech conflict.
- Existing non-mixed tasks preserve normal canonical confidence and routing.

## Stress corpus

P1.3 contains 18 cases:

- 12 unresolved mixed-domain tasks without primary ownership,
- 6 target-truth recovery cases,
- 6 order-invariance pairs across the three requested domain families.

The corpus intentionally reverses clause order so taxonomy tuple order or sentence order cannot silently become product ownership.

## PASS criteria

Unresolved cases must prove:

- deterministic competing domains,
- `domain=unresolved`,
- `product_archetype=unresolved`,
- confidence reduction,
- conflict + needs-evidence provenance,
- fail-closed `FlowPlanner` behavior.

Target-truth cases must prove:

- truth domain belongs to the observed candidate set,
- canonical domain + archetype recover from that truth,
- conflict provenance remains visible,
- confidence recovers without returning to implicit `0.95`,
- normal flow planning resumes,
- domain/archetype specialist skills are present.

## Truth boundary

P1.3 does not claim the system can infer unstated human priorities. Its guarantee is narrower and safer: when declared language supports multiple plausible product owners and no explicit owner exists, the system surfaces the ambiguity and waits for stronger evidence rather than choosing one silently.
