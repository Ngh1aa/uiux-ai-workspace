# Skill Catalog — V5

## Core pipeline

| Skill | Vai trò |
|---|---|
| `website-delivery-pipeline` | Orchestrator lifecycle + adaptive pack/specialist routing |
| `project-context` | Project config, constraints and source-of-truth |
| `product-discovery` | Problem, audience, JTBD, constraints, KPI, scope |
| `product-decision-and-stakeholder-framing` | Translate stakeholder/solution asks into underlying problems, stress-test evidence/impact, and clarify the authorized product call |
| `product-strategy-and-prioritization` | Reality-grounded positioning, evidence-weighted prioritization and appetite/scope decisions after discovery |
| `website-audit-and-redesign` | Audit live/legacy site before redesign |
| `brand-guidelines` | Brand foundation, color, type, voice |
| `ux-research-and-journey` | Journey, task analysis and flows |
| `information-architecture` | Inventory, taxonomy, labels, hierarchy, navigation/findability, page roles and URL migration |
| `ux-laws-and-heuristics` | Heuristic review |
| `design-reference-research-and-benchmark` | Search, score and synthesize real/curated design references by domain, audience, business goal and implementation fit |
| `reference-extraction-and-design-audit` | Extract source-attributed visual-system evidence from selected references or the current codebase without making it canonical |
| `design-intelligence-retrieval` | Retrieve a small verified subset from the pinned UI UX Pro Max design-intelligence corpus, then synthesize ADOPT/ADAPT/REJECT against project truth |
| `real-world-artifact-and-domain-metaphor-design` | Translate real domain objects/documents/spaces/rituals into useful digital structure/signatures without literal skeuomorphism |
| `visual-design-direction` | Layout, hierarchy and visual grammar |
| `visual-taste-calibration` | Anti-template / subject-matter-fit calibration after a visual direction exists |
| `ui-improvement` | Existing UI remediation orchestrator: diagnose → preserve → route specialists → implement → verify |
| `conversion-and-content` | Marketing-page argument, message match, value proposition, proof, objections, CTA hierarchy and CRO hypotheses |
| `content-design-and-question-design` | Interface content structure and question design for forms/transactional journeys |
| `ux-writing-and-microcopy` | State-level UI copy, labels, CTA, errors, empty/loading/success/recovery, terminology and localization-safe microcopy |
| `design-system-and-components` | Tokens, components, variants, states |
| `interaction-patterns-and-form-ux` | Common forms/search/filter/dialog patterns |
| `motion-and-microinteractions` | Purposeful motion |
| `asset-media-and-art-direction` | Image/video/icon direction |
| `system-reality-and-production-readiness` | Distinguish real/mock/static/simulated/partial behavior, data contracts and production gaps |
| `responsive-and-device-strategy` | Responsive/device behavior |
| `accessibility` | WCAG, semantic, keyboard/focus baseline |
| `localization-and-i18n` | Multilingual UX architecture |
| `frontend-architecture-and-refactoring` | Structure, reuse, safe refactor |
| `frontend-implementation` | Semantic implementation |
| `component-driven-development` | Isolated component states/stories/tests |
| `reference-analysis-and-design-to-code` | Reference/Figma/screenshot to system/code |
| `web-ui-code-review` | Code-level web UI review with conditional React/Next performance specialization and local-owner routing |
| `ai-agent-coding-guardrails` | Context-aware, dependency-aware safe AI coding/change discipline with vertical slices/checkpoints and evidence verification |
| `search-demand-and-content-briefing` | Current search/query demand, question/intent maps, evidence-backed page/content briefs and search-performance signals |
| `seo-strategy` | Technical/on-page SEO implementation: indexability, canonicals, metadata, schema, linking, redirects, sitemap/robots |
| `web-quality-and-performance` | CWV, lab/field evidence and project performance budgets |
| `security-and-privacy` | Risk-based security/privacy baseline and verification |
| `analytics-and-experimentation` | Outcome/counter-metrics, event/funnel instrumentation and pre-run experiment design |
| `experimentation-interpretation` | Post-result experiment interpretation: uncertainty/effect size, multiplicity, sequential methods, segments, CUPED/ratio/network concerns and ship/kill/iterate decisions |
| `testing-strategy` | Risk-driven functional/state/browser/visual/accessibility/performance verification |
| `ui-craft-and-visual-qa` | Visual craft and responsive QA |
| `code-review-and-release` | Two-stage review, release/rollback and post-deploy gate |
| `production-monitoring-and-maintenance` | Post-release technical health |
| `content-governance-and-cms` | Content schema/ownership/CMS |
| `skill-authoring-and-governance` | Maintain this library |

## Reference intelligence

`design-reference-research-and-benchmark` sits between UX/content decisions and `visual-design-direction` for substantial new design/redesign work. It uses a mixed source model: real industry sites for product/UX truth, curated/award sources for visual craft, case-study/shot platforms for system/component ideas and mood platforms for art direction. Awards/gallery popularity are not evidence of usability/conversion success.

When a selected reference or the current project needs deeper system-level evidence, route `reference-extraction-and-design-audit`. Extraction documents color/type/spacing/radius/elevation/layout/component/responsive/theme evidence with source + certainty; it never licenses cloning or makes frequent observed values canonical.

## External design intelligence

`design-intelligence-retrieval` exposes the complete pinned UI UX Pro Max corpus without making it global prompt context. Route only for an active knowledge gap; use the smallest mode (`--design-system`, one explicit `--domain`, or detected `--stack`), verify the match, retry once when appropriate, then synthesize `ADOPT / ADAPT / REJECT` against project truth. Upstream-generated MASTER/page files remain candidate artifacts.

## External UI/UX specialist adapters

Source locks live in `vendor/external-uiux/SOURCE-LOCKS.md`.

- `visual-taste-calibration` → coherent direction still feels generic/interchangeable/AI-templated.
- `web-ui-code-review` → source-level UI/pre-merge review; React/Next reference only after stack/version detection.
- `reference-extraction-and-design-audit` → selected reference/current-system extraction.
- `ux-writing-and-microcopy` → string/state copy affects comprehension/action/trust/recovery/localization.

## Cross-functional intelligence for UI/UX

Pinned source provenance lives in `vendor/cross-functional-intelligence/SOURCE-LOCKS.md`. These skills complement UI/UX decision quality; they are not another lifecycle orchestrator.

### Product decision

`product-decision-and-stakeholder-framing` is informed by Mind the Product's `make-the-call`. Route when an ask is already phrased as a solution (“make hero bigger”, “add chatbot”, “build integration”) and the underlying problem/evidence/priority is unclear. It translates asks to solution-independent problems, stress-tests evidence/blind spots/impact and keeps the final business call with the authorized owner.

### Product strategy / prioritization

`product-strategy-and-prioritization` is informed by ProductSkills positioning/prioritization/scope patterns. Route only after the problem/outcome is understood enough to rank or scope. Quantitative models are decision aids: unknown Reach/Impact/Effort stays UNKNOWN. Mandatory accessibility/security/legal/project-truth requirements cannot lose to a score.

### Growth / CRO / marketing copy

`conversion-and-content` incorporates targeted CRO and marketing-copy patterns from the pinned `ai-vita/skills` snapshot. Route for page argument, traffic/message match, proof, objections and CTA hierarchy. Best practices remain hypotheses until project research/analytics/experiments support a conversion claim.

### Experimentation

`analytics-and-experimentation` owns outcome metrics, counter-metrics, tracking/funnels and pre-run experiment design. `experimentation-interpretation` owns completed results and is informed by Rampstack's statistical interpretation guidance. Do not load both merely because “A/B test” is mentioned; choose based on lifecycle stage.

### Search demand / SEO

`search-demand-and-content-briefing` owns live/current demand evidence, natural-language question maps and content briefs. `seo-strategy` owns technical/on-page implementation. If no actual current source returns a metric, use `NO_DATA`/`UNKNOWN` instead of remembered or fabricated volume.

### Engineering complement

`ai-agent-coding-guardrails` incorporates context hierarchy/trust, dependency-aware planning, vertical slices and checkpoints informed by Addy Osmani's agent-skills, while retaining `skills_UIUX` implementation/release ownership.

## Real-world artifact intelligence

`real-world-artifact-and-domain-metaphor-design` studies physical products, printed/operational documents, spatial systems, tools and offline rituals in the domain and maps them through form/structural/information/behavioral/ritual transfer layers with an L0–L4 fidelity ladder. Default to the lowest useful fidelity.

## Production reality & delivery

`system-reality-and-production-readiness` exists because rendered UI can imply behavior that is not actually integrated. Use it for forms/search/auth/checkout/CMS/API/analytics and prototype-to-production work. `production-delivery` groups reality checks with coding guardrails, security/privacy, performance, verification, release/rollback and monitoring.

## V5 measurement-reliability specialists
- `evidence-provenance-and-research-ops`
- `journey-outcome-and-service-health`
- `brand-recognition-validation`
- `accessibility-conformance-evaluation`
- `visual-regression-and-design-drift`
- `adaptive-skill-routing-and-context-budget`
- `agent-evaluation-and-reliability`
- `continuous-learning-and-improvement`

## V4 experience-strategy specialists
- `audience-intent-and-top-tasks`
- `entry-context-and-visit-intent`
- `journey-driven-content-and-layout`
- `brand-distinctiveness-and-visual-signature`
- `service-experience-to-digital-journey`
- `experience-principles-and-signature-moments`
- `omnichannel-experience-continuity`
- `brand-recognition-and-consistency-qa`

## V3 specialist skills

### Research & validation
- `user-research-planning-and-recruitment`
- `moderated-usability-testing`
- `research-synthesis-and-insight-management`
- `ux-benchmarking-and-metrics`
- `card-sorting-and-tree-testing`
- `service-blueprinting`
- `prototype-strategy-and-concept-testing`

### Advanced interaction & enterprise
- `site-search-and-findability`
- `complex-forms-and-wizards`
- `state-feedback-and-error-recovery`
- `complex-workflow-and-progress-ux`
- `data-tables-and-enterprise-ux`
- `data-visualization-and-dashboard-ux`
- `authentication-account-and-recovery-ux`
- `personalization-and-preference-ux`

### Inclusive, content & trust
- `content-design-and-question-design`
- `ux-writing-and-microcopy`
- `inclusive-design-and-cognitive-accessibility`
- `assistive-technology-testing`
- `trust-credibility-and-transparency`
- `ethical-ux-and-deceptive-patterns`

### DesignOps & AI
- `design-critique-and-rationale`
- `design-system-governance-and-adoption`
- `human-ai-interaction-design`

## Capability packs
- `measurement-reliability` (V5)
- `production-delivery` (V5 production hardening)
- `product-growth-intelligence` (cross-functional product/growth/search/experimentation)
- `experience-strategy` (V4)
- `research-validation`
- `advanced-interaction`
- `inclusive-trust`
- `designops-governance`
- `human-ai`

## Domain playbooks
`corporate-website`, `education-website`, `ecommerce-website`, `real-estate-and-building-website`, `hospitality-website`, `portfolio-website`, `news-and-media-website`, `saas-website`, `landing-page`, `government-and-public-sector-website`, `nonprofit-website`, `startup-and-incubator-website`.

## Selection rules

Keep base profiles small and route the smallest graph justified by the decision:

- Local UI remediation → `ui-improvement` + relevant specialists only.
- Substantial redesign → reference benchmark; deep extraction/design DB only for actual gaps.
- Ambiguous stakeholder solution ask → `product-decision-and-stakeholder-framing` before treating the request as a design requirement.
- Rank opportunities / define positioning / cut scope → `product-strategy-and-prioritization` after discovery evidence exists.
- Marketing-page conversion/message problem → `conversion-and-content`; add analytics/experiment skill only if measurement/testing is active.
- Pre-run experiment → `analytics-and-experimentation`; completed result → `experimentation-interpretation`.
- Current search demand/content brief → `search-demand-and-content-briefing`; technical search implementation → `seo-strategy`.
- Code task needing multi-file plan/context/dependency discipline → `ai-agent-coding-guardrails`; tiny fixes remain lightweight.
- Production candidate/release → `production-delivery` when integrations/security/performance/browser/rollback/production truth are material.

Do not activate product/growth/search/engineering specialists merely because they are installed. Cross-functional knowledge should improve a concrete UI/UX decision, not expand every task into product management, marketing and engineering at once.
