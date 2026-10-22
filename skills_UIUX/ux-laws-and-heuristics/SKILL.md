---
name: ux-laws-and-heuristics
description: |
  Tham chiếu các UX laws và heuristics để đánh giá và cải thiện quyết định thiết kế.
  KHÔNG áp dụng mọi law một cách máy móc — mỗi quyết định cần ghi rõ user task,
  evidence, trade-off và cách kiểm chứng.
globs:
  - "docs/ux-review.md"
  - "docs/decision-log.md"
---

# UX Laws & Heuristics

## Mục đích

Cung cấp framework để đánh giá thiết kế dựa trên các nguyên tắc UX đã được nghiên cứu. Đây là **heuristic để tạo giả thuyết**, KHÔNG phải luật tuyệt đối. Mỗi lần áp dụng phải ghi rõ context, evidence và trade-off.

## ⚠️ Quy tắc quan trọng

1. **KHÔNG** liệt kê tất cả laws rồi áp dụng hết vào mọi design
2. **CÓ** chọn law phù hợp với user task cụ thể đang giải quyết
3. Mỗi quyết định design dựa trên UX law phải ghi vào decision log theo format:

```markdown
### Decision: [Mô tả quyết định]
- **User task**: [Task cụ thể]
- **Law applied**: [Tên law]
- **Rationale**: [Tại sao law này phù hợp cho context này]
- **Trade-off**: [Đánh đổi gì khi áp dụng]
- **How to verify**: [Cách kiểm chứng hiệu quả]
```

## UX Laws Reference

### 1. Hick's Law — Thời gian quyết định tăng theo số lượng lựa chọn

Mô hình choice-reaction thường có dạng `T = a + b·log₂(n + 1)` trong điều kiện
thí nghiệm tương ứng. Không dùng số lựa chọn để dự đoán trực tiếp thời gian tìm
kiếm trên website; familiarity, xác suất lựa chọn, grouping và labeling đều ảnh hưởng.

**Khi nào áp dụng**:
- Navigation có quá nhiều items
- Form có quá nhiều options
- Dashboard hiển thị quá nhiều actions cùng lúc
- Pricing page có quá nhiều plans

**Hướng dẫn thực thi**:
- Giảm số lượng options hiển thị cùng lúc
- Nhóm related options thành categories
- Highlight recommended/default option
- Progressive disclosure: hiển thị options dần dần

**Cảnh báo**: Không áp dụng cực đoan. Nếu giảm options quá mức, user phải click nhiều lần hơn → tăng friction. Cân bằng giữa số lượng choices và số bước hoàn thành task.

### 2. Fitts's Law — Target lớn + gần = dễ click hơn

Một dạng Shannon thường dùng là `MT = a + b·log₂(D/W + 1)`; `a`, `b` phải được
ước lượng theo điều kiện đo. `D/W` một mình không phải công thức thời gian.

**Khi nào áp dụng**:
- CTA button quá nhỏ hoặc ở vị trí khó reach
- Touch targets trên mobile
- Submit button xa form fields
- Close button nhỏ trên modal

**Hướng dẫn thực thi**:
- Web: WCAG 2.2 **2.5.8, level AA** dùng **24×24 CSS px**, với các ngoại lệ
  spacing/equivalent/inline/user-agent/essential. **2.5.5, level AAA** dùng
  **44×44 CSS px** với ngoại lệ riêng. 44×44 có thể là mục tiêu usability của
  project; không gọi đó là minimum AA hay đổi trực tiếp CSS px thành native pt/dp.
- CTA buttons phải nổi bật và đủ lớn
- Primary action gần vùng user đang tương tác
- Navigation items có sufficient padding
- Infinite edges: tận dụng screen edges cho actions (sticky nav, fixed CTA)

**Cảnh báo**: Nút lớn hơn không phải lúc nào cũng tốt. Button quá lớn chiếm space và giảm visual hierarchy.

### 3. Jakob's Law — Users spend most time on OTHER sites

**Khi nào áp dụng**:
- Thiết kế navigation pattern
- Placement của logo, search, cart, login
- Form conventions (labels, validation, submit)
- Quyết định có dùng unconventional layout không

**Hướng dẫn thực thi**:
- Dùng navigation, search, back và form conventions quen thuộc với audience/platform.
- Vị trí logo/search/submit phụ thuộc task, reading direction, viewport và platform;
  không có yêu cầu phổ quát rằng submit phải ở bottom-right hay search ở top-right.
- Giữ labels, affordances và kết quả hành động nhất quán với kỳ vọng đã có.

**Cảnh báo**: Convention không phải lúc nào cũng best. Nếu convention gây confusion cho đối tượng cụ thể, có thể deviate — nhưng phải có evidence mạnh.

### 4. Miller / Chunking — Phân biệt nhớ lại và nhận diện

`7±2` là kết quả lịch sử về giới hạn xử lý/nhớ trong điều kiện cụ thể, không phải
giới hạn số mục nhìn thấy trên UI. Navigation và catalog thường hỗ trợ recognition,
khác với việc buộc user nhớ thông tin qua nhiều màn hình.

**Khi nào áp dụng**:
- Số items trong navigation
- Số steps trong process/wizard
- Số features hiển thị cùng lúc
- Số data points trong comparison

**Hướng dẫn thực thi**:
- Chunk theo quan hệ có nghĩa, không ép số mục cố định.
- Navigation: chọn breadth/depth theo information scent, grouping, familiarity và
  scanning cost; dùng owner [information-architecture](../information-architecture/SKILL.md).
- Step indicators cho multi-step processes
- Comparison: chọn số option từ attributes/task và khả năng đối chiếu; cho pin/filter
  khi cần, không dùng một giới hạn 5 option cho mọi bảng.
- Dùng headings và visual grouping để break content

**Cảnh báo**: Không dùng Miller để biện minh menu ≤7. Kiểm tra phần việc user phải
nhớ, thông tin còn nhìn thấy và chỗ có thể externalize memory.

### 5. Von Restorff Effect — Items khác biệt được nhớ tốt hơn

**Khi nào áp dụng**:
- CTA cần nổi bật giữa nội dung
- Pricing table cần highlight recommended plan
- Important information cần attention
- New features cần giới thiệu

**Hướng dẫn thực thi**:
- Primary CTA khác biệt visual so với secondary actions
- "Most popular" hoặc "Recommended" badge trên pricing
- Highlight thay đổi mới bằng badge/color/animation
- NHƯNG nếu mọi thứ đều "nổi bật" → không gì nổi bật cả

**Cảnh báo**: Quá nhiều visual emphasis = visual noise. Chỉ 1-2 elements nên "stand out" per viewport.

### 6. Gestalt Principles — Cách não nhóm visual elements

#### Proximity
- Items gần nhau perceived là related
- **Áp dụng**: Group form labels gần inputs, space giữa sections > space giữa items trong section

#### Similarity
- Items giống nhau perceived là related
- **Áp dụng**: Same styling cho same-level elements (cards, nav items, list items)

#### Continuity
- Mắt theo dõi lines và curves
- **Áp dụng**: Alignment, grid consistency, visual flow từ top-left đến bottom-right (F-pattern)

#### Closure
- Não tự complete incomplete shapes
- **Áp dụng**: Cards không cần visible borders nếu có clear background contrast

#### Common Region
- Items trong cùng khu vực perceived là group
- **Áp dụng**: Cards, containers, sections dùng background/border để group content

### 7. Response feedback — Chọn budget theo tác vụ

**Khi nào áp dụng**:
- Loading states
- Form submission feedback
- Navigation transitions
- Search results

**Hướng dẫn thực thi**:
- Đặt feedback/performance budget có đơn vị, điều kiện đo và rationale theo task;
  không trình bày 100/400ms như guarantee về engagement.
- Chọn skeleton, spinner hoặc progress từ thời gian chờ và thông tin có thật;
  skeleton không luôn tốt hơn spinner.
- Optimistic UI chỉ khi rollback/reconciliation rõ và hệ quả phù hợp; pending
  payment/booking/approval không được hiển thị thành hoàn tất trước xác nhận thật.
- Cải thiện cả thời gian thực lẫn khả năng hiểu trạng thái; không che latency bằng
  animation hoặc confirmation giả.

### 8. Tesler's Law — Mọi ứng dụng có mức complexity không thể giảm

**Khi nào áp dụng**:
- Simplifying complex forms
- Reducing feature scope
- Hiding vs showing advanced options

**Hướng dẫn thực thi**:
- Accept rằng một số tasks inherently complex
- Design choice: complexity ở phía system hay user?
- Progressive disclosure: simple first, advanced on demand
- Smart defaults giảm decisions cho user
- Nhưng KHÔNG giấu critical information để "đơn giản hóa"

### 9. Peak-End Rule — Trải nghiệm được đánh giá bởi peak moment và end moment

**Khi nào áp dụng**:
- Onboarding flow
- Checkout process
- Form completion
- Task completion

**Hướng dẫn thực thi**:
- Chọn confirmation/closure hữu ích; animation/delight chỉ khi phù hợp cảm xúc và task.
- End experience positively: confirmation page, next steps, thank you
- Tránh negative peaks: long load, confusing error, data loss
- Last impression matters: checkout confirmation, email follow-up

### 10. Aesthetic-Usability Effect — Thiết kế đẹp perceived là dễ dùng hơn

**Khi nào áp dụng**: Luôn luôn, nhưng đặc biệt khi:
- First impression matters (landing page)
- Building trust (finance, health, legal)
- Competing with alternatives

**Hướng dẫn thực thi**:
- Invest vào visual polish
- NHƯNG: beautiful UI che giấu usability issues → test cả hai
- Aesthetics alone không thể cứu bad IA hoặc confusing flows

## Nielsen's Heuristics (Quick Reference)

| # | Heuristic | Application |
|---|-----------|-------------|
| 1 | Visibility of system status | Loading indicators, progress bars, current state |
| 2 | Match between system & real world | Dùng ngôn ngữ user, không phải system language |
| 3 | User control & freedom | Undo, back, exit rõ ràng |
| 4 | Consistency & standards | Follow platform conventions |
| 5 | Error prevention | Disable invalid actions, confirm destructive ones |
| 6 | Recognition > recall | Show options, don't make users remember |
| 7 | Flexibility & efficiency | Shortcuts cho expert, simplicity cho beginner |
| 8 | Aesthetic & minimalist design | Chỉ hiển thị information cần thiết |
| 9 | Help users with errors | Clear error messages, suggest recovery |
| 10 | Help & documentation | Searchable, task-oriented, concise |

## UX Review Template

Khi review một page/component, dùng template sau:

```markdown
## UX Review: [Page/Component name]

### Context
- **Primary user task**: [Task]
- **User persona**: [Persona]
- **Device/context**: [Desktop/mobile/tablet]

### Evaluation
| Criterion | Rating | Evidence | Recommendation |
|-----------|--------|----------|----------------|
| Clarity of CTA | 🟢🟡🔴 | [What you observed] | [Improvement] |
| Information hierarchy | 🟢🟡🔴 | [Evidence] | [Improvement] |
| Cognitive load | 🟢🟡🔴 | [Evidence] | [Improvement] |
| Findability | 🟢🟡🔴 | [Evidence] | [Improvement] |
| Error handling | 🟢🟡🔴 | [Evidence] | [Improvement] |
| Accessibility | 🟢🟡🔴 | [Evidence] | [Improvement] |
| Responsiveness | 🟢🟡🔴 | [Evidence] | [Improvement] |

### UX Laws Applied
| Law | Specific application | Trade-off |
|-----|---------------------|-----------|
| [Law name] | [How it applies here] | [What was sacrificed] |
```

## Source and scope review

Khi chuẩn hoặc số định lượng ảnh hưởng quyết định, đọc
[source/scope register](references/principle-sources.md). Ghi rõ version/level,
đơn vị, ngoại lệ, nguồn, ngày kiểm và cách kiểm chứng; tách standard requirement
khỏi heuristic và project hypothesis. Không thêm checklist cho law không liên quan.

## Output bắt buộc

### `docs/ux-review.md`
UX review cho mỗi major page/flow.

### Updates to `docs/decision-log.md`
Mỗi design decision dựa trên UX law phải được ghi lại.

## Anti-patterns cần tránh

❌ Áp dụng TẤT CẢ UX laws vào MỌI page/component
❌ Cite UX law mà không ghi context và trade-off
❌ Dùng UX law để justify preference thay vì improve user outcome
❌ Confuse heuristics (guidelines) với rules (requirements)
❌ Apply Fitts's Law mà không xét viewport và context
❌ Enforce Miller's 7±2 như hard rule cho mọi list
