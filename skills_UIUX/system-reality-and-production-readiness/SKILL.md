---
name: system-reality-and-production-readiness
description: |
  Phân biệt feature/integration thật, mock, static, simulated, partial và unknown; định nghĩa data/API/CMS
  contracts, truthful states và production-readiness gaps trước khi agent gọi một website/flow là hoạt động
  hoặc sẵn sàng production. Dùng cho prototype, integration work, release hardening và full-site implementation.
---

# System Reality & Production Readiness

## Goal

Ngăn một UI “trông như hoạt động” bị nhầm thành hệ thống thực sự hoạt động.

Core rule:

`rendered state ≠ verified system behavior`

## Reality labels

Mỗi material feature/integration phải được phân loại:

- `REAL` — integration/behavior thật và đã verify trong scope hiện tại;
- `MOCK` — dữ liệu/response giả để phát triển UI;
- `STATIC` — nội dung hardcoded, không có runtime integration;
- `SIMULATED` — UI giả lập behavior nhưng không gọi hệ thống thật;
- `PARTIAL` — một phần integration thật, còn gap rõ;
- `UNKNOWN` — chưa đủ evidence để xác định.

Không tự nâng `PARTIAL/UNKNOWN` thành `REAL`.

## Trigger examples

Dùng khi có:

- form submit;
- search/filter có backend/data source;
- login/account/auth;
- checkout/payment;
- CMS/content API;
- CRM/lead integration;
- analytics/consent;
- uploads;
- realtime/status data;
- prototype được chuẩn bị đưa production;
- website có nhiều static/mock data nhưng user yêu cầu “hoàn thiện”.

Không cần cho local CSS-only fix không đụng data/behavior.

## Workflow

### 1. Inventory material capabilities

Tạo bảng:

| Capability | UI exists | Data/Service | Reality | Evidence | Risk if wrong |
|---|---|---|---|---|---|

Ví dụ:

| Contact form | yes | unknown endpoint | UNKNOWN | no network evidence | false lead capture |
| Product filter | yes | local JSON | STATIC | source inspection | acceptable prototype only |

### 2. Separate UI state from system state

Không được suy luận:

- success message → backend accepted;
- spinner → request exists;
- search box → search service exists;
- login screen → authentication exists;
- order confirmation → payment captured;
- dashboard chart → source data is live;
- CMS-like editor → persistence exists;
- analytics event name → event is actually emitted/received.

### 3. Define integration contract

Với feature dynamic, ghi khi applicable:

```text
Source / endpoint
Input schema
Output schema
Required fields
Optional fields
Auth / permission
Loading state
Empty state
Error state
Partial / stale state
Retry / recovery
Idempotency / duplicate-submit concern
Cache / freshness
Privacy / logging implications
Owner / system of record
```

Không invent endpoint/schema nếu project chưa có; label `UNKNOWN` hoặc `PROPOSED`.

### 4. Truthful state contract

UI chỉ được hiển thị `success` khi condition thành công thực sự được biết.

Nếu request chưa confirm:

- dùng pending/loading;
- preserve input khi recoverable;
- show error/retry khi failure;
- không reset dữ liệu chỉ vì animation đã chạy.

Prototype có thể simulate state nhưng phải được ghi `SIMULATED` trong implementation docs/report.

### 5. Stress data reality

Kiểm component/flow với:

- missing optional data;
- empty result;
- long/short content;
- large result set;
- slow request;
- timeout;
- server error;
- partial response;
- stale/cache mismatch;
- permission denied;
- duplicate submit;
- locale expansion.

Không design chỉ bằng happy-path demo data.

### 6. Production gap assessment

Cho mỗi capability chưa `REAL`, ghi:

| Gap | Current reality | Required for production | Owner/dependency | Severity |
|---|---|---|---|---|

Severity:

- `P0` — false critical behavior/data-loss/security/payment risk;
- `P1` — blocks important journey or trust;
- `P2` — incomplete but safe fallback exists;
- `P3` — optional enhancement.

### 7. Handoff

Route gap đến đúng owner skill:

- API/component implementation → `frontend-implementation` / architecture;
- states/recovery → interaction specialists;
- privacy/security → `security-and-privacy`;
- CMS schema/ownership → `content-governance-and-cms`;
- verification → `testing-strategy`;
- release blocker → `code-review-and-release`.

## Output

Cho substantial work, tạo `docs/system-reality.md` hoặc equivalent:

```md
# System Reality

## Project mode

## Capability matrix

## Data/API/CMS contracts

## Mock/static/simulated inventory

## Production gaps

## Verification evidence

## Unverified dependencies
```

## Quality gate

- [ ] Material capabilities có reality label.
- [ ] Không có false success state.
- [ ] Dynamic flows có loading/empty/error/recovery phù hợp.
- [ ] Mock/static data không bị report như live production data.
- [ ] Unknown backend/API behavior không bị fabricate.
- [ ] Production gaps có severity + owner/dependency.
- [ ] `REAL` chỉ được dùng khi có evidence phù hợp scope.

## Anti-patterns

- `preventDefault()` + success toast rồi gọi form hoàn thiện.
- Hardcode fake metrics/customer/project data vào production path.
- Login UI không backend nhưng report “authentication done”.
- Reset form trước khi biết request thành công.
- Catch mọi error rồi vẫn hiển thị success.
- Mark feature production-ready chỉ vì build pass.

## Completion rule

Không dùng `working`, `integrated`, `live`, `production-ready` cho capability chưa được evidence chứng minh ở mức tương ứng.
