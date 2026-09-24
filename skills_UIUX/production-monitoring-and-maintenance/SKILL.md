---
name: production-monitoring-and-maintenance
description: |
  Theo dõi và bảo trì website sau release: uptime, errors, Core Web Vitals field data,
  analytics, SEO health, broken links, dependencies, security và regression. Dùng sau deploy,
  khi lập maintenance plan hoặc khi cần phân biệt incident fix với cải tiến sản phẩm.
---

# Production Monitoring & Maintenance

## Post-release principle

Deploy không phải điểm kết thúc. Production data là vòng feedback mới cho UX và technical quality.

## Health signals

Theo dõi ít nhất:

- Availability/uptime.
- Client/server errors.
- Critical form/checkout/lead success rate.
- Core Web Vitals field data nếu có.
- Broken links/404 tăng bất thường.
- Search indexing/crawl issues.
- Conversion/event tracking health.
- Dependency/security alerts.

## Incident triage

| Severity | Meaning | Example |
|---|---|---|
| P0 | Core business/user task unavailable | Checkout/form/login down |
| P1 | Major degradation | Mobile nav broken, severe layout issue |
| P2 | Limited defect | One secondary component/style bug |
| P3 | Enhancement | Polish/optimization |

Fix root cause; tránh patch UI che lỗi data/network thật.

## Regression review

Sau change lớn kiểm lại:

- Primary journeys.
- Key templates.
- SEO metadata/indexability.
- Analytics events.
- Performance deltas.
- Accessibility critical paths.

## Maintenance cadence

Tùy project nhưng plan nên có:

- Dependency/security review.
- Content/link freshness review.
- Performance/SEO review.
- Analytics funnel review.
- Design-system drift review.

Không update dependency hàng loạt mà không đọc breaking changes/test.

## Learning loop

Production finding → issue → priority → change → verification → decision log nếu ảnh hưởng pattern/system.

## Output

Tạo `docs/maintenance-plan.md` nếu project cần vận hành dài hạn.

## Acceptance criteria

- [ ] Critical journeys có health signal.
- [ ] Có severity/ownership process.
- [ ] Có regression checklist.
- [ ] Analytics/SEO/performance được xem là production quality, không chỉ launch task.
- [ ] Dependency update có test và rollback plan phù hợp.
