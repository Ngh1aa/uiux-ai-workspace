# MASTER PRE-DESIGN RESEARCH PROMPT V4.2
## V4.1 + PHASE-AWARE / RESPONSIVE-SCOPE-AWARE GATING

> Kế nhiệm `MASTER-PRE-DESIGN-RESEARCH-PROMPT-V4.1.md`. Đọc và giữ toàn bộ V4.1/V4.0/V3.0 **trừ các rule được override rõ dưới đây**.
>
> Bắt buộc đọc thêm `PHASE-AWARE-GATING.md` và `website-delivery-pipeline/SKILL.md` trước khi kết luận Phase 1 PASS/BLOCKED.

## 1. PHASE-AWARE OVERRIDE — HARD RULE

Không được biến requirement của phase sau thành blocker của Prompt 1.

Dùng trạng thái:

```text
DONE_VERIFIED
N/A_JUSTIFIED
PENDING_FUTURE_PHASE
BLOCKED
```

`PARTIAL/UNVERIFIED` chỉ thành `BLOCKED` khi verification đó là exit criterion **DUE NOW** của Prompt 1.

Future NEW-render QA, implementation regression, production smoke, release verification phải là `PENDING_FUTURE_PHASE` với `OWNER_PHASE` + verification plan nếu chúng chưa đến hạn.

Prompt 1 chỉ `PASSED` khi current-phase `BLOCKED = 0`, current-phase `UNACCOUNTED = 0`, mọi current exit criterion có evidence và mọi pending item có future owner.

## 2. OLD RENDERED BASELINE — FALLBACK EVIDENCE OVERRIDE

Override V4.0 rule coi failure to capture live OLD screenshot là blocker mặc định.

Nếu redesign existing website:

1. ưu tiên actual OLD rendered screenshots cùng viewport;
2. nếu live/browser capture không khả dụng, dùng evidence thay thế theo thứ tự phù hợp:
   - screenshot/user-provided capture đã có;
   - existing project screenshots/visual artifacts;
   - archived/reference capture đáng tin cậy;
   - source/layout/component inspection đủ để xác định current silhouette với limitation rõ.

Ghi loại evidence và limitation.

Chỉ `BLOCKED` Prompt 1 khi thiếu OLD visual evidence làm cho **material structural delta không thể xác định đáng tin cậy**.

Nếu baseline evidence thay thế đủ để tạo Redesign Delta Contract nhưng chưa đủ cho pixel-level OLD→NEW proof, Prompt 1 có thể PASS và pixel-level proof được giao cho owner phase phù hợp.

Không claim `OLD visual baseline verified from live render` nếu thực tế chỉ dùng fallback evidence.

## 3. RESPONSIVE SCOPE OVERRIDE

Responsive requirement phải theo Project Config / Design Contract.

### `desktop_only`

- desktop viewports/pressure points = DUE NOW;
- mobile/tablet requirements inherited từ V3/V4/V4.1 = `N/A_JUSTIFIED`;
- không yêu cầu `mobile transformation rules`, mobile screenshots, mobile crop strategy hoặc mobile composition proof để Prompt 1 PASS;
- không claim `fully responsive`.

Các artifact cũ có cột mobile vẫn có thể giữ cột đó với giá trị `N/A — desktop_only`.

### `responsive_all`

Giữ toàn bộ yêu cầu intentional desktop/tablet/mobile composition của V3/V4/V4.1.

## 4. MEDIA CONTRACT — APPLICABLE FAMILIES ONLY

Media/Focal Contract chỉ bắt buộc cho component/page families thực sự tồn tại hoặc nằm trong approved sitemap.

Không block corporate/education/nonprofit site vì không có `PDP`, `PLP`, `related products` hay ecommerce-only family.

Ví dụ:

- ecommerce → Home hero, PLP/product card, PDP, collection/related khi tồn tại;
- corporate → hero/editorial, case-study card, leadership/media, project/detail gallery khi tồn tại;
- education → campus/program/event/news media families khi tồn tại.

## 5. PROMPT 1 HANDOFF — SCOPE-AWARE

Prompt 1 có thể PASS khi trả lời được:

1. structural redesign delta nào người dùng sẽ nhận ra và vì sao;
2. page-role composition families nào được chọn;
3. asset/media nào có crop/focal risk trong **applicable component families**;
4. responsive transformation cho các viewport **in declared scope**;
5. evidence nào sẽ verify OLD→NEW và media integrity ở owner phase tiếp theo;
6. current-phase blocker count = 0 và pending future verification đã có owner.

Không hỏi mobile-specific câu như một hard gate khi `desktop_only`.

## 6. DURABLE HANDOFF

Cập nhật `docs/uiux/Phase-State.md` với phase result, immutable skill SHA, due-now blocker/unaccounted counts và pending-by-owner counts.

> **Core principle:** Prompt 1 phải nghiêm với decision/evidence cần có bây giờ, nhưng không được FAIL vì requirement ngoài scope hoặc evidence chỉ có thể xuất hiện ở phase sau.
