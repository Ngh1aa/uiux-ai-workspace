# Bộ đề chuẩn

Các đề cố định để biết repo có thật sự giúp ra thiết kế tốt hơn sau mỗi lần nâng cấp hay không,
chứ không chỉ dày thêm. Kết quả mọi lần chạy nằm trong [`REPORT.md`](REPORT.md).

| Đề | Loại | Cỡ |
|---|---|---|
| [01 Landing xưởng gốm](briefs/01-landing.md) | Website một trang | M |
| [02 App đặt sân cầu lông](briefs/02-app.md) | App 5 màn | L |
| [03 Dashboard kho shop len](briefs/03-dashboard.md) | Trang quản trị | M |
| [04 Web app phòng khám, ba vai trò](briefs/04-multi-role.md) | Web app desktop 4 màn | L |
| [05 App sổ liên lạc iOS và Android](briefs/05-native.md) | App native 4 màn × 2 nền tảng | L |

## Quy tắc

- **Đề thêm sau** ghi dòng `**Thêm vào:** YYYY-MM-DD`; lần chạy trước ngày đó không bắt buộc có đề
  này, lần chạy từ ngày đó phải làm đủ.
- **Không sửa đề.** Đề có sẵn nội dung và số liệu để mọi lần chạy so được với nhau. Muốn đổi
  đề thì tạo đề mới với số mới, giữ đề cũ.
- Làm đề đúng như làm việc thật: theo [`START-HERE.md`](../START-HERE.md), không nhìn lần chạy trước.
- Ghi rõ ai chấm: `agent-heuristic` khi agent tự chấm, `expert-review` khi người ngoài chấm.
- Ghi `protocol` trong `scores.json`: `kind` là `fresh` (làm từ đầu, không xem lời giải cũ),
  `iterative-repair` (sửa tiếp, bắt buộc có `parent_run`) hoặc `legacy-unknown` (lịch sử thiếu
  bằng chứng). Ghi `author_id`, `reviewer_id`, `independent_review` đúng thực tế. Tự chấm vẫn
  hợp lệ nhưng phải ghi `false`; agent ở phiên độc lập vẫn là `agent-heuristic`.
- `repo_commit` là SHA đầy đủ của toolkit. `run.cjs` ghi SHA, trạng thái working tree và hash
  checker vào `checks.json`; lưu diff/manifest khi thử trước commit. Không suy đoán SHA lịch sử:
  dùng `null` kèm `protocol.legacy_note` và hiển thị UNKNOWN.
- Lượt sửa tiếp đo khả năng cải tiến mẫu cũ. Để so chất lượng bản đầu, chạy lượt `fresh` với
  cùng đề, nội dung, assets, viewport và điều kiện công cụ; dùng người chấm độc lập khi có.

## Chạy một lần mới

1. Tạo thư mục `runs/<ngày>-v<n>/` và làm từng đề vào `<đề>/index.html`.
2. Soát và chụp ảnh (cần Playwright):

   ```sh
   node benchmarks/run.cjs benchmarks/runs/<ngày>-v<n>
   ```

   Lượt mới soát 390/1024/1280/1440px sáng/tối, reflow 320px; đề 04 thêm layout strict.
   Runner giữ riêng render và flow. Tạo `flow.browser.cjs --json <file>` chạy Playwright thật,
   xuất `briefs.<đề>.status` và `scenarios: [{name, status}]`; thiếu scenario là UNKNOWN.
   Native của đề 05 vẫn UNKNOWN khi chỉ chạy browser.
3. Muốn ghi `independent_review: true`, đóng gói ảnh trong `shots/` bằng
   `python3 scripts/review-packet.py make` và để người duyệt độc lập chấm theo
   [hướng dẫn duyệt độc lập](../skills_UIUX/design-critique-and-rationale/references/independent-review.md).
   Mở ảnh ra xem, chấm theo [rubric](../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md)
   và ghi `scores.json` (mẫu: [lần chạy đầu](runs/2026-10-24-v1/scores.json)). Ghi thêm `NOTES.md`:
   lỗi bắt được trong lúc làm, repo được sửa gì, việc nên làm tiếp.
   `checks.json` phiên bản 2 tách render, flow tĩnh và browser; flow tĩnh không chứng minh runtime.
   Độc lập cần từng đề có `review: {path, sha256}` trỏ review.json, reviewer/điểm khớp kết quả thật,
   ảnh thuộc lần render đã ghi hash, brief/rubric không bị đổi. Agent độc lập vẫn là heuristic.
   `source.repo_commit` chỉ là HEAD baseline; `provenance/local.patch`, manifest và hash sample/assets/test
   nhận diện phần local chưa commit. Không lấy SHA baseline gán cho code mới.
4. Cập nhật bảng tổng hợp:

   ```sh
   python3 benchmarks/report.py
   ```

5. Giữ nguyên ảnh và điểm các lượt lịch sử. Runner từ chối ghi đè v1/v2; lượt local chưa review
   có thể chạy lại với `--refresh`. Khi đã có review, tạo revision mới để giữ bằng chứng đã duyệt.
   Ảnh state chỉ tạo từ browser scenarios được ghi riêng trong `shots/behavior/`; ảnh initial không chứng minh coverage toàn bộ màn.

## Chấm lại theo gu chủ repo (2026-10-30)

Sau khi TASTE được bổ sung và checker có luật mới, hai lượt 2026-10-29 được soát và chấm lại:
**0/10 bài đạt theo TASTE** (bảng cũ ghi 8/10 Đạt). Chi tiết, bằng chứng và các chỗ checker còn bỏ sót ở
[evidence/2026-10-30](evidence/2026-10-30/README.md). Điểm cũ trong `REPORT.md` giữ nguyên làm lịch sử; lượt
mới phải đạt theo TASTE hiện tại.

## Đọc kết quả thế nào

- *Lỗi soát* phải bằng 0. Đây là mức sàn, không phải bằng chứng đẹp.
- *Ngưỡng* đạt khi render và luồng bắt buộc PASS, không hard fail, rubric đạt cỡ việc.
  Luồng FAIL hoặc UNKNOWN chặn kết luận Đạt; lịch sử không có flow hiển thị UNKNOWN mà không sửa điểm cũ.
- Điểm do agent tự chấm thường cao hơn thực tế. So **xu hướng** giữa các lần chạy, đừng coi một
  con số là kết luận.

## Thử trên dự án bên ngoài

Thử một repo khách hàng có sẵn là một **external-project-audit**, không phải lượt `fresh` của
ba đề trên và không đo khả năng tạo UI mới. Giữ code khách riêng, ghi exact target SHA và toolkit
SHA + diff/hash nếu chưa commit, liệt kê route, viewport, kịch bản, evidence, PASS/FAIL/UNKNOWN.
Phân biệt lỗi của target, lỗi bộ soát và giới hạn môi trường. Không chép source/asset của khách
vào repo này. Review độc lập theo `START-HERE.md`; không gọi đó là test với người dùng thật.
