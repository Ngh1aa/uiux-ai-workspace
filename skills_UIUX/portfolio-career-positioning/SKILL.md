---
name: portfolio-career-positioning
description: Audit and shape a design/product portfolio as a recruiter-facing product: target-role positioning, identity consistency, case-study evidence, AI-assisted workflow proof, CV/link/repository hygiene, technical claims and recruiter scan paths. Use for portfolio rebuilds, role repositioning and career-facing case-study systems.
---

# Portfolio Career Positioning

## Goal

Treat the portfolio as a product with a primary audience (recruiter/hiring manager/design/product/engineering reviewer), a decision to support (invite, interview, shortlist) and inspectable evidence — not as a gallery of screens.

## Core model

`target role → recruiter questions → evidence inventory → narrative hierarchy → case proof → technical/workflow proof → rendered QA → claim boundary`

## 1. Positioning contract

Make these explicit before broad redesign:

- primary target role/title;
- secondary adjacent roles only if they do not dilute the primary story;
- seniority/experience boundary;
- preferred product/domain signals;
- design thesis / working principle;
- strongest differentiator that can be inspected, not merely claimed.

Avoid conflicting identities such as Business Analyst naming paired with Product Designer messaging unless legacy naming is clearly explained or migrated.

## 2. Recruiter-critical inventory

Audit public surfaces together:

- homepage title/hero/about;
- flagship order;
- supporting work;
- each case-study route;
- CV/resume file and link;
- GitHub account/repository identity;
- source code claims and actual framework/dependencies;
- live prototype/deployment links;
- Figma/design links where relevant;
- contact links;
- sitemap/SEO metadata when public discovery matters;
- public scratch/internal notes or stale generated files that weaken the signal.

No recruiter-critical CTA may remain a placeholder (`#`, dead route, stale PDF, inaccessible deployment).

## 3. Case-study evidence model

A strong case should make these inspectable where applicable:

1. **Problem/context** — what decision or user/business tension existed?
2. **Evidence** — DIRECT_USER / LIVE_BEHAVIOR / PROXY / DESK_EVIDENCE / HYPOTHESIS / UNKNOWN.
3. **Product reasoning** — flows, states, IA, system model, constraints.
4. **Decision and trade-off** — what was chosen, rejected and why?
5. **Design/system response** — reusable components, behavior and visual logic.
6. **Working proof** — prototype/code/live route/screenshots.
7. **Validation** — real evidence if it exists; otherwise planned/blocker explicitly labeled.
8. **Outcome/measurement** — only verified metrics; otherwise measurement plan/UNKNOWN.

Independent concepts must remain visibly independent concepts. Do not convert polish into business impact.

## 4. AI-assisted work proof

Do not use a generic “I use AI” tools list as the primary proof.

Prefer an inspectable workflow such as:

`ground project truth → synthesize/research → explore → design/code → rendered QA → repair → human release judgment`

Show concrete artifacts when public/safe:

- agent/project contracts;
- skill routing;
- prompt/task manifest;
- branch/PR workflow;
- test/QA configuration;
- rendered QA artifacts;
- decision logs or evidence boundaries.

Separate responsibilities:

**Human-owned:** product problem, user truth, priorities, trade-offs, ethical/release decisions, final rationale.  
**AI-assisted:** repo audit, synthesis, alternative generation, implementation acceleration, debugging, repetitive QA, evidence organization.

Never imply the AI conducted real user research unless actual sessions and evidence exist.

## 5. Technical proof

Every technical claim must be substantiated by current public source or clearly scoped private evidence.

Examples:

- Claim React/Next.js only if dependency/source/build evidence exists.
- Claim accessibility QA only if tests/review evidence exists.
- Claim design-to-code if the reviewer can inspect design/source/working output.
- Do not infer a framework from deployment provider alone.

For hybrid roles, prioritize at least one project with the exact stack the target role requests rather than relabeling static prototypes.

## 6. CV and identity hygiene

- Maintain one canonical recruiter CV per active positioning unless variants are intentionally managed outside the public root.
- Filename should identify the candidate and target role clearly.
- Homepage/resume links must point to that canonical file.
- Explain or migrate legacy repo/account naming that could confuse reviewers.
- Keep README public-facing and remove internal scratch notes from the public branch unless they are intentionally part of the case evidence.

## 7. Recruiter scan path

Design for three depths:

- **5 seconds:** who are you, what do you design/build, what differentiates you?
- **60 seconds:** 2–3 flagship cases, role/scope, strongest evidence, working proof.
- **10 minutes:** detailed decisions/trade-offs/research/technical evidence and source inspection.

Flagship order should support the target role, not chronology by default.

## 8. QA contract

Before completion verify:

- hero/title/metadata agree on primary role;
- flagship and supporting project links resolve;
- canonical CV link resolves and duplicates are intentional or removed;
- live/source/Figma/contact links are not placeholders;
- case-study evidence labels do not overclaim;
- technical stack claims match source;
- desktop/mobile recruiter scan path renders without overflow/broken media;
- navigation, keyboard focus and accessibility basics work;
- public source does not expose stale internal scratch/version clutter that contradicts the system-thinking claim;
- sitemap/discovery surfaces reflect current case routes when applicable.

## Output

For substantial portfolio work, leave an inspectable set of changes rather than only recommendations: updated recruiter narrative, case routes/content, identity/CV/link cleanup, technical/AI proof, claim boundaries and QA evidence.

## Quality gate

PASS only when a reviewer can answer **who this person is, what role they fit, how they think, what they actually made, how AI changes their workflow, and which claims are verified** without relying on unsupported inference.
