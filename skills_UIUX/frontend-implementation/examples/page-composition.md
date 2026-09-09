# Example — Compose, don't clone

Bad:
```text
HomeHero.tsx
AboutHero.tsx
ServiceHero.tsx
ProductHero.tsx
```
Bốn component gần giống, chỉ khác alignment/image.

Better khi semantics thật sự chung:
```text
Hero
├── variant: media-split | media-overlay | editorial
├── tone: default | brand | inverse
├── slots: eyebrow/title/body/actions/media
└── responsive contract
```

Nhưng **không** ép mọi hero vào một mega-component nếu page type có behavior/anatomy khác hẳn. Reuse theo semantics, không theo tên “Hero”.
