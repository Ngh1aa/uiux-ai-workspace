---
name: localization-and-i18n
description: |
  Thiết kế website đa ngôn ngữ từ content model, URL, locale routing, typography, layout,
  language switcher đến SEO hreflang. Dùng khi website có từ hai locale trở lên hoặc cần
  chuẩn bị architecture để dịch mà không phá UX, responsive và component system.
---

# Localization & Internationalization

## Separate concerns

- **i18n**: architecture cho nhiều locale.
- **l10n**: content/culture adaptation cho locale cụ thể.

Không hardcode text trong reusable component nếu project dùng translation layer.

## Content rules

- UI copy phải có stable key và context.
- Không concatenate fragments khiến grammar sai khi dịch.
- Placeholder variables phải rõ nghĩa.
- Date/time/number/currency dùng locale-aware formatter.
- Không giả định English text length.

## Layout resilience

Test với text dài hơn 30–50%:

- Buttons không cắt label.
- Nav không overflow âm thầm.
- Cards không phụ thuộc fixed height vô lý.
- Heading wrap vẫn đẹp.
- Form label/error không phá grid.

## Vietnamese-specific checks

- Font phải có đầy đủ Vietnamese glyphs/diacritics.
- Line-height đủ cho dấu.
- Uppercase/letter-spacing không làm giảm readability.
- Search/sort nếu có phải xử lý Unicode đúng.

## Locale routing

Chọn strategy nhất quán: path/domain/subdomain theo product requirement. Language switcher nên đưa user tới **equivalent page** khi có, không luôn reset về homepage.

## SEO

- Unique localized title/description.
- Correct canonical cho từng locale.
- hreflang chỉ khi thực sự có equivalent localized pages.
- Sitemap/links phải crawlable.

## Translation completeness

Không release locale có menu dịch nhưng content chính/validation/error/legal vẫn lẫn ngôn ngữ nếu không chủ đích.

## Output

Nếu site multilingual, tạo `docs/localization-strategy.md` gồm locale list, route model, fallback, translation ownership, content fields và QA matrix.

## Acceptance criteria

- [ ] Locale routing xác định.
- [ ] Components chịu được text expansion.
- [ ] Dates/numbers/currency locale-aware.
- [ ] Language switcher preserve context.
- [ ] Metadata/hreflang plan đúng.
- [ ] Font glyphs locale được test.
