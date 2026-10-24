# Project Instructions — Phase-Aware UI/UX Workflow

Mọi công việc UI/UX trong Project này phải sử dụng bộ skill:
https://github.com/Ngh1aa/skills_UIUX

## QUY TRÌNH KHỞI ĐỘNG

1. Đọc project truth trước: README, AGENTS/project instructions, source code, route, component, token, data/API, build/test/deploy convention và các tài liệu được cung cấp.
2. Từ `skills_UIUX`, với task page/multi-page/whole-site phải đọc tối thiểu:
   - `README.md`
   - `SKILL-CATALOG.md`
   - `website-delivery-pipeline/SKILL.md`
   - `adaptive-skill-routing-and-context-budget/SKILL.md`
   - `project-context/SKILL.md`
3. Resolve phiên bản mới nhất trên `main` tại thời điểm bắt đầu project. Nếu `docs/uiux/Skill-Version-Lock.md` chưa tồn tại, PHASE 1 có authority tạo file này; việc file chưa tồn tại trước PHASE 1 KHÔNG phải blocker.
4. Ghi version, exact commit SHA, ngày kiểm tra và nguồn vào `docs/uiux/Skill-Version-Lock.md`.
5. Các phase sau phải dùng cùng commit SHA đã khóa. Chỉ đổi phiên bản giữa project khi đã review conflict/migration, cập nhật Decision Log và Requirement Coverage Ledger.
6. Trước mỗi phase, phân loại:
   - Scope: `local | component | page | multi-page | journey | whole-site | system`
   - Type: `research | audit | redesign | build | remediation | implementation | QA | release`
   - Risk: `low | medium | high | critical`
   - Mode: `strategy | visual_prototype | interactive_prototype | production_candidate | production`
7. Route smallest applicable skill graph theo scope, phase, risk và mode. Không load toàn bộ skill library.

## SKILL DISCIPLINE

- Trước khi thực hiện, tạo Skill Activation Plan ngắn:
  `Task | Trigger/risk | Skill | Tác động dự kiến | Verification`
- Chỉ ghi một skill là USED khi skill đó đã được đọc và thực sự làm thay đổi decision, code, artifact hoặc verification.
- Với mỗi skill USED, ghi:
  `Skill | Trigger | Requirement áp dụng | Thay đổi tạo ra | Verification | Evidence`
- Không đoán nội dung skill chỉ từ tên.

## SOURCE OF TRUTH

Thứ tự ưu tiên:
1. Yêu cầu hiện tại của user.
2. Project truth và source code thực tế.
3. Design Contract và artifact đã PASS.
4. Skill đã route.
5. Nguồn chính thức, nghiên cứu và reference bên ngoài.

Nếu phát hiện conflict, không silently chọn một phía. Ghi conflict, evidence, quyết định và ảnh hưởng vào Decision Log.
`UNKNOWN` phải giữ là `UNKNOWN`; không tự biến thành fact.

## EVIDENCE DISCIPLINE

Mỗi finding quan trọng phải được label:
`FACT | EVIDENCE_BACKED_INFERENCE | PROFESSIONAL_HYPOTHESIS | ASSUMPTION | UNKNOWN`

Reference phải được label:
`PRODUCTION | CASE_STUDY | CONCEPT | MOOD_REFERENCE | UNKNOWN`

Website giải thưởng/gallery chỉ là nguồn visual craft, không phải bằng chứng UX, conversion hoặc accessibility.

## REQUIREMENT COVERAGE — PHASE-AWARE

- Mọi requirement MATERIAL/APPLICABLE từ user, prompt, Design Contract, routed skills, regression và release phải có ID và `OWNER_PHASE` trong Requirement Coverage Ledger.
- Requirement của regression/release tương lai không được biến thành blocker ở phase hiện tại chỉ vì chưa đến lúc verify.
- Requirement dùng bốn trạng thái:
  - `DONE_VERIFIED`
  - `N/A_JUSTIFIED`
  - `PENDING_FUTURE_PHASE`
  - `BLOCKED`
- `PENDING_FUTURE_PHASE` chỉ dùng khi requirement thực sự applicable nhưng authoritative verification thuộc phase sau. Bắt buộc ghi `OWNER_PHASE`, dependency và verification plan.
- `PENDING_FUTURE_PHASE` không phải PASS giả. Khi đến owner phase, item phải chuyển thành `DONE_VERIFIED`, `N/A_JUSTIFIED` hoặc `BLOCKED`.

### Mapping kết quả skill/gate

- `PASS -> DONE_VERIFIED`
- `N/A` có rationale `-> N/A_JUSTIFIED`
- `FAIL -> BLOCKED` nếu requirement thuộc exit gate/current owner phase.
- `PARTIAL/UNVERIFIED -> BLOCKED` CHỈ KHI verification đó là exit criterion bắt buộc của phase hiện tại.
- `PARTIAL/UNVERIFIED` cho phase sau `-> PENDING_FUTURE_PHASE`.
- `UNKNOWN` fact không tự động là blocker; chỉ `BLOCKED` nếu unknown đó ngăn một material decision/claim/gate của phase hiện tại.

### Phase exit rule

Phase chỉ `PASSED` khi:
- mọi requirement DUE NOW đã được account;
- `current-phase BLOCKED = 0`;
- `current-phase UNACCOUNTED = 0`;
- mọi exit criterion hiện tại có verification + evidence đủ;
- mọi `PENDING_FUTURE_PHASE` có owner phase + verification plan.

Không yêu cầu evidence chỉ có thể tồn tại ở phase tương lai.
Không giữ item ở `PENDING_FUTURE_PHASE` sau khi owner phase đã tới chỉ để manufacture PASS.

## DURABLE PHASE STATE

Mỗi phase phải cập nhật `docs/uiux/Phase-State.md` tối thiểu với:

```yaml
skill_ref: <immutable commit SHA>
phase: <1|2|3|4>
result: <PASSED|BLOCKED|N/A_JUSTIFIED>
project_commit: <SHA or N/A>
due_now_blocked: <count>
due_now_unaccounted: <count>
pending_future_phase: <count>
pending_by_owner:
  phase_2: <count>
  phase_3: <count>
  phase_4: <count>
```

Phase sau đọc `Phase-State.md` thay vì phụ thuộc vào việc câu `PHASE X RESULT = PASSED` còn tồn tại trong chat trước hay không.

## SYSTEM REALITY

Trước khi gọi một feature là hoạt động, phân loại:
`REAL | MOCK | STATIC | SIMULATED | PARTIAL | UNKNOWN`

Không tạo false success state. UI thành công không chứng minh request/API/payment/authentication đã thành công. Mock/simulated không được gọi là production-ready.

## IMPLEMENTATION SAFETY

- Research và Design Contract phải PASS trước khi code đối với redesign/new full-site.
- Inspect trước khi edit; xác định root owner trước khi sửa.
- Reuse trước khi create; extend trước khi duplicate.
- Preserve user changes và behavior ngoài scope.
- Không refactor unrelated code.
- Không patch CSS chồng lớp để che root cause.
- Không dùng destructive git operation hoặc force reset làm rollback mặc định.
- Không merge/deploy khi chưa có release authorization rõ ràng.

## VISUAL VÀ QA

- Build success không thay thế rendered visual QA.
- Screenshot tồn tại nhưng chưa mở và inspect không phải visual evidence.
- Screenshot nhìn lỗi thì build/CI xanh vẫn FAIL.
- Với redesign, OLD/NEW phải cùng viewport và cùng trạng thái có thể so sánh khi baseline khả dụng.
- Không được chỉ đổi font, màu, spacing, radius, shadow, animation hoặc hình ảnh nhưng giữ nguyên hierarchy/composition/journey.
- Không dùng universal hero/layout cho các page role khác nhau.
- Không tuyên bố whole-site redesign nếu primary route còn legacy/drift mà không có rationale.
- Accessibility automated scan không thay thế manual review hoặc formal conformance evaluation.
- Missing rendered evidence chỉ `BLOCKED` khi phase hiện tại đang claim visual completion. Phase 1 có thể để future NEW-render QA ở `PENDING_FUTURE_PHASE`; Phase 2 representative gate và Final QA thì rendered evidence là DUE NOW.

## RESPONSIVE SCOPE

- Responsive scope phải theo Project Config/Design Contract.
- Mặc định của Project này có thể đặt là `desktop_only` nếu user không yêu cầu mobile.
- Nếu `desktop_only`: kiểm tra các desktop viewport/pressure point đã khai báo; mobile/tablet = `N/A_JUSTIFIED`; không tuyên bố fully responsive. Generic mobile guidance không override explicit desktop-only scope.
- Nếu `responsive_all`: phải kiểm tra desktop, tablet, mobile; mobile không được chỉ là desktop stack lại.

## PROJECT MODE

- Không mặc định mọi redesign/build là `production_candidate`.
- Dùng `interactive_prototype` khi mục tiêu chính là design/implementation và chưa có đủ integration/release evidence.
- Chỉ dùng `production_candidate` khi scope thực sự cần production-level verification về integration, security/privacy, performance/browser, release và rollback.

## RELEASE AUTHORIZATION

- Nếu `release_authorization = no_release` và user không yêu cầu release: Phase 4/release = `N/A_JUSTIFIED`; project có thể kết thúc ở Final QA PASSED và không bị coi là BLOCKED.
- Nếu user yêu cầu release nhưng authority cần thiết thiếu hoặc mơ hồ: release action = `BLOCKED`.
- `create_pr_only`: chỉ tạo/kiểm tra PR.
- `merge_only`: chỉ merge sau khi gate/protection/status/review PASS; không deploy ngoài authorization.
- `merge_and_deploy`: merge an toàn, theo dõi deployment và production smoke.

## CONTEXT VÀ TOKEN

- Lưu báo cáo chi tiết vào `docs/uiux/`; chat chỉ báo ngắn gọn outcome, evidence, blocker và file thay đổi.
- Không đọc lại hoặc trình bày lại phase đã PASS, trừ khi phát hiện conflict có bằng chứng.
- Phase sau dùng Design Contract, Requirement Coverage Ledger, Phase-State, Handoff và source hiện tại làm nguồn sự thật.
- Không upload lại source ZIP nếu đã kết nối GitHub.
- Không yêu cầu user đính kèm lại tài liệu đã có trong repo/Project.

## AUTONOMY

- Tự chủ động hoàn thành mọi việc an toàn trong scope với tooling hiện có.
- Không dừng chỉ để báo một lỗi có thể tự sửa.
- Chỉ hỏi khi thiếu lựa chọn business-critical không thể research/resolve hoặc cần thêm authority cho merge/deploy/external write.

Ưu tiên:
`FIX PROJECT > EXPLAIN PROJECT`.
