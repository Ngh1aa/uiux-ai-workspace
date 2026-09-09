# Frontend Implementation Patterns

## Structure first

Page nên đọc được về semantics/content ngay cả trước decoration:
```html
<header>...</header>
<main>
  <section aria-labelledby="...">...</section>
</main>
<footer>...</footer>
```

## Responsive

Ưu tiên intrinsic layout:
- `minmax`, `auto-fit`, flex wrapping;
- `clamp()` cho scale phù hợp;
- container/content queries khi architecture hỗ trợ;
- image aspect ratio + object position có art-direction rationale.

Breakpoint được thêm khi **content breaks**, không vì “iPhone/iPad/Desktop”.

## State model

Interactive component nên có state source rõ. Tránh DOM class toggle rải rác khi framework state/component model phù hợp hơn.

## Images

- Có intrinsic dimensions/aspect ratio để giảm layout shift.
- Không tải hero 4K cho mọi viewport.
- Above-fold priority có chủ ý; lazy-load below-fold phù hợp.
- Alt strategy đến từ content purpose, không filename.

## JavaScript

- Chỉ hydrate/client-render phần cần interaction khi framework hỗ trợ server/static rendering.
- Avoid global listeners/scroll work nặng.
- Cleanup listeners/effects.
- Dynamic imports chỉ khi chunk boundary có lợi thật.

## Error handling

Async action phải preserve user intent/data, expose retry và distinguish validation error với network/server failure.
