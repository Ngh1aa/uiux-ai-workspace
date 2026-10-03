# P1.2 Mixed-Domain Routing Stress

## Purpose

P1.2 tests ambiguous prompts that deliberately contain two plausible product domains at the same time. The goal is not to make the router multi-label. The goal is to prove that one canonical primary domain is selected from explicit product semantics, while secondary domain signals remain observable in provenance and do not leak specialist ownership.

The stress lane covers three mixed-domain families requested after P1.1:

- AI + FinTech
- SaaS / enterprise software + ecommerce
- EdTech + enterprise operations

## Arbitration contract

For prompts that explicitly state `primary product is ...` (or `the primary product is ...`):

1. Explicit primary-product semantics own `domain` and `product_archetype`.
2. If the primary clause itself contains multiple domain cues, the earliest product-defining cue in that clause owns the route. This prevents taxonomy-table order from overriding language such as `AI workspace for financial analysts`.
3. Secondary domains are preserved as `secondary_domain:<domain>` inference evidence.
4. Reordering primary and secondary clauses must not change domain, archetype, surface, flow, inferred features, or secondary-domain provenance.
5. Rejected domains must not remain as stale `domain:*` evidence.
6. Specialist composition must follow the selected primary domain/archetype only; secondary domains are provenance, not automatic skill overlays.
7. Existing P1.1 generic ecommerce-payment disambiguation remains valid when no explicit primary-product ownership is declared.
8. Feature inference must distinguish domain terminology from agent terminology: `payment orchestration` is not an agentic workflow by itself, while `AI copilot`, `AI assistant`, or explicit agent orchestration can activate the agentic feature.

## Corpus

The corpus contains 12 tasks: six ownership scenarios, each duplicated with the domain clauses reversed.

| Mixed family | Primary ownership | Expected domain | Expected archetype |
| --- | --- | --- | --- |
| AI + FinTech | AI product | `ai-software` | `ai-workspace` |
| AI + FinTech | FinTech product | `financial-services` | `payments-infrastructure` |
| SaaS + ecommerce | SaaS operations product | `enterprise-software` | `enterprise-operations` |
| SaaS + ecommerce | ecommerce product | `commerce-retail` | `checkout-commerce` |
| EdTech + enterprise | EdTech product | `education-edtech` | `learning-operations` |
| EdTech + enterprise | enterprise operations product | `enterprise-software` | `enterprise-operations` |

Each ownership scenario has A/B wording where the secondary-domain clause is moved before or after the primary-product clause. The full route signature, including inferred features, must remain identical.

## Defects exposed during dogfood

The intentionally failing first run exposed canonical defects rather than fixture-only failures:

- taxonomy iteration order could override explicit primary-product semantics, causing AI-primary prompts to become FinTech and enterprise-SaaS-primary prompts to become commerce;
- a primary clause containing two cues, such as `AI workspace for financial analysts`, could still be hijacked by the earlier domain entry in the taxonomy table;
- generic `orchestration` in feature terms caused `payment orchestration` to emit a false `agentic-workflow` feature.

The canonical fixes therefore live in shared inference, not in per-test exceptions.

## PASS criteria

Every task must prove:

- expected canonical domain,
- expected product archetype,
- `PRODUCT` change surface,
- `professional-website-redesign` flow,
- explicit-primary provenance,
- expected secondary-domain provenance,
- clean final `domain:*` evidence,
- required specialist stage skills,
- pair-level word-order invariance including inferred features.

The lane also has focused collision checks proving that bare `payment orchestration` is not agentic and that an explicit AI copilot remains agentic even when FinTech owns the primary domain.

## Evidence behavior

The JSON evidence runner executes even when the focused pytest step fails, so a red P1.2 run still uploads the resolved contracts and routing matrix for diagnosis.

## Truth boundary

A PASS proves deterministic routing for this declared ambiguity grammar. It does not claim that the system can infer unstated human priorities from any arbitrary mixed-domain sentence. When no primary ownership is explicit, normal canonical taxonomy and target-project truth remain authoritative.
