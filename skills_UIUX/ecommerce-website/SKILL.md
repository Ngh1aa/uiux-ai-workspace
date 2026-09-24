---
name: ecommerce-website
description: |
  Domain playbook cho ecommerce/catalogue website. Dùng khi có product discovery, category,
  search/filter, comparison, PDP, wishlist/cart/checkout hoặc lead-to-purchase flow cần tối ưu
  findability, product confidence, conversion và post-purchase UX mà không dùng dark patterns.
---

# Ecommerce Website Playbook

## Core journey

`Discover → browse/search → narrow/filter → compare → evaluate PDP → cart → checkout → confirmation → post-purchase`

## Catalogue UX

- Category naming theo customer language.
- Filters chỉ dựa trên attributes thật có giá trị chọn mua.
- Selected filters visible và removable.
- Sort options ít nhưng meaningful.
- Product cards hiển thị đủ info để quyết định có mở PDP hay không.

## Search

Search phải có scope rõ, useful no-results recovery và preserve query/filter state khi quay lại listing.

## Product detail page

Ưu tiên:

- Product name/value.
- Price/availability nếu applicable.
- High-quality media.
- Variant selection.
- Key specs/benefits.
- Shipping/returns/warranty.
- Reviews/proof nếu có.
- Related/compatible products có rationale.

Không giấu critical cost hoặc availability tới cuối checkout.

## Comparison

Nếu products có specs phức tạp, provide compare flow với aligned attributes và highlight difference, không chỉ đặt nhiều card cạnh nhau.

## Cart/checkout

- Preserve cart.
- Editable quantity/variant.
- Transparent costs.
- Guest checkout nếu business cho phép.
- Validation inline, data không mất sau error.
- Order confirmation có summary + next step.

## Ethics

Không dùng fake scarcity, preselected paid add-ons, hidden unsubscribe, confusing confirm/cancel hierarchy hoặc countdown giả.

## Acceptance criteria

- [ ] User tìm và lọc product hiệu quả.
- [ ] PDP trả lời key purchase questions.
- [ ] Cost/availability minh bạch.
- [ ] Cart/checkout recovery tốt.
- [ ] Mobile filters/variants/checkout usable.
