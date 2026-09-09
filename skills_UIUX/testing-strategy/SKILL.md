---
name: testing-strategy
description: |
  Xây test/verification strategy theo critical journeys, change risk và project support matrix:
  functional, state/error/recovery, responsive/browser, accessibility, visual, performance và regression.
  Dùng khi implementation cần evidence trước completion/release; không biến fixed checklist thành proof.
---

# Testing Strategy

## Principle

`critical outcome → risk → test surface → expected result → evidence → regression coverage`

Không test mọi thứ giống nhau. Ưu tiên journey/behavior có consequence cao.

## 1. Test scope

Xác định:

```text
Project mode
Changed routes/components/features
Critical user journeys
System reality (REAL/MOCK/STATIC/SIMULATED/PARTIAL/UNKNOWN)
Supported browsers/devices if known
Risk level
Existing test tooling
Release target
```

Nếu browser/device support chưa được project định nghĩa, dùng representative modern matrix như hypothesis chứ không gọi là official support.

## 2. Priority

- `P0` — critical journey/data/security/payment blocker; must pass for production release.
- `P1` — major function/UX/accessibility/responsive/visual sanity issue; normally release-blocking unless accepted mitigation.
- `P2` — craft/secondary path/regression concern.
- `P3` — optional/low-consequence preference.

## 3. Verification matrix

Material change phải map:

| Change / capability | Risk | Expected outcome | Test method | Pass condition | Evidence/result |
|---|---|---|---|---|---|

Không ghi `PASS` nếu không thực sự chạy/inspect test phù hợp.

## 4. Functional / state testing

Test happy path + relevant alternative/recovery states:

```text
default
loading/pending
success
validation error
server/network error
empty / filtered-empty
populated
partial/stale
permission/auth failure
timeout/retry
duplicate-submit/idempotency concern
cancel/undo/back navigation where relevant
```

Form success chỉ pass khi system reality cho phép biết operation thật sự thành công. Prototype simulation phải được label simulated.

### Conditional-state coverage rule

A rendered control that only exists after data/selection/auth/error state is **not tested** by opening the default/empty page.

For material UI verification:

```text
route/template
× viewport/pressure width
× data state required to expose the UI
× interaction state required to expose the defect
```

Examples:

- Cart must be seeded/populated before claiming Checkout CTA state coverage.
- Order detail must load a deterministic order before its action/status styles are covered.
- Error/recovery control must be put into the error state before visual/state verification.

Seeded/mock data may expose UI deterministically, but remains `MOCK/SIMULATED` evidence and does not prove backend success.

## 5. Responsive testing

Test representative widths **và pressure widths**, không chỉ exact breakpoints.

Default sampling khi project không định nghĩa:

- small mobile around 360–390px;
- tablet/intermediate around 768px;
- desktop around 1280px+;
- widths ngay trước/sau layout break/change nếu issue xuất hiện ở đó.

Check:

- no unintended horizontal overflow;
- reading/order/hierarchy;
- heading/button/nav wrapping;
- image/video crop;
- touch/interactive reachability;
- sticky/fixed UI;
- dialogs/menus;
- tables/filters/forms;
- density/whitespace.

Không yêu cầu mọi page phải có CTA above fold hoặc cards stack theo một pattern cố định.

## 6. Browser matrix

Theo project/audience support. Khi chưa có matrix và production scope material, ưu tiên representative engines:

- Chromium;
- WebKit/Safari;
- Firefox.

Không cần test browser không support chỉ để đủ checklist.

Tập trung feature dễ khác browser:

- sticky/fixed/viewport units;
- forms/date/select controls;
- flex/grid intrinsic sizing;
- font metrics;
- filters/backdrop;
- scroll behavior;
- media autoplay/inline playback;
- animation;
- focus/keyboard behavior.

## 7. Accessibility testing

Phân tầng evidence:

### Automated baseline
- axe/Lighthouse/HTML checks nếu tooling phù hợp.

### Manual keyboard
- focus order/visibility;
- all actions reachable;
- no trap;
- modal/menu focus management;
- error/recovery states.

### Zoom/reflow/visual
- zoom/text resize/reflow when material;
- contrast/no color-only meaning;
- reduced motion.

### Assistive technology
- screen reader/AT testing cho critical/high-risk journeys khi scope/risk justify.

Automation-only không chứng minh WCAG conformance. Formal claim route `accessibility-conformance-evaluation`.

## 8. Visual QA

Rendered UI changed → inspect rendered result.

Check:

- **elementary visual sanity first:** no important text/control only visible when selected/highlighted; no foreground≈background; no disappearing hover/focus/active/disabled labels;
- surface/foreground semantic pairing and actual computed cascade/specificity;
- hierarchy;
- grid/alignment;
- typography/wrapping;
- spacing rhythm;
- color/surface/brand roles;
- image crop/focal point;
- component states;
- page diversity vs template repetition;
- responsive pressure points;
- visual regression on shared owners.

For shared header/footer/nav/theme/button/surface changes, representative sampling is insufficient for elementary sanity. Map the shared owner to **all affected routes/templates** and run the sanity check everywhere it renders; deeper visual/aesthetic inspection may remain representative.

For production/release or user-caught CSS regressions, prefer semantic discovery over a fragile selector whitelist:

- scan all visible text-bearing elements outside variable-media contexts for catastrophic foreground/surface collapse;
- discover rendered interactive elements (`a`, `button`, form actions, role-based controls) and inspect state contrast;
- seed/populate conditional states so hidden controls actually render;
- record route × viewport × data-state × interaction-state coverage.

A green test that never rendered the broken control is a **false green**.

For human/primary-subject hero media, `object-fit: cover` is not a pass condition. Primary/focal `cover` should be unsafe by default until a verified crop contract identifies focal subject/no-cut zone, target viewports and inspected rendered evidence.

Screenshot tồn tại nhưng không được inspect ≠ evidence.

## 9. Performance testing

Dùng `web-quality-and-performance` budgets/project targets.

- lab test dưới conditions ghi rõ;
- multiple runs/stable CI khi variability material;
- field data khi available;
- resource/third-party budget when relevant.

Không hardcode “Lighthouse >= 90 all categories” như universal release truth.

## 10. Security/privacy verification

Khi changed path có form/auth/API/data/upload/payment/third party, route `security-and-privacy` và test controls phù hợp scope trong safe environment.

Test strategy không tự biến thành penetration test hoặc compliance audit.

## 11. Regression strategy

Với shared/high-impact change, xác định affected matrix:

```text
shared owner/token/component
→ all routes/templates using it for elementary sanity
→ declared viewports + pressure widths
→ material data states needed to expose conditional UI
→ semantic surface contexts
→ default/hover/focus/active/disabled states where applicable
→ representative deep visual evidence
→ automated/manual regression evidence
```

Ưu tiên deterministic tests cho behavior. Với visual sanity, computed rendered style/contrast checks có thể bổ sung screenshot evidence; không được dùng chúng thay cho human inspection khi screenshot obvious broken.

For CSS visibility regressions, project-level deterministic guards should fail on:

- catastrophic foreground/background collapse on visible text;
- interactive label contrast failure in exercised states;
- shared owner failure on any affected route/template;
- primary/focal `cover` media without an explicit verified crop contract;
- missing conditional data-state coverage when that state is required to render the changed control.

Nếu user/reviewer bắt được lỗi obvious mà test plan bỏ lọt, promote failure đó thành regression coverage trước khi đóng remediation khi feasible, và ghi rõ **why the previous run was falsely green**.

## 12. Evidence record

Cho test đã chạy, ghi:

```text
method
environment/browser/viewport when material
data state / seeded state when material
interaction state when material
result
evidence/artifact reference if available
limitations
```

Không fabricate test result.

## Output

Cho substantial work, tạo `docs/test-plan.md` hoặc `docs/verification-matrix.md`:

```md
# Verification Plan
## Scope / risks
## Critical journeys
## Browser / responsive matrix
## Data/state coverage matrix
## Verification matrix
## Accessibility evidence
## Visual sanity / shared-owner coverage
## Performance evidence
## Regression coverage
## Failures / unresolved P0-P1
## Unverified areas
```

## Quality gate

- [ ] Critical journeys/risk drive test priority.
- [ ] Happy path + material recovery states covered.
- [ ] Conditional controls are rendered with deterministic data/state before being called covered.
- [ ] Responsive tested at pressure widths within declared scope.
- [ ] Browser matrix matches project or is explicitly proposed.
- [ ] Accessibility evidence level reported accurately.
- [ ] Visual changes visually inspected.
- [ ] Shared-owner visual changes have all-affected-route elementary sanity coverage.
- [ ] Visible-text sanity is not limited to an unjustified small selector whitelist.
- [ ] Changed interactive states remain readable/perceptible in actual rendered state.
- [ ] Human/focal media crop verified at target viewports when applicable.
- [ ] Primary/focal `cover` has verified crop contract or safer art direction.
- [ ] Performance uses budgets/conditions, not vanity score alone.
- [ ] Mock/simulated behavior not reported as real system pass.
- [ ] P0/P1 failures explicit.

## Anti-patterns

- “Looks good on my machine” = tested.
- Build success = functional/visual proof.
- Exact breakpoint-only testing.
- Automated accessibility scan = conformance.
- One Lighthouse run = field performance.
- Success toast = backend test pass.
- Testing only demo/happy-path content.
- Empty Cart = Checkout CTA tested.
- One representative page = enough after changing a shared footer/header/theme owner.
- CSS declaration says correct color = rendered contrast verified.
- Hand-picked button selector list = all interactive states covered.
- `object-position: top` = focal crop verified.
