# Runtime design notes

Implementation notes for runtime capabilities, kept for traceability. They explain why a
mechanism exists; they are **not** loaded during normal task routing (see `START-HERE.md`,
"Context loading rule"). Live contracts stay one level up in `skills_UIUX/runtime/`.

Moved here on 2026-10-22 because no file in the repository referenced them by path. Notes
that are still referenced (A4, A5 evaluation memory, A7, A13 cross-project, P11 to P175) stay
where they are so existing links keep working.

| Note | Topic |
|---|---|
| [A10-VISION-CREATIVE-DIRECTOR.md](A10-VISION-CREATIVE-DIRECTOR.md) | A10 — Vision Creative Director |
| [A11-AUTHENTICATED-REMOTE-CONTROL.md](A11-AUTHENTICATED-REMOTE-CONTROL.md) | A11 — Authenticated Remote Factory Control Plane |
| [A12-BENCHMARK-REGRESSION-CORPUS.md](A12-BENCHMARK-REGRESSION-CORPUS.md) | A12 — Benchmark & Regression Corpus |
| [A13-NOVA-REAL-PROJECT-DOGFOOD.md](A13-NOVA-REAL-PROJECT-DOGFOOD.md) | A13 — Nova Real-Project Dogfood |
| [A5-4-A5-5-QUALITY-LEARNING.md](A5-4-A5-5-QUALITY-LEARNING.md) | A5.4–A5.5 — Post-Render Quality Learning + Advisory Recall |
| [A5-6-STAGE-AWARE-QUALITY-RECALL.md](A5-6-STAGE-AWARE-QUALITY-RECALL.md) | A5.6 — Stage-Aware Quality Recall Routing |
| [A5-7-PROVIDER-ADVISORY-CONTEXT-FIREWALL.md](A5-7-PROVIDER-ADVISORY-CONTEXT-FIREWALL.md) | A5.7 — Provider Advisory Context Firewall |
| [A6-2-PROVIDER-BUDGET-TELEMETRY.md](A6-2-PROVIDER-BUDGET-TELEMETRY.md) | A6.2 — Provider Budget + Usage Telemetry |
| [A6-3-TRUSTED-PROVIDER-USAGE.md](A6-3-TRUSTED-PROVIDER-USAGE.md) | A6.3 — Trusted Provider Usage + Hard Output Caps |
| [A6-5-ZERO-COST-PROVIDER-GUARD.md](A6-5-ZERO-COST-PROVIDER-GUARD.md) | A6.5 — Zero-Cost Provider Guard + Free-Tier Managed Routing |
| [A8-2-JIT-PROVENANCE-OPTIONAL-ROUTING.md](A8-2-JIT-PROVENANCE-OPTIONAL-ROUTING.md) | A8.2 — JIT Provenance & Optional Skill Routing |
| [A8-3-SHARED-CONTEXT-BUDGET-PREFLIGHT.md](A8-3-SHARED-CONTEXT-BUDGET-PREFLIGHT.md) | A8.3 — Shared Provider Context Budget & Atomic JIT Activation |
| [A8-4-RESUMABLE-STAGE-CONTINUITY.md](A8-4-RESUMABLE-STAGE-CONTINUITY.md) | A8.4 — Resumable Stage Continuity & Flow-Revision Binding |
| [A8-5-SECTION-LEVEL-JIT-RETRIEVAL.md](A8-5-SECTION-LEVEL-JIT-RETRIEVAL.md) | A8.5 — Section-level JIT Skill Retrieval |
| [A8-JIT-SKILL-CONTEXT.md](A8-JIT-SKILL-CONTEXT.md) | A8 — Just-in-Time Skill Context |
| [A9-MODEL-READABLE-BROWSER-OBSERVATION.md](A9-MODEL-READABLE-BROWSER-OBSERVATION.md) | A9 — Model-readable Browser Observation |
| [P17-GITHUB-PRODUCTION-TRANSACTION.md](P17-GITHUB-PRODUCTION-TRANSACTION.md) | P1.7 — GitHub-Native Production Runner / Transaction Boundary |
