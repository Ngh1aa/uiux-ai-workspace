# COVERAGE.md

Cập nhật: 2026-09-21

Quy tắc: 0–5; không có artifact + verification phù hợp = 0. P0 chỉ inventory nên **không dùng mô tả portfolio để tự nâng điểm**.

| Mảng | Baseline | Evidence state | Ghi chú |
|---|---:|---|---|
| Product & UX strategy | 0/5 | UNKNOWN | Chưa audit project context/decision evidence |
| Research & validation | 0/5 | UNKNOWN | Chưa xác minh research/validation method |
| IA & user flows | 0/5 | UNKNOWN | Chưa audit recovery/edge artifacts |
| Visual/UI craft | 0/5 | UNKNOWN | Portfolio có screenshot/live links nhưng chưa rendered QA trong run này |
| Design system | 0/5 | UNKNOWN | Chưa verify tokens/components/states ở target repos |
| Interaction & motion | 0/5 | UNKNOWN | Chưa browser-test hero/micro-interactions |
| Accessibility | 0/5 | UNKNOWN | Chưa Playwright/axe/keyboard/contrast QA target |
| Responsive & đa nền tảng | 0/5 | UNKNOWN | Chưa verify 375/768/1440 |
| UX writing & content | 0/5 | UNKNOWN | Chưa stress-test Vietnamese/long strings/states |
| Domain phức tạp | 0/5 | UNKNOWN | Domain labels VERIFIED nhưng product-depth evidence chưa audit |

Điểm sẽ được nâng **theo từng project** khi A1/A2/A3/B1 tạo artifact và verification thật. Không dùng average để che hard-gate fail.
