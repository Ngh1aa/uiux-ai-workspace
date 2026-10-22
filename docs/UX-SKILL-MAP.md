# UX skill map: one owner per decision

The library has 117 skills. Many UX skills look alike by name. This map says which skill
**owns** each UX decision, so humans and agents load one skill instead of five.
It does not delete or merge skills; it routes between them.

## By phase

| Phase | Decision | Owner | Load only when |
|---|---|---|---|
| U0 Frame | Is this the right problem, what outcome, what scope | `product-discovery` | New product/feature, or ask is vague |
| U0 Frame | Stakeholder asked for a solution ("add a chatbot") | `product-decision-and-stakeholder-framing` | The ask names a solution, not a need |
| U0 Frame | What to build first, what to cut | `product-strategy-and-prioritization` | Problem is understood; options compete |
| U1 Understand | Who comes, why, top tasks | `audience-intent-and-top-tasks` | Always for new structure |
| U1 Understand | How they arrive (search, QR, Zalo link) and what they expect | `entry-context-and-visit-intent` | Landing pages, campaigns, deep links |
| U1 Understand | Personas, journey map, pain points | `ux-research-and-journey` | Journey spans many touchpoints or time |
| U1 Understand | Offline service → digital journey | `service-experience-to-digital-journey` | Schools, clinics, hotels, showrooms |
| U2 to U6 Structure | Flows, screen/state inventory, navigation model, wireframe spec, walkthrough, UX Readiness | **`ux-structure-and-flow-design`** | Before any visual direction |
| U4 Structure | Large IA, taxonomy, labels, URL migration | `information-architecture` | More than ~20 destinations or contested labels |
| U5 Structure | Page section order on content pages | `journey-driven-content-and-layout` | Marketing/content pages (not app screens) |
| U5 Detail | Common interaction patterns (tabs, filters, dialogs) | `interaction-patterns-and-form-ux` | Choosing a standard pattern |
| U5 Detail | Multi-step, conditional, high-stakes forms | `complex-forms-and-wizards` | Branching, review, save/resume |
| U5 Detail | Loading, empty, error, recovery | `state-feedback-and-error-recovery` | Any async or failure-prone screen |
| U5 Detail | Mobile-native navigation, interruptions, permissions | `mobile-navigation-and-state-ux` | iOS/Android app work |
| U5 Detail | Words on screens | `ux-writing-and-microcopy` | Labels, errors, empty states |
| U5 Detail | Question wording in forms | `content-design-and-question-design` | Forms where the question itself confuses |
| Validate | Expert review against heuristics | `ux-laws-and-heuristics` | Wireframe or live UI review |
| Validate | Which prototype fidelity answers the question | `prototype-strategy-and-concept-testing` | Before building a prototype |
| Validate | Run a usability test | `moderated-usability-testing` | Real participants available |
| Validate | Plan and recruit research | `user-research-planning-and-recruitment` | Before any study |
| Validate | Card sort / tree test | `card-sorting-and-tree-testing` | IA labels or grouping uncertain |
| Decide | Critique and rationale | `design-critique-and-rationale` | Reviews, choosing between options |
| Measure | Usability metrics before/after | `ux-benchmarking-and-metrics` | Comparing versions on the same tasks |
| Measure | Product analytics, events, A/B plan | `analytics-and-experimentation` | Production tracking or pre-run test design |

## Overlaps resolved

| Looks like | Use this | When | Use the other | When |
|---|---|---|---|---|
| Forms | `interaction-patterns-and-form-ux` | Standard short form, picking a pattern | `complex-forms-and-wizards` | Multi-step, branching, review, save/resume |
| Testing | `moderated-usability-testing` | Running sessions | `real-user-validation` | Coordinating evidence across problem → live stages (orchestrates the others) |
| Prototype | `prototype-strategy-and-concept-testing` | Deciding fidelity and what to test | `moderated-usability-testing` | Actually testing it |
| Metrics | `ux-benchmarking-and-metrics` | Task success, time, errors on fixed tasks | `outcome-metrics-and-instrumentation` / `analytics-and-experimentation` | Business outcomes and event tracking in production |
| Research ops | `research-synthesis-and-insight-management` | Turning notes into insights | `research-evidence-pipeline` | Setting up the whole pipeline (screener → ledger → decision log) |
| Provenance | `evidence-provenance-and-research-ops` | Making a claim traceable across projects | `research-synthesis-and-insight-management` | Within one research round |
| Journey | `ux-research-and-journey` | Understanding the journey | `ux-structure-and-flow-design` | Turning it into flows and screens |
| Layout order | `journey-driven-content-and-layout` | Content/marketing page sections | `ux-structure-and-flow-design` | App screens and task flows |
| States | `state-feedback-and-error-recovery` | Any platform | `mobile-navigation-and-state-ux` | Native-only concerns (back, permissions, interruptions) |
| Brand | `brand-recognition-validation` | Research protocol: do people recognise it | `brand-recognition-and-consistency-qa` | QA: do all screens look like one brand |

## Minimum sets

| Task size | Load |
|---|---|
| Copy or label fix | `ux-writing-and-microcopy` |
| One screen change | `ux-structure-and-flow-design` (combined single file) + one detail owner |
| New feature (2 to 5 screens) | `audience-intent-and-top-tasks` + `ux-structure-and-flow-design` + detail owners as needed |
| New product / full redesign | Pack `ux-foundation`, then visual skills after UX Readiness |
