---
name: content-governance-and-cms
description: |
  Thiết kế content schema, CMS readiness, editorial ownership, migration và lifecycle cho website.
  Dùng khi site có nhiều bài/page/data lặp, cần dashboard/CMS, migrate website cũ hoặc cần đảm bảo
  content có thể vận hành lâu dài mà không phụ thuộc hardcoded markup.
---

# Content Governance & CMS

## Principle

Component model và content model phải tương thích nhưng không khóa chặt vào nhau. Editor nên thay content trong giới hạn an toàn mà không phá layout.

## Content inventory

Với mỗi content type xác định:

- Purpose.
- Required/optional fields.
- Field type.
- Validation/length guidance.
- Relationships/taxonomy.
- SEO fields.
- Media requirements.
- Ownership/lifecycle.

## Structured content

Ưu tiên fields có meaning (`title`, `summary`, `cta`) hơn blob HTML khổng lồ nếu content cần tái sử dụng. Rich text chỉ dùng khi editor thật sự cần tự do trong body content.

## Component/content contract

- Card title có max guidance nhưng layout phải chịu text dài hợp lý.
- Image field có aspect/focal/caption/alt metadata khi cần.
- CTA có label + destination + optional behavior, không lưu raw button HTML.
- Taxonomy có purpose rõ; tránh tag tự do vô hạn.

## Migration

Nếu migrate site cũ:

1. Export inventory.
2. Map old type/field → new schema.
3. Preserve URL/SEO identifiers.
4. Flag content không map được.
5. Import/transform.
6. QA counts, links, media, metadata.
7. Redirect removed/merged URLs.

## Governance

Xác định ai tạo, review, publish, update và archive content. Content quan trọng cần freshness rule và owner.

## Prototype mode

Nếu project chỉ là UI prototype, vẫn tạo mock content theo schema thật thay vì copy text trực tiếp khắp components; backend có thể để ngoài scope.

## Acceptance criteria

- [ ] Content types/fields có schema.
- [ ] Component không phụ thuộc content “đẹp hoàn hảo”.
- [ ] Media/SEO metadata có chỗ lưu.
- [ ] Migration có mapping + redirect consideration.
- [ ] Có ownership/freshness cho content vận hành dài hạn.
