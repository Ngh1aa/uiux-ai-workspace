# FINAL UI/UX / VISUAL / CONTENT QA & REMEDIATION V3.2
## V3.1 + PHASE-AWARE / RESPONSIVE-SCOPE / DOMAIN-ROLE CORRECTIONS + ELEMENTARY VISUAL SANITY HARDENING

> Kế nhiệm `FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.1.md`. Đọc và giữ V3.1/V3.0/V2.0 **trừ các rule được override rõ dưới đây**.
>
> Bắt buộc đọc `PHASE-AWARE-GATING.md`, Design Contract, Requirement Coverage Ledger, `docs/uiux/Phase-State.md` và khi visual work substantial/shared thì `ui-craft-and-visual-qa/checklists/elementary-visual-sanity-gate.md`.

## 1. FINAL-QA REQUIREMENT ACCOUNTING

Final QA là owner phase của các verification được giao cho nó. Khi owner phase đã tới, item không được tiếp tục giữ `PENDING_FUTURE_PHASE` để né lỗi.

Dùng:

```text
DONE_VERIFIED
N/A_JUSTIFIED
PENDING_FUTURE_PHASE
BLOCKED
```

Final QA chỉ PASS khi:

- all Final-QA DUE-NOW requirements accounted;
- `BLOCKED = 0` cho Final-QA scope;
- `UNACCOUNTED = 0`;
- no unresolved DUE-NOW P0/P1 macro/critical issue;
- elementary visual sanity gate PASS khi applicable;
- mọi release-only item chưa đến hạn có owner phase rõ.

## 2. RESPONSIVE SCOPE OVERRIDE

### `desktop_only`

Override mọi inherited requirement bắt buộc desktop + mobile:

- inspect declared desktop representative viewports/pressure points;
- mobile/tablet checks = `N/A_JUSTIFIED`;
- `Mobile delta status` phải report `N/A_JUSTIFIED — desktop_only`;
- không claim `fully responsive`.

### `responsive_all`

Giữ desktop/tablet/mobile rendered review và intentional mobile recomposition requirements.

## 3. OLD→NEW APPLICABILITY

- redesign existing + reliable OLD evidence → OLD→NEW same/comparable viewport is DUE NOW;
- redesign existing nhưng Prompt 1 đã document fallback baseline → dùng best comparable OLD evidence, ghi limitation, không fabricate pixel-perfect comparison;
- genuinely new website → OLD→NEW = `N/A_JUSTIFIED`; thay bằng NEW→DESIGN CONTRACT + NEW→NEW cross-page QA.

Không block new website vì không có OLD screenshot.

## 4. PAGE-SPECIFIC CHECKS — ACTUAL ROLES ONLY

Các check ecommerce/fashion trong V3.1 chỉ bắt buộc khi actual sitemap có role tương ứng.

Ví dụ:

- Shop/PLP rules → only if listing/catalogue role exists;
- PDP rules → only if product/detail decision role exists;
- Collection/lookbook → only if actual editorial/collection role exists;
- corporate/education/public site phải dùng page-role checklist từ Design Contract + sitemap thay vì giả lập ecommerce pages.

Missing non-existent role = `N/A_JUSTIFIED`, không phải FAIL/BLOCKED.

## 5. REPRESENTATIVE ROUTES + SHARED-OWNER COVERAGE

Representative set phải map từ actual page-role matrix và critical journeys, không từ universal fixed list.

Final QA phải inspect:

- all representative primary roles chosen by risk/materiality;
- any route that carried a known P0/P1 regression;
- cross-page contact sheet/montage when substantial multi-page work;
- applicable media families and state variants.

### Shared-owner override — hard gate

Representative sampling **không đủ** cho elementary sanity nếu thay đổi owner dùng chung như:

- header/nav/footer;
- theme/surface token hoặc cascade layer;
- shared button/CTA/link variant;
- typography/color role ảnh hưởng nhiều template.

Khi đó phải:

1. map owner → **all affected routes/templates**;
2. smoke/check visibility trên mọi affected route/template;
3. inspect ít nhất một rendered instance cho mỗi semantic state/context khác biệt (light, dark/inverse, image overlay, disabled, selected...);
4. deep aesthetic review vẫn có thể representative, nhưng elementary visibility/state sanity phải phủ hết affected surface.

## 6. ELEMENTARY VISUAL SANITY — HARD GATE

Chạy trước khi chấm polish/aesthetic sâu.

### 6.1 Surface / foreground pairing

FAIL nếu:

- important text chỉ nhìn được khi bôi đen/select;
- foreground và rendered background effectively cùng màu / `1:1`;
- shared surface đổi light↔dark nhưng descendant text/link/icon/divider/control không được audit/re-pair;
- source CSS nói đúng màu nhưng computed browser style bị selector/cascade khác override.

`background` và `foreground/content` là một contract. Không chấp nhận fix chỉ đổi background.

### 6.2 Interactive states

Inspect applicable:

`default → hover → focus-visible → active/selected → disabled → loading → success/error`

FAIL nếu label/icon biến mất, state đổi foreground nhưng không có compatible surface/border, hoặc disabled control trở thành ô trống không đọc được.

Automated contrast/computed-style checks được khuyến nghị cho production-candidate/release/shared variants nhưng **không** thay thế human rendered inspection và không tự tạo claim WCAG conformance.

### 6.3 Human / focal-subject crop

Với hero/feature media có người hoặc focal subject rõ:

- inspect actual crop ở mọi declared viewport/pressure point;
- `object-fit: cover` / `object-position` declaration không phải evidence;
- cắt qua face/eyes/top-of-head/primary identifying feature mà không có art-direction rationale = P1 (hoặc P0 nếu mất nội dung quyết định chính);
- nếu một asset không sống được qua các ratio, phải dùng responsive art direction/alternate crop/layout.

### 6.4 Screenshot evidence

Screenshot tồn tại nhưng chưa mở/inspect = **không có visual evidence**.

Nếu screenshot nhìn hỏng nhưng CI/build/DOM metrics xanh, screenshot thắng và phase FAIL/BLOCKED.

## 7. USER-CAUGHT OBVIOUS DEFECT PROMOTION

Nếu user/reviewer bắt được lỗi obvious mà QA lẽ ra phải thấy:

1. fix project root owner;
2. add project-level regression/check khi feasible;
3. update owning skill/checklist nếu failure generalizable;
4. add/promote regression eval case trong skill library;
5. exercise guard mới trước khi close remediation.

Không coi việc vá project một lần là reliability fix hoàn chỉnh.

## 8. RELEASE / DEPLOYMENT

Release verification chỉ DUE NOW khi release được user yêu cầu và authority cho phép.

- `no_release` → release/deployment = `N/A_JUSTIFIED`; Final QA vẫn có thể PASS;
- `create_pr_only` → verify PR state only;
- `merge_only` → verify merge only;
- `merge_and_deploy` → deployment + production smoke DUE NOW.

Không trả `BLOCKED` chỉ vì config chủ động cấm release.

## 9. FINAL REPORT

Report tối thiểu:

```text
Final QA result: PASSED / BLOCKED
Declared responsive scope
Representative roles reviewed
Shared-owner all-route sanity coverage
Elementary visual sanity: PASS / FAIL / N/A_JUSTIFIED
Interactive state visibility status
Human/focal crop status when applicable
OLD→NEW: PASS / FAIL / N/A_JUSTIFIED / BLOCKED
NEW→DESIGN CONTRACT
NEW→NEW cross-page status
Media/layout integrity on applicable families
DUE-NOW P0/P1 remaining
Pending release-only requirements by owner
Release status / N/A_JUSTIFIED
```

## 10. HUMAN VISUAL VETO RETAINED

Screenshot obvious broken vẫn FAIL dù CI/build/DOM metrics xanh.

Phase-aware/scope-aware không được dùng để hạ tiêu chuẩn của verification thực sự DUE NOW.

> **Core principle:** Final QA phải chặn lỗi thật trên scope thật. Invisible text, disappearing CTA states, shared cascade regressions và unjustified focal crop là lỗi release-blocking cơ bản, không phải “polish phụ”.
