---
name: website-delivery-pipeline
description: Orchestrates the full lifecycle of building or redesigning a professional website. Use at project start, for multi-phase work, or when deciding which UI/UX skills, capability packs, domain playbooks, artifacts, evidence and quality/reliability gates are needed.
---

# Website Delivery Pipeline — V5 Orchestrator

## Core principle
`business/user goal → project truth → evidence → audience/entry intent → whole journey → success definition → validated UX/IA → reference intelligence → optional design-intelligence retrieval → distinctive experience/system → system reality → planned implementation → verification → release → measured outcomes → continuous learning`

Route the **smallest useful skill graph**. Do not load the whole library.

## Step 0 — Read project context
If `.uiux-profile.json` exists, read it plus every `source_of_truth` file before applying generic rules. Project evidence overrides generic defaults unless a higher-priority user instruction changes direction.

## Step 1 — Classify scope, risk and project mode
Use `adaptive-skill-routing-and-context-budget` principles. Classify both scope/risk and mode: `strategy`, `visual-prototype`, `interactive-prototype`, `production-candidate` or `production`.

A local component fix and a whole-service redesign should not activate the same context. A prototype and a production release should not be held to the same integration/release gate.

For an **existing implemented UI** where the user asks to fix, improve, polish, modernize or make the interface more professional without necessarily redesigning the whole product, route through `ui-improvement`.

If a page/site redesign has weak, generic or undefined visual direction, or the user explicitly asks to learn from strong websites/references, route through `design-reference-research-and-benchmark` before locking `visual-design-direction`.

If broader product/style/color/type/icon/motion/chart/UX/stack knowledge can materially improve an active UI/UX decision, route `design-intelligence-retrieval` after project/domain/audience/page-role context is known and before the affected visual/design-system decision is locked. Do not activate it merely because the vendor database is installed.

If the work contains forms, search, auth, checkout, CMS/API data, analytics or other behavior that can look real while being mock/simulated, activate `system-reality-and-production-readiness` before calling it working or production-ready.

### Redesign hard-routing override

For a **whole-site redesign/rebuild**, especially when the user supplies a legacy site, brand source and asks to research comparable websites, do **not** let `ui-improvement` become the primary path. The minimum redesign graph is:

`project-context → website-audit-and-redesign → audience/user-journey/domain playbook → design-reference-research-and-benchmark → [design-intelligence-retrieval when useful] → visual-design-direction → design-system/components → frontend implementation → responsive/accessibility → rendered visual QA`

Add domain-specific and reality/security/performance skills only when justified.

Before any substantial code edit, the redesign must have a **Design Contract** (file or equivalent working artifact) containing at minimum:

- owner/business goal and what the owner must communicate;
- primary audiences, entry intents and what each audience must find quickly;
- journey/decision sequence connecting user intent to business conversion;
- preserve/change list from the existing site;
- brand evidence and color-role map, not only a palette;
- reference roles and extracted principles;
- layout grammar + typography + imagery/media direction;
- page-role composition matrix for primary templates;
- top-of-page/hero strategy per page role;
- mobile transformation rules when mobile/tablet are in declared scope;
- explicit `do / do not` rules and visual signatures.

**No-code gate:** if these items are still generic (for example “modern, premium, clean”, one universal hero, or one layout copied across unrelated page roles), stop and resolve the design direction before implementation.

For sites with 5+ materially different primary page roles, require at least **3 distinct top-of-page composition families** unless a documented brand/product rationale justifies stronger repetition. Consistency may reuse tokens, navigation and signatures; it must not reduce every page to the same shell with different copy/images.

## Step 2 — Choose base profile + conditional packs
- Substantial content/layout redesign, experiential service, brand differentiation or online/offline journey → `experience-strategy`.
- High product/behavior uncertainty, redesign validation or IA risk → `research-validation`.
- Production outcome proof, formal conformance, repeated AI workflows, visual/system regression risk → `measurement-reliability`.
- Production-candidate/release work with integrations, security, cross-browser verification or rollback concerns → `production-delivery`.
- Complex search/forms/state/workflow/data/account UI → `advanced-interaction`.
- Broad audience, high trust, accessibility or high-consequence decisions → `inclusive-trust`.
- Mature design system or repeated cross-project UI work → `designops-governance`.
- End-user AI features → `human-ai`.

## Pipeline
| Phase | Required / conditional capabilities | Gate |
|---|---|---|
| 0 Intake | discovery + project context | problem, owner goal, scope, mode |
| 0A Evidence | optional provenance register | claims marked evidence/hypothesis/assumption |
| 0B Audience | audience + entry intent when material | who, why now, top tasks |
| 0C Success | service outcome/metric definition when material | meaningful success + data source known |
| 0D Existing | website audit | preserve/change rationale |
| 1 Research | optional research-validation | evidence gaps tested appropriately |
| 2 Whole journey | optional service/omnichannel mapping | real journey/channels/key moments known |
| 3 UX/IA | journey + IA + optional card/tree testing | flows/findability validated to risk |
| 4 Content/experience | journey-driven layout + experience principles | sections advance user decisions |
| 4A Reference benchmark | conditional `design-reference-research-and-benchmark` | mixed source pool, finalists by role, no blind copying |
| 4B Design intelligence | conditional `design-intelligence-retrieval` | narrow verified retrieval, ADOPT/ADAPT/REJECT synthesis, no database-as-truth |
| 5 Brand/visual | brand + visual + optional digital signature | implementable, recognizable grammar + page-role matrix |
| 5A Design contract | required for substantial redesign | owner/user goals, journey, brand, references, adopted intelligence, compositions and do/don't are concrete before code |
| 6 System | design system + interaction + optional designops | reusable components/states without template monotony |
| 6A System reality | conditional reality/data/API/CMS audit | real/mock/static/simulated/partial/unknown explicit |
| 7 Plan | architecture + change plan + guardrails | owners, dependencies, acceptance and verification known |
| 8 Code | frontend implementation | maintainable working implementation that follows the design contract |
| 9 Inclusive | responsive + accessibility + optional cognitive/AT | usable critical journeys |
| 10 Advanced behavior | optional search/forms/state/data/auth/AI | no undefined high-risk states |
| 11 Quality | visual QA + brand + performance + SEO + security/trust | evidence-backed findings |
| 12 Verification | tests + browser/device + verification matrix | every material change has pass condition/result |
| 12A Rendered design review | required for substantial visual work | actual rendered pixels inspected across representative routes/viewports |
| 13 Conformance/regression | optional accessibility/visual drift/reliability gates | scope/sample/baselines explicit |
| 14 Release | code review + release + rollback | known risks, rollback and post-deploy smoke defined |
| 15 Production | monitoring + service-health metrics + research | real outcome observed |
| 16 Learning | continuous learning | signal becomes research/fix/test/eval |

## Phase-aware requirement and gate accounting

Multi-phase projects MUST distinguish a real blocker from work that is valid but not yet due. Do not make early phases impossible to pass by forcing future QA/release requirements into the current exit gate.

For a Requirement Coverage Ledger, use:

```text
DONE_VERIFIED
N/A_JUSTIFIED
PENDING_FUTURE_PHASE
BLOCKED
```

Each material/applicable requirement should also have an `OWNER_PHASE` (or equivalent lifecycle owner) and verification plan.

Rules:

- `DONE_VERIFIED`: required evidence for the owning/current phase exists and the pass condition is met.
- `N/A_JUSTIFIED`: not applicable to the declared scope/mode, with rationale. Example: mobile/tablet for an explicitly `desktop_only` project; production deployment when authorization is `no_release`.
- `PENDING_FUTURE_PHASE`: requirement is applicable, but its authoritative verification belongs to a later phase. Record owner phase + planned method. It is **not** a fake PASS and must be consumed when its owner phase arrives.
- `BLOCKED`: a due-now exit criterion cannot be satisfied with available authority/evidence, or a real defect/conflict prevents safe progress.

Mapping skill results must be phase-aware:

```text
PASS -> DONE_VERIFIED
N/A + rationale -> N/A_JUSTIFIED
FAIL -> BLOCKED when the requirement is due now
PARTIAL / UNVERIFIED -> BLOCKED only when the current phase requires that verification to exit
PARTIAL / UNVERIFIED for a later owner phase -> PENDING_FUTURE_PHASE
UNKNOWN fact -> keep UNKNOWN; block only if that unknown prevents a current-phase material decision/claim
```

A phase may be `PASSED` when:

- every requirement **due in that phase** is accounted for;
- current-phase `BLOCKED = 0`;
- current-phase `UNACCOUNTED = 0`;
- phase exit criteria have evidence;
- every `PENDING_FUTURE_PHASE` item has a named future owner + verification method.

Do not require future release smoke, future regression evidence or future production integration evidence to be complete during research/design. Conversely, once the owner phase is reached, a pending item cannot remain pending merely to manufacture a PASS.

For durable handoff across conversations/agents, persist phase status in a project artifact such as `docs/uiux/Phase-State.md` containing at least phase result, skill/version SHA, project commit when relevant, blocker counts and pending-owner counts. Downstream phases should prefer this artifact over relying on a literal PASS sentence remaining in chat history.

### Skill-version lock bootstrap

If a project requires `docs/uiux/Skill-Version-Lock.md` but the file does not yet exist, the first lifecycle phase may resolve the intended immutable skill ref and create the lock. Absence of the lock **before its bootstrap step** is not itself a blocker. Subsequent phases must use the locked ref unless an explicit reviewed migration changes it.

### Release authorization

`no_release` means release/deploy work is intentionally outside current authority. Do not run a release phase and then report `BLOCKED` merely because authorization was deliberately set to `no_release`; mark the release phase/scope `N/A_JUSTIFIED`. If the user explicitly requests release while authority is absent or ambiguous, then release is genuinely `BLOCKED` pending authorization.

## Design-intelligence routing rules

The pinned UI UX Pro Max corpus is a retrieval source, not another orchestrator.

1. Read project truth and determine product/domain/audience/page-or-app role first.
2. New/system-wide visual direction → `--design-system`.
3. Focused UX/design concern → one explicit `--domain`.
4. Implementation-specific concern → `--stack` only after detecting the actual stack from project source.
5. Use one dominant intent and 2–5 meaningful query terms plus a useful constraint.
6. Verify the returned match. Retry once with a narrower query/explicit mode if empty or off-topic; after that, record `no verified match` and fall back to higher-priority local/project evidence.
7. Synthesize material candidates as `ADOPT / ADAPT / REJECT` and record adaptation rationale/verification.
8. Do not persist unverified output, load the full corpus into prompt context, or activate all vendored skills by default.
9. Upstream-generated `design-system/*/MASTER.md` or page overrides are candidate artifacts; the adopted Design Contract remains canonical. Never use upstream `--force` without explicit user authorization.
10. Retrieved recommendations do not prove usability, conversion, accessibility or production readiness.

For substantial redesign, use `DESIGN-INTELLIGENCE-AUGMENTED-REDESIGN-PROMPT.md` when this layer is active. It augments real reference research and never replaces structural redesign/media/rendered QA gates.

## Reference-intelligence routing rules
- Use real production/category sites first for IA, journey, trust and conversion questions.
- Use curated galleries/award sites for visual grammar, art direction, typography, storytelling and motion—not as proof of UX success.
- Behance/Dribbble/Pinterest are secondary sources with different roles; distinguish production work from concepts/shots/mood references.
- For substantial design work, prefer a mixed pool and select 3–6 finalists with distinct jobs instead of cloning one reference.
- Score references by industry, audience, business, brand, UX, layout and feasibility fit; aesthetics alone is insufficient.
- Hand extracted principles to `visual-design-direction`; use `reference-analysis-and-design-to-code` when a specific reference must be translated more closely into system/code.

## Production-reality routing rules
- A rendered success state is not proof that an operation succeeded.
- Label material capabilities `REAL`, `MOCK`, `STATIC`, `SIMULATED`, `PARTIAL` or `UNKNOWN` when reality is not obvious.
- Do not call a form/search/login/checkout/CMS/analytics integration complete without evidence appropriate to that claim.
- Production-candidate work should include `system-reality-and-production-readiness`, `ai-agent-coding-guardrails`, `testing-strategy`, `security-and-privacy` when applicable, `web-quality-and-performance` and `code-review-and-release`.
- Prefer project-specific performance/browser/release budgets over universal vanity thresholds.
- Rollback should default to platform rollback/previous deployment or safe revert, not destructive history rewrites.

## Implementation and verification discipline
- For multi-file/high-risk work, define independently verifiable tasks before editing.
- Preserve unrelated user changes; prefer isolated branch/worktree when tooling supports it.
- Review substantial work in two stages: spec/intent compliance first, code/experience quality second.
- Every material change should map to `expected outcome → verification method → pass condition → result`.
- Build pass is not visual proof; automated accessibility audit is not conformance; lab performance is not field outcome.
- For substantial redesign, inspect a **cross-page screenshot set/montage** before handoff so repeated hero/section templates, brand drift and hierarchy monotony are visible side-by-side.
- If the environment cannot render or inspect changed UI in a phase whose exit claim requires rendered evidence, mark that due-now visual verification `BLOCKED` or `UNVERIFIED`; do not use source/build success as a substitute and do not present the redesign as visually finished. If rendered verification belongs to a later owner phase, keep it `PENDING_FUTURE_PHASE` rather than blocking an earlier research/design phase.

## V5 evidence/reliability rules
- Trace material research/analytics claims to source, date, context and limitations.
- Define meaningful service success before claiming a redesign improved UX.
- A partial or automated-only accessibility review cannot justify a formal conformance claim.
- Visual baseline changes require intent review; repeated raw tokens/duplicate components are design drift.
- One successful agent run demonstrates capability, not reliability. Use multiple independent trials when reliability matters.
- Grade outcomes rather than brittle tool choreography unless the path itself is a requirement.
- Production failures that matter should feed future research, tests/checklists or regression evals.

## Core rules retained
- Distinguish owner goals from user goals and do not invent user research.
- Do not assume all visits start on the homepage.
- Do not map content inventory directly into blocks.
- Logo + primary color alone is not proof of distinctive digital identity.
- If the real service continues after a form/booking/application, design the handoff and recovery.
- Preserve proven content/SEO/behavior in redesigns until evidence supports change.
- Complex flows require state/error/recovery definitions.
- Money/consent/subscription/privacy flows require deceptive-pattern review.
- AI flows require capability limits, correction/control and graceful failure.

## Evaluation loop
1. `python scripts/validate-skills.py`
2. `python scripts/validate-v2.py`
3. `python scripts/validate-vendor-uiux-pro-max.py`
4. Smoke the retrieval adapter with a focused `--design-system` query.
5. `python scripts/eval-harness.py list`
6. Run representative tasks through the chosen provider adapter for multiple trials when needed.
7. Emit JSONL per [../evals/ADAPTER-CONTRACT.md](../evals/ADAPTER-CONTRACT.md).
8. `python scripts/eval-harness.py summarize --results results.jsonl --k 3`
9. Promote stable capability failures/successes into regression coverage.

## Completion rule
Never say `done`, `working`, `integrated`, `production-ready`, `fully responsive`, `accessible`, `WCAG conformant`, `validated`, `secure`, `UX improved`, `redesigned`, `visually finished` or `reliable` without evidence appropriate to that exact claim. Report verified versus unverified explicitly.
