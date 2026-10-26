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

   Lệnh này soát 390px, 1024px và 1280px, cả sáng và tối, rồi ghi `checks.json` và ảnh vào `shots/`.
3. Muốn ghi `independent_review: true`, đóng gói ảnh trong `shots/` bằng
   `python3 scripts/review-packet.py make` và để người duyệt độc lập chấm theo
   [hướng dẫn duyệt độc lập](../skills_UIUX/design-critique-and-rationale/references/independent-review.md).
   Mở ảnh ra xem, chấm theo [rubric](../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md)
   và ghi `scores.json` (mẫu: [lần chạy đầu](runs/2026-10-24-v1/scores.json)). Ghi thêm `NOTES.md`:
   lỗi bắt được trong lúc làm, repo được sửa gì, việc nên làm tiếp.
   `checks.json` chỉ là soát render. Bấm thử các luồng chọn/nhập → xác nhận → quay lại sửa;
   ghi kết quả chức năng riêng, không nâng thành PASS chỉ vì ảnh hay điểm rubric tốt.
4. Cập nhật bảng tổng hợp:

   ```sh
   python3 benchmarks/report.py
   ```

5. So ảnh trong `shots/` với lần chạy trước. Repo chỉ lưu ảnh chế độ sáng ở 390px và 1280px; các
   ảnh khác chạy lại `run.cjs` là có.

## Đọc kết quả thế nào

- *Lỗi soát* phải bằng 0. Đây là mức sàn, không phải bằng chứng đẹp.
- *Ngưỡng* đạt khi không có hard fail, điểm trung bình và điểm thấp nhất đạt mức của cỡ việc.
- Điểm do agent tự chấm thường cao hơn thực tế. So **xu hướng** giữa các lần chạy, đừng coi một
  con số là kết luận.

## Thử trên dự án bên ngoài

Thử một repo khách hàng có sẵn là một **external-project-audit**, không phải lượt `fresh` của
ba đề trên và không đo khả năng tạo UI mới. Giữ code khách riêng, ghi exact target SHA và toolkit
SHA + diff/hash nếu chưa commit, liệt kê route, viewport, kịch bản, evidence, PASS/FAIL/UNKNOWN.
Phân biệt lỗi của target, lỗi bộ soát và giới hạn môi trường. Không chép source/asset của khách
vào repo này. Review độc lập theo `START-HERE.md`; không gọi đó là test với người dùng thật.
