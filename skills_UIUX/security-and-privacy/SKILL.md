---
name: security-and-privacy
description: |
  Security/privacy baseline cho website và web app theo risk: data minimization, trust boundaries,
  validation/encoding, auth/session/access control, secrets, uploads, third parties, browser/server
  protections và privacy-by-design. Dùng khi có form, API, auth, personal data, payment, uploads,
  analytics hoặc production release; không dùng checklist cơ bản để claim compliance/security.
---

# Security & Privacy

## Principle

Security là risk discipline, không phải copy một bộ header hoặc regex vào mọi stack.

`assets/data/actors → trust boundaries → threats/misuse → controls → verification → residual risk`

Khi cần requirements/verification chi tiết và web access khả dụng, ưu tiên OWASP ASVS + relevant OWASP Cheat Sheet phiên bản hiện hành thay vì hardcode lời khuyên có thể lỗi thời.

## Scope first

Xác định trước:

- project mode: prototype / production-candidate / production;
- data collected/stored/transmitted;
- authentication/authorization;
- money/payment;
- uploads/user-generated content;
- external APIs/webhooks;
- analytics/marketing/third-party scripts;
- deployment/server/CDN capability;
- legal/market requirements đã được project xác nhận.

Không invent legal obligation. Nếu jurisdiction/requirement chưa biết, ghi `UNKNOWN / REQUIRES LEGAL REVIEW`.

## Data inventory & minimization

Cho material data:

| Data | Purpose | Required? | Source | Destination | Retention | Access | Risk |
|---|---|---|---|---|---|---|---|

Rules:

- chỉ collect dữ liệu phục vụ mục đích rõ;
- không đưa PII/sensitive form content vào analytics/logs vô cớ;
- không lưu sensitive data ở client storage nếu threat model không cho phép;
- production logging phải tránh secrets/tokens/full sensitive payloads;
- retention/deletion phải theo project/policy, không tự bịa timeline.

## Trust boundaries

Đừng coi client validation là security boundary.

Phân biệt:

```text
browser/client
server/API
identity provider
CMS/database
third-party service
analytics/marketing
storage/CDN
```

Mỗi boundary cần biết input nào đi qua, ai kiểm soát và control nằm ở đâu.

## Input, output and injection safety

- Validate input theo schema/business rule ở server/trusted boundary khi server tồn tại.
- Client validation phục vụ UX, không thay server validation.
- Prefer safe DOM/framework APIs; avoid raw HTML injection.
- Nếu phải render untrusted HTML, dùng sanitizer đã được duy trì và policy phù hợp context.
- Encode/escape theo output context; không giả định một sanitizer giải quyết mọi context.
- Validate URLs/redirect destinations theo allowlist/expected scheme khi user-controlled.
- Không dùng `eval`/dynamic code execution với untrusted input.

Không dùng regex demo như bằng chứng rằng email/phone/URL/security validation đã “đúng chuẩn”.

## Request/session/auth/access control

Khi applicable:

- authentication state phải đến từ trusted identity/session source;
- authorization phải kiểm server-side/trusted boundary, không dựa vào hidden UI;
- review CSRF protection theo authentication/cookie/request model;
- session/token lifecycle: storage, expiry, rotation/revocation, logout;
- destructive/high-value actions cần re-auth/confirmation khi risk justify;
- rate/abuse protection nằm ở server/edge/service phù hợp, không phải chỉ disable button ở client;
- error messages không leak sensitive internals.

Không thêm một control chỉ vì checklist nếu architecture không dùng threat tương ứng.

## Forms and submissions

Với form có backend:

- truthful pending/success/error/retry states;
- prevent accidental duplicate submit nhưng không coi đó là rate limiting;
- server-side validation/error handling;
- abuse/spam mitigation phù hợp risk;
- data-use/privacy context gần nơi collect khi project/legal requirement cần;
- preserve recoverable input khi submission fail.

Route `system-reality-and-production-readiness` nếu endpoint/service chưa được verify.

## Uploads / user-generated content

Nếu có upload:

- explicit allowed types/use cases;
- size/count limits;
- validate content/type ở trusted boundary;
- safe naming/storage/location;
- authorization for read/write/delete;
- malware/content scanning khi risk/system capability yêu cầu;
- do not execute/serve untrusted files in unsafe context.

Chi tiết implementation phụ thuộc stack; tham chiếu current OWASP guidance khi thực thi.

## Secrets and configuration

- Không commit secrets/tokens/private keys.
- Không expose server secrets vào client bundle/public env.
- Use deployment secret management/environment config phù hợp platform.
- Nếu secret có dấu hiệu đã leak, việc xóa file không đủ: mark for rotation/revocation và history review.
- Không tự động sửa/xóa `.env` của user nếu không được yêu cầu; report exposure risk rõ.

## Browser/server protections

Security headers/config phải theo deployment architecture và current browser guidance.

Review khi applicable:

- HTTPS/HSTS deployment policy;
- CSP;
- frame embedding / `frame-ancestors`;
- content-type sniffing protection;
- referrer policy;
- permissions policy;
- secure cookie attributes;
- CORS policy;
- cache behavior cho sensitive pages;
- SRI chỉ khi phù hợp với external static resource workflow.

Không copy một CSP/header block mẫu rồi gọi secure. Một CSP dùng inline exceptions rộng có thể chỉ là migration step, không phải end-state proof.

## Third-party risk

Inventory:

| Service | Purpose | Data shared | Execution privilege | Failure impact | Alternative/mitigation |
|---|---|---|---|---|---|

Review:

- có thật sự cần third party không;
- data nào rời hệ thống;
- script chạy privilege gì trong page;
- consent/policy requirement đã được project xác định chưa;
- loading failure ảnh hưởng critical journey thế nào;
- dependency compromise/update model.

## Privacy UX

Privacy copy phải truthful và match actual behavior.

Không viết “chúng tôi chỉ dùng email để phản hồi” nếu hệ thống còn gửi CRM/marketing/analytics mà chưa xác nhận.

Consent:

- không preselect/obscure choice khi consent thật sự cần;
- reject non-essential tracking before required consent khi applicable;
- withdrawal/preferences phải usable nếu policy yêu cầu;
- legal/compliance claim cần qualified review, không suy từ UI.

## Verification

Chọn theo risk/scope:

- code/config inspection;
- dependency/secret scanning nếu tooling có;
- auth/access-control tests;
- invalid/malicious-input boundary tests ở safe test environment;
- CSP/header verification trên deployed environment;
- privacy/data-flow review;
- OWASP ASVS-based review cho production/high-risk applications.

Automation/tool scan hỗ trợ evidence nhưng không chứng minh application “secure”.

## Output

Cho substantial production work, tạo `docs/security-privacy.md` hoặc equivalent:

```md
# Security & Privacy
## Scope / system boundaries
## Data inventory
## Material risks
## Controls implemented
## Verification evidence
## Third-party inventory
## Unverified / residual risks
## Requires legal/security review
```

## Quality gate

- [ ] Scope/data/trust boundaries được hiểu ở mức phù hợp.
- [ ] Client-only controls không bị report như server security.
- [ ] No known secrets exposed in changed code.
- [ ] Auth/access controls nằm đúng trusted boundary khi applicable.
- [ ] Untrusted input/output handling có rationale theo context.
- [ ] Privacy statements không vượt quá actual behavior/evidence.
- [ ] Third-party/data-sharing material được xem xét.
- [ ] Verification + residual risks được báo trung thực.

## Claim discipline

Không nói `secure`, `OWASP compliant`, `GDPR compliant`, `privacy compliant` hoặc tương tự nếu chưa có assessment phù hợp exact scope/standard/jurisdiction.
