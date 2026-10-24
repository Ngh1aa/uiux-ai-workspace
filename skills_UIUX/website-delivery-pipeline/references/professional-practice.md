# Professional website delivery: operating guide

This guide turns the existing pipeline into work an agent and reviewer can inspect. It is a practice framework, not a claim that the agent has ten years of experience. Domain judgment, research access and actual rendered quality still need evidence.

## Start with the current project

Read `START-HERE.md` and `TASTE.md`, then follow the chosen flow stage by stage. The flow owns stage order. Do not create a second plan from this guide.

- **Existing product:** inspect source AND rendered routes/states, identify reusable tokens/components, preserve content and behavior explicitly, and record current uncommitted work before editing.
- **New website:** confirm it is actually new; a `build` task can target an existing site. Inventory brand, content, audience, business constraints and available assets. Mark missing inputs as assumptions or UNKNOWN. No fictional legacy audit.
- **Small change:** use the smaller resolved Flow and existing artifacts. Do not demand a complete research report for a button repair.
- **High-risk product:** route domain, privacy, security, accessibility and real-user validation skills to the affected decisions. A marketing prototype does not validate a clinical, financial or operational workflow.

## The four executable stages

The professional website Flow currently executes `research → design → implementation → qa`. Release and post-release learning are scoped handoffs to existing release/monitoring owners, not secretly automatic fifth/sixth stages. Replanning returns to the owner of a failed decision.

| Stage | Decision to resolve | Minimum useful evidence | When to return upstream |
|---|---|---|---|
| Research | What problem and audience justify this site? | Brief/JTBD; buyer-user-operator-approver map; baseline or confirmed absence; evidence ledger; journey/IA; reference-transfer decisions | Invalid audience, unsupported business claim, missing project truth |
| Design | Which composition and interaction serves each page job? | Distinct directions with real content; responsive wireframes; tokens/components/states; prototype tasks; canonical Design Contract | Generic direction, weak information hierarchy, content/IA contradictions |
| Implementation | How does the approved design become truthful working behavior? | Current compiled spec; reuse/change plan; responsive code; real/mock inventory; build and regression results | Stale contract/spec, incompatible data reality, violated preservation boundary |
| QA | What actually works, and what remains uncertain? | Rendered matrix; visual critique; keyboard/a11y; critical tasks; current proof hashes; handoff and unresolved-risk register | Broken interaction/layout, invisible focus, misleading content, invalid/stale proof |

`data/lifecycle.json` is the canonical deliverable catalog. Both external manifests and managed provider requests include only the active stage card. Resource links are a menu for unresolved questions, not an instruction to load every skill.

## Research that changes decisions

Start with a decision, not a request to “research the industry.” For example: “Can a plant manager determine whether this supplier handles an urgent control-panel retrofit?” Identify what evidence would change page priority, proof format, CTA or delivery scope.

Use the existing research-evidence pipeline and its templates. A traceable row connects:

`source → observation → interpretation → decision → route/state/component → verification`

Record disconfirming evidence and sampling/source limits. Separate desk evidence, expert walkthroughs, synthetic fixtures and direct users. If recruitment is unavailable, produce a usable hypothesis-led design and a research plan; keep human validation UNKNOWN. Never invent interviews, review quotes, certifications, client counts, savings, ROI or conversion improvements.

An evidence-rich brief can be one short document. An evidence-poor brief is not improved by ten redundant documents. One existing file can satisfy several deliverables when the links point to specific decisions.

## Design judgment rather than a generic template

Use references to understand a mechanism: how hierarchy shortens evaluation, how proof answers objections, how imagery explains a service, or how mobile changes the decision sequence. Record ADOPT/ADAPT/REJECT and why the project differs. Do not transfer a complete page or proprietary brand assets.

Compare materially different compositions with the same realistic content. A palette change is not a second direction. Define the expected benefit and likely downside before comparing captures. Use the existing counterbalanced direction-comparison protocol; agent observations cannot become human preference evidence.

For each page role, define its entry question, proof objects, section sequence, CTA and recovery path. Reuse tokens and components while allowing different page compositions. Specify empty/error/loading/success and long-content cases. Design mobile transformation, keyboard behavior and reduced motion before implementation, not as a final shrink-to-fit exercise.

Visual review must inspect the actual output for hierarchy, typography, spacing, density, alignment, crop, meaningful differentiation and content quality. The integrity checker cannot decide whether a design looks professional.

## Coverage record: honest, optional operator assistance

Run from the repository root; Python needs the normal Factory environment. These commands only print results:

```text
python -B skills_UIUX/website-delivery-pipeline/scripts/check-delivery.py --template --stage research --goal "Redesign industrial B2B site"
python -B skills_UIUX/website-delivery-pipeline/scripts/check-delivery.py --root <target-root> --report docs/uiux/research-delivery.json
```

Save a template only in an authorized work area. A read-only research runner does not gain permission to write target files. An external agent/operator may keep its record outside the target until a permitted documentation step exists.

Each item starts `PENDING`. After doing the work, link UTF-8 artifact files relative to the chosen project root with their **raw-byte SHA-256** and set `RECORDED`. Do not hash a normalized string; line endings affect file bytes. Reuse the real evidence ledger, plan or report instead of copying it. Binary screenshots remain referenced through the canonical rendered-QA/design contracts.

| Checker output | Meaning | Exit code |
|---|---|---|
| BLOCKED | Missing/duplicate/unknown items, pending work, empty/stale/out-of-root files, changed context/catalog | 1 |
| NEEDS_REVIEW | An item is DEFERRED or NA_JUSTIFIED with a reason; reviewer must assess it | 2 |
| RECORDED_CURRENT | Required records exist and hashes match | 0 |

This is **not a completion gate**. It checks coverage/freshness of records, not their truth or semantic adequacy. A self-authored context hash is not authentication; compare it to the current task. Recomputing hashes does not approve changed decisions. Existing runtime gates, permissions and human approval still apply. `human_validation` and `aesthetic_quality` remain UNKNOWN in this checker, even if an artifact claims otherwise.

## What is automatic and what needs an agent/person

| Capability | Actual boundary |
|---|---|
| Flow/stage selection and active-stage packet | Code resolves/routs the existing Flow; cards do not grant authority |
| Design artifact/capture freshness | Shared checker reruns current contract and nested dependencies |
| Manual approval | Bound to current stage/revision/evidence; auto policy remains a separate existing policy |
| Rendered focus smoke | Browser checks computed state after keyboard input; static CSS flags are source lint only |
| Lifecycle record coverage | Explicit read-only CLI, not an automatic stage-completion decision |
| Research, IA, content, direction, implementation | Agent/designer performs and records the work; tools do not produce credible research on their own |
| Human validation | Actual sessions/observations needed; not fabricated by an agent |
| Release and impact | Explicit release authority, environment checks and subsequent measurement needed |

Rendered focus smoke accepts visible outlines and changed visible shadows; ambiguous border/background/caret indicators, shadow DOM/iframes and oversized control sets require dedicated review. It does not establish contrast, complete Tab order, modal traps, closed shadow roots or every dynamic state. A `NEEDS_REVIEW` result does not satisfy the automatic keyboard-focus gate. Correct the implementation or extend the shared detector with a real rendered regression and review; never relabel a report PASS by hand.

### Continuing an older run

Old design receipts without a bound project/artifact/dependency hash must be regenerated with the canonical checker against current files. In manual mode, an old list of approved gate IDs alone is insufficient: review the current evidence and approve again. Replanning or replacing evidence invalidates the previous approval. Existing default auto-approval policy is unchanged; these bindings do not turn auto mode into human approval. Browser QA for a Flow with `keyboard-focus` must be rerun through the current collector to produce its rendered focus report. Do not edit checkpoint fields or copy hashes merely to make an old run pass.

## Handoff, release and learning

Deliver run/preview instructions, version and artifact inventory, component/token/content ownership, actual test results, known issues with severity/owner and an explicit acceptance decision. Keep machine checks, agent inspection and human approval separate.

For a prototype, record release/integration work as future scope with an owner and verification plan. For production, verify real form/API/auth/CMS behavior, permissions/privacy/security, relevant SEO, field/lab performance boundaries, monitoring, rollback and release approval through existing owners. A prototype should not masquerade as a deployed service; a prototype also should not require an already-completed production experiment.

After release, review actual metrics against a known baseline and compare with qualitative evidence. Define the event/data source, consent, analysis owner and decision rule first. Avoid causal claims from a before/after screenshot or an unmeasured launch.

## Source map and maintenance

The catalog links primary sources reviewed on 2026-10-13: Design Council (diverge/converge), GOV.UK (research planning/service lifecycle), W3C (accessibility evaluation/focus), web.dev (user-experience metrics), Google Search Essentials, and OWASP ASVS. These support practice principles; they are not a project-specific legal/security/accessibility certification.

Change this catalog and the shared packet adapter together. Re-run `tests/test_website_delivery.py`, routing/provider tests and the repository validators. Re-review references when standards, tooling or project risks change. Keep specialized knowledge in existing skill owners rather than duplicating it here.
