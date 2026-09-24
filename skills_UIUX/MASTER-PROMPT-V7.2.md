# MASTER PROMPT V7.2 — PHASE-AWARE / SCOPE-AWARE STRUCTURAL IMPLEMENTATION OS
## V7.1 + DOMAIN-ROLE / RESPONSIVE-SCOPE GATE CORRECTIONS

> Kế nhiệm `MASTER-PROMPT-V7.1.md`. Đọc và giữ toàn bộ V7.1/V7.0/V6.0 **trừ các rule được override rõ dưới đây**.
>
> Bắt buộc đọc `PHASE-AWARE-GATING.md`, `website-delivery-pipeline/SKILL.md`, Design Contract và `docs/uiux/Phase-State.md` trước khi rollout.

## 1. PHASE-AWARE ENTRY

Chỉ requirement DUE NOW của implementation phase mới tham gia exit gate.

```text
DONE_VERIFIED
N/A_JUSTIFIED
PENDING_FUTURE_PHASE
BLOCKED
```

Requirement QA/release thuộc owner phase sau không được biến thành implementation blocker chỉ vì chưa verify.

Ngược lại, rendered representative-page evidence là DUE NOW trước full rollout cho substantial visual implementation; thiếu evidence này có thể `BLOCKED`.

## 2. RESPONSIVE SCOPE OVERRIDE

### `desktop_only`

Override mọi inherited rule bắt buộc mobile screenshots/mobile crop/mobile structural delta:

- verify declared desktop viewports/pressure points;
- mobile/tablet = `N/A_JUSTIFIED`;
- không cần chứng minh mobile composition khác desktop;
- không claim `fully responsive`.

### `responsive_all`

Giữ các gate desktop/tablet/mobile của V6/V7/V7.1.

Các câu `mobile equivalents`, `mobile delta`, `crop strategy works on mobile separately` chỉ là hard gate khi mobile nằm trong declared scope.

## 3. REPRESENTATIVE PAGE GATE — DOMAIN-ROLE-AWARE

Override V7.1 hard-code:

```text
Home + Shop/PLP + PDP + Collection
```

Bộ representative pages phải được chọn từ **actual sitemap + page-role matrix + critical journey**.

Chọn 2–4 materially different roles đủ chứng minh design DNA, composition diversity, decision-object hierarchy và media integrity.

Examples:

- ecommerce: Home + PLP + PDP + collection/checkout khi tồn tại;
- corporate: Home + service/solution + project/case study + contact/about khi material;
- education: Home + program + admissions + campus/news/event khi material;
- government/public: landing/service + detail/procedure + search/listing + form/transaction khi material.

Không tạo blocker vì project không có ecommerce-only route.

## 4. MEDIA FAMILY — APPLICABLE ONLY

Media owner contract chỉ áp dụng family tồn tại:

```text
hero/editorial
listing/card
project/case-study
leadership/profile
PDP/product media
thumbnail/gallery
collection/lookbook
related items
```

Không yêu cầu `PDP`/`PLP`/fashion crop rules cho site không có các role này.

Khi một family không tồn tại: `N/A_JUSTIFIED`, không phải `BLOCKED`.

## 5. OLD→NEW EVIDENCE

Với redesign existing:

- ưu tiên same-viewport OLD→NEW evidence;
- nếu Prompt 1 đã dùng documented fallback OLD baseline, implementation phải preserve limitation và tạo NEW screenshot ở matching comparable viewport/state khi feasible;
- pixel-perfect OLD comparison không được fabricate nếu OLD live render không tồn tại.

Chỉ block rollout khi thiếu evidence làm cho structural/crop correctness của representative implementation không thể review đáng tin cậy.

Với genuinely new website: OLD→NEW = `N/A_JUSTIFIED`; dùng NEW→DESIGN CONTRACT + cross-page review.

## 6. FULL ROLLOUT EXIT

Full rollout chỉ được bắt đầu khi:

- representative roles applicable đã render + inspect;
- no DUE-NOW P0/P1 macro issue;
- composition diversity requirement phù hợp actual number of material page roles;
- media integrity pass trên applicable families;
- responsive verification pass cho declared scope;
- current-phase `BLOCKED = 0`, `UNACCOUNTED = 0`;
- future QA/release items có `OWNER_PHASE` + verification plan.

Không giữ P2/P3 ngoài representative/critical scope như blocker implementation nếu Design Contract cho phép owner phase sau; phải ledger hóa rõ.

## 7. RELEASE AUTHORIZATION

Các release condition inherited chỉ kích hoạt khi release nằm trong authority.

- `no_release` → release scope `N/A_JUSTIFIED`;
- `create_pr_only` → không merge/deploy;
- `merge_only` → không deploy ngoài authority;
- `merge_and_deploy` → release checks + production smoke DUE NOW ở release phase.

## 8. DURABLE HANDOFF

Cập nhật `docs/uiux/Phase-State.md` sau representative pass/full implementation handoff.

> **Core principle:** implementation gate phải nghiêm với rendered quality cần chứng minh bây giờ, nhưng không được hard-code device/page roles không thuộc project hoặc release evidence thuộc phase sau.
