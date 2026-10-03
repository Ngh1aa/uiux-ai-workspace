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
2. Secondary domains are preserved as `secondary_domain:<domain>` inference evidence.
3. Word order must not change the canonical outcome.
4. Rejected domains must not remain as stale `domain:*` evidence.
5. Specialist composition must follow the selected primary domain/archetype only; secondary domains are provenance, not automatic skill overlays.
6. Existing P1.1 generic ecommerce-payment disambiguation remains valid when no explicit primary-product ownership is declared.

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

Each ownership scenario has A/B wording where the secondary-domain clause is moved before or after the primary-product clause. The route signature must remain identical.

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
- pair-level word-order invariance.

## Truth boundary

A PASS proves deterministic routing for this declared ambiguity grammar. It does not claim that the system can infer unstated human priorities from any arbitrary mixed-domain sentence. When no primary ownership is explicit, normal canonical taxonomy and target-project truth remain authoritative.
