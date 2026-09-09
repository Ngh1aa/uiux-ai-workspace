---
name: code-review-and-release
description: |
  Code review, release-readiness, deploy/rollback và post-deploy verification theo scope/risk.
  Dùng khi substantial change chuẩn bị merge/release hoặc user yêu cầu production readiness.
  Tách requirement/spec fidelity, project/code standards và rendered/system evidence; dùng project-specific gates và tránh destructive rollback mặc định.
---

# Code Review & Release

## Principle

`review intent → review standards → review rendered/system evidence → assess release risk → release safely → smoke production → monitor`

Release gate phải phản ánh project thật; không bắt mọi site cùng Lighthouse/browser/test thresholds.

## 1. Scope the review/release

Ghi:

```text
Fixed point / merge-base when reviewing a diff
Project mode
Target environment
Changed routes/features
Shared owners/tokens/components touched
Data/API/CMS/auth/payment dependencies
Config/env/migration requirements
SEO/URL redirects if any
Known P0/P1 risks
Rollback mechanism
```

Khi review branch/PR, resolve fixed point trước và xác nhận diff không rỗng. Bad ref/empty diff phải fail sớm thay vì để reviewer suy luận trên change-set sai.

Không release production nếu không biết target/dependency critical trong scope.

## 2. Three independent review axes

Không để một axis “bù điểm” cho axis khác. Code sạch có thể implement sai spec; đúng spec có thể vi phạm project standards; cả hai có thể pass source review nhưng rendered behavior vẫn hỏng.

### Axis A — Requirement / spec fidelity

- Change có giải quyết đúng request/problem?
- Requirement Coverage / Design Contract / source-of-truth nào sở hữu quyết định?
- Project truth/brand/business/user constraints được preserve?
- Có missing requirement, false success, scope creep/unrelated refactor?
- System reality có truthful không: REAL/MOCK/STATIC/SIMULATED/PARTIAL/UNKNOWN?
- Acceptance conditions ban đầu đã đạt?

Axis A fail → không approve chỉ vì code clean.

### Axis B — Project / code standards

Review theo affected surface và documented project conventions trước generic heuristic:

- correct owner/reuse/architecture;
- semantic HTML/state logic;
- component/token drift;
- dependency/config conventions;
- accessibility/security/privacy rules when applicable;
- data/error/recovery behavior;
- performance/SEO implementation when applicable;
- tests/verification seams;
- obvious smells such as duplication, speculative abstraction or shotgun edits only as judgment signals, never as automatic hard violations unless project standards say so.

Repo/project standards override generic style heuristics.

### Axis C — Rendered / runtime evidence

For UI or behavior changes inspect the real execution surface when due in this phase:

- required routes render;
- screenshot/visual comparison at representative declared viewports;
- no broken/poor media crop, overflow or hierarchy regression;
- relevant interaction/state path works;
- console/network/API evidence when behavior depends on runtime;
- keyboard/accessibility checks appropriate to scope;
- browser/device/performance evidence when material.

Build/CI success cannot substitute for Axis C when the claim is visual/runtime. No baseline means visual regression is `INCONCLUSIVE`/unverified, not silent PASS.

### Parallel review option

For substantial/high-risk diffs, Axis A and Axis B may be reviewed in separate contexts/sub-agents to reduce cross-contamination, then aggregated without reranking one axis over another. Axis C should consume rendered/runtime evidence rather than only the source diff.

## 3. Verification matrix

Mỗi material change:

| Change | Expected outcome | Verification | Pass condition | Result |
|---|---|---|---|---|

Possible evidence:

- build/type/lint;
- unit/integration/E2E;
- route smoke;
- network/API behavior;
- visual comparison;
- representative viewport/browser checks;
- keyboard/AT checks;
- performance/security checks;
- deployed-environment smoke.

Map results into the project Requirement Coverage Ledger: `DONE_VERIFIED`, `BLOCKED`, `N/A_JUSTIFIED`, or phase-aware `PENDING_FUTURE_PHASE` where the repository contract allows it. Do not invent a PARTIAL PASS.

## 4. Release blockers

Mặc định block release nếu applicable:

- unresolved P0;
- P1 làm hỏng primary/critical journey mà không có accepted mitigation;
- false success/data behavior;
- build/runtime failure;
- known secret exposure chưa xử lý;
- auth/access-control/security issue nghiêm trọng trong changed path;
- destructive data/schema change không có migration/rollback plan;
- critical accessibility blocker;
- redirect/SEO migration có nguy cơ mất critical URLs mà chưa map;
- không có cách rollback/recover hợp lý cho high-risk release;
- due-now Axis A/B/C evidence còn BLOCKED.

Không block prototype vì production-only requirement nếu project mode không phải production-candidate/production; thay vào đó ghi owner phase/gap.

## 5. Pre-release checklist

Theo scope, xác nhận:

### Project / code
- working tree/change set understood;
- unrelated user changes preserved;
- build/type/lint/tests relevant đã chạy hoặc ghi unverified;
- dependency/config/env changes documented;
- source-of-truth/docs updated khi material.

### Product / content
- placeholders/fake data không vô tình ship như real data;
- contact/legal/business-critical facts verified;
- error/empty/loading/success states truthful;
- analytics/consent state aligned actual implementation.

### UX / quality
- representative responsive/browser matrix;
- critical keyboard/accessibility checks;
- visual QA on affected routes;
- performance budget/regression check where material;
- no broken critical links/actions.

### Platform / SEO
- redirects/canonical/sitemap/robots changes verified when applicable;
- security headers/config reviewed in deployed environment when applicable;
- third-party services/env keys configured without exposing secrets.

## 6. Deployment record

Record:

```text
release/commit identifier
target environment
time/date if relevant
migration/config changes
known issues
verification completed
rollback target/procedure
```

Không tự deploy nếu user/project authorization không cho phép.

## 7. Rollback discipline

Prefer, theo platform:

1. platform previous-deployment rollback / immutable release rollback;
2. safe git revert of release commit(s);
3. forward fix nếu rollback gây data/schema risk và incident process chọn forward fix.

Không dùng `git reset --hard` + force-push shared/default branch làm rollback mặc định.

Nếu database/schema/data migration involved, code rollback không đủ; phải đánh giá data compatibility/recovery separately.

## 8. Post-deploy smoke

Sau release, nếu có quyền truy cập target environment, verify critical subset:

- production URL/HTTPS;
- primary navigation/journey;
- forms/search/auth/payment/integrations affected;
- console/network/server errors available;
- redirects/canonical critical paths;
- analytics event delivery when in scope;
- obvious visual/responsive regression;
- monitoring alerts/logging health.

Không gọi release done chỉ vì CI/deploy job green.

## 9. Monitoring / learning

Define what to watch:

- errors/failed requests;
- 404/redirect anomalies;
- submission/conversion breakage;
- performance/CWV trend;
- analytics instrumentation;
- support/user feedback;
- security/abuse signals when available.

Production incident/failure material phải feed về tests, regression coverage, design/system docs hoặc research. Repeated agent/tool failures should use the failure-diagnosis reference owned by `agent-evaluation-and-reliability` before blind retry.

## Output

Cho substantial release, tạo `docs/release-readiness.md` hoặc equivalent:

```md
# Release Readiness
## Scope / fixed point
## Axis A — Requirement/spec fidelity
## Axis B — Project/code standards
## Axis C — Rendered/runtime evidence
## Verification matrix
## Blockers / known risks
## Release dependencies
## Rollback plan
## Post-deploy smoke
## Monitoring
```

## Quality gate

- [ ] Axis A/B/C được report riêng và không mask lẫn nhau.
- [ ] Material changes có verification evidence.
- [ ] P0/P1 được xử lý hoặc reported/accepted rõ.
- [ ] System reality không bị phóng đại.
- [ ] Rollback không dựa mặc định vào destructive history rewrite.
- [ ] Production release có post-deploy smoke plan/result.
- [ ] Completion claim match evidence.

## Anti-patterns

- “CI green” = release success.
- Code quality PASS masking spec FAIL.
- Spec PASS masking project-standard violations.
- Source review masking visibly broken rendered UI.
- No visual baseline silently treated as regression PASS.
- Force-push rollback mặc định.
- Universal Lighthouse threshold làm release gate cho mọi project.
- Review style/naming nhưng bỏ qua broken behavior.
- Ship mock/fake data như production truth.
