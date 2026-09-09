---
name: web-quality-and-performance
description: |
  Audit và tối ưu performance theo user-critical routes, Core Web Vitals, resource budgets,
  loading/runtime behavior và lab/field evidence. Dùng khi media, fonts, JS/CSS, third parties,
  rendering hoặc release performance có thể ảnh hưởng UX; không dùng một Lighthouse score cứng
  như bằng chứng duy nhất rằng website nhanh.
---

# Web Quality & Performance

## Principle

Performance là product constraint cần **budget + evidence**, không phải polish cuối cùng.

`critical journeys/routes → user conditions → budget → implementation → lab evidence → field evidence when available → regression control`

## Scope and baseline

Trước khi tối ưu:

- xác định key routes/templates;
- traffic/device/network/market context nếu biết;
- baseline lab metrics dưới điều kiện ghi rõ;
- field data (CrUX/RUM) nếu có;
- current resource sizes/counts;
- LCP candidate, third-party cost, heavy interaction/runtime hotspots.

Không invent field data/baseline.

## Core Web Vitals

Dùng current official thresholds/guidance khi task yêu cầu current numbers. Baseline phổ biến cần theo dõi:

- LCP — loading experience;
- INP — interaction responsiveness;
- CLS — visual stability.

Khi web access khả dụng và release decision phụ thuộc threshold, verify current official guidance thay vì dựa vào memory.

## Performance budget

Định nghĩa budget theo project/key route, có thể gồm:

| Budget dimension | Example role |
|---|---|
| LCP/INP/CLS | user experience target |
| JS/CSS/font/image bytes | transfer/parse/render cost |
| request count | connection/third-party complexity |
| hero/media weight | visual ambition constraint |
| third-party scripts | privacy/performance/control risk |
| long tasks/runtime | interaction responsiveness |

Không bắt mọi project dùng cùng `1.5MB`, `150KB JS`, `90 Lighthouse` hoặc image-size number. Nếu project chưa có budget, đề xuất `PROPOSED` budget dựa trên baseline/business/technical constraints và ghi assumption.

## LCP / loading

Kiểm:

- server/edge response path;
- render-blocking CSS/JS;
- discoverability/priority của LCP resource;
- hero image/video poster sizing/crop/format;
- font loading;
- client rendering/data waterfalls;
- unnecessary preloads/preconnects.

Rules:

- không lazy-load actual LCP image;
- khai báo intrinsic dimensions/aspect ratio;
- ưu tiên framework/platform image pipeline nếu có;
- preload/fetch priority chỉ khi evidence cho thấy resource thật sự critical;
- không preload hàng loạt asset.

## CLS / visual stability

Kiểm:

- image/embed dimensions;
- dynamic banners/ads/content insertion;
- font metric shifts;
- client hydration/content replacement;
- animation/layout changes;
- sticky/fixed UI.

Reserve layout space trước khi content arrives khi predictable.

## INP / runtime

Kiểm:

- long synchronous tasks;
- unnecessary re-renders;
- event handlers;
- layout thrashing;
- expensive hydration;
- large client bundles;
- work có thể defer/split/stream/offload.

Debounce/throttle/web workers/requestIdleCallback không phải universal solution; dùng theo root cause/browser support.

## Images / media

Art direction và performance phải đi cùng nhau:

- correct source dimensions;
- responsive variants/srcset/framework equivalent;
- modern efficient format khi stack hỗ trợ;
- appropriate quality;
- lazy load below-fold media;
- poster/fallback cho video;
- avoid autoplay media làm nghẽn critical path;
- reserve aspect ratio.

Không đặt một file-size ceiling giống nhau cho hero, product imagery và editorial photography nếu không có rationale.

## Fonts

- preload chỉ critical font resources;
- minimize families/weights theo actual brand need;
- self-host khi project/privacy/performance rationale phù hợp;
- `font-display` strategy có chủ đích;
- xem xét fallback metrics/size-adjust khi shift material;
- kiểm Vietnamese/locale glyph coverage trước subsetting.

## JavaScript / CSS

- ship only what route/interaction cần;
- code split/defer non-critical code theo framework;
- remove dead/duplicate code khi evidence có;
- avoid hydration/client JS cho static content nếu architecture cho phép;
- use compositor-friendly motion khi có thể;
- không rewrite stack chỉ để chase micro-optimization.

## Third parties

Inventory:

| Third party | Job | Bytes/requests | Main-thread cost | User/data impact | Can defer/remove? |
|---|---|---|---|---|---|

Third-party performance là cả loading, runtime, privacy và reliability concern.

## Lab vs field

### Lab
Dùng Lighthouse/DevTools/WebPageTest hoặc equivalent để reproduce/debug dưới controlled conditions.

### Field
Dùng CrUX/RUM/production telemetry khi có để hiểu real-user distribution.

Không nói “Core Web Vitals đạt” từ một Lighthouse run đơn lẻ. Lab score có variability và không thay field data.

## Verification matrix

Cho change material:

`change → target metric/budget → test condition → before/after evidence → regression risk`

Chạy nhiều lần hoặc dùng stable CI conditions khi metric dễ biến động.

## Output

Cho substantial audit, tạo `docs/performance-audit.md` hoặc equivalent:

```md
# Performance Audit
## Key routes / user conditions
## Baseline
## Proposed or approved budgets
## Main bottlenecks / root causes
## Changes
## Lab evidence
## Field evidence if available
## Third-party budget
## Remaining risks / unverified
```

## Quality gate

- [ ] Key routes/conditions rõ.
- [ ] Budget/target có rationale, không chỉ vanity score.
- [ ] LCP/CLS/INP root causes được inspect khi relevant.
- [ ] Media/font/JS/third-party costs được xem xét.
- [ ] Lab và field evidence được phân biệt.
- [ ] Performance claims ghi điều kiện test.
- [ ] Không giảm accessibility/content/brand-critical functionality chỉ để chase score.

## Anti-patterns

- One Lighthouse score = production performance proof.
- Universal resource ceilings không xét project.
- Lazy-load LCP media.
- Preload mọi thứ.
- Add JS animation/plugin cho effect CSS/native đủ làm.
- Hide/remove meaningful content để tăng score.
- Optimize micro-details trước waterfall/bundle/render root causes.
