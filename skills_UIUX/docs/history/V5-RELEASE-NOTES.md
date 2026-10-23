# V5 Release Notes

## Theme
Evidence, Reference Intelligence, Measurement & Production Reliability.

## Core V5
- Evidence provenance and claim discipline.
- Service outcome measurement and continuous learning.
- Accessibility conformance-evaluation discipline.
- Visual/design drift protection.
- Adaptive skill routing/context budgeting.
- Provider-neutral multi-trial eval harness.

## Reference intelligence enhancement
- Added `design-reference-research-and-benchmark` for evidence-aware visual reference research before major design/redesign work.
- Added source-role rules for real industry sites, curated galleries/awards, Behance/Dribbble and mood sources.
- Added fit scorecard, domain source matrix, anti-copy rules, benchmark quality gate and example artifact.
- Routed reference research into `website-delivery-pipeline`, `visual-design-direction`, professional/prototype profiles and legacy website research architecture.
- Added `reference-research-001` capability eval.

## Real-world artifact / domain metaphor intelligence
- Added `real-world-artifact-and-domain-metaphor-design` for learning from physical products, printed/operational documents, spatial systems, tools and offline rituals instead of relying only on website references.
- Added five transfer layers: form, structural, information, behavioral and ritual/process metaphor.
- Added fidelity ladder `L0 REFERENCE_ONLY → L1 CUE → L2 STRUCTURAL → L3 DIRECT_FORM → L4 IMMERSIVE` with the rule to use the lowest useful fidelity.
- Added domain starter matrix covering banking, news/media, education, real estate, furniture, fashion, hospitality, travel, logistics, automotive, healthcare, government, museum and developer/SaaS contexts.
- Added reality/trust guardrails so real cards, official documents, tickets, certificates and branded artifacts must use verified current assets/specs or be labeled representative/concept/unknown.
- Added mobile/accessibility rules so semantic experience does not depend on physical resemblance.
- Added research foundations referencing current Apple familiarity/metaphor guidance, Nielsen Norman Group real-world matching/skeuomorphism guidance and OOUX object/mental-model practice.
- Added `artifact-metaphor-001` capability eval and a banking example.

## Production-grade hardening
- Added `MASTER-PROMPT-V5.0.md` as a lean progressive-disclosure master orchestrator.
- Added `system-reality-and-production-readiness` to distinguish `REAL / MOCK / STATIC / SIMULATED / PARTIAL / UNKNOWN` features and integrations.
- Added `production-delivery` pack for prototype-to-production/release work.
- Hardened `website-delivery-pipeline` with project mode, system-reality, implementation-plan, verification, release and post-deploy phases.
- Hardened `ai-agent-coding-guardrails` with proportional planning, preserve-user-work rules, verification matrix and two-stage review.
- Refactored `security-and-privacy` around trust boundaries, data flow, current OWASP verification guidance and claim discipline.
- Refactored `web-quality-and-performance` around route-specific performance budgets and lab-vs-field evidence.
- Refactored `testing-strategy` around critical journeys, pressure widths, project browser matrix and truthful integration states.
- Refactored `code-review-and-release` around spec-vs-quality review, safe rollback/revert and post-deploy smoke; destructive history rewrite is not a default rollback.
- Added `system-reality-001` and `production-release-001` capability evals.

## Design intent
V5 deliberately avoids turning the master prompt into a larger monolith. Detailed rules live in specialist skills and are loaded only when a decision is active. This follows the repository's adaptive-routing model and reduces context dilution/conflicting instructions.

See [MASTER-PROMPT-V5.0.md](MASTER-PROMPT-V5.0.md), [V5-ARCHITECTURE.md](V5-ARCHITECTURE.md) and [SKILL-CATALOG.md](SKILL-CATALOG.md).
