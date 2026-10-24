# Bộ đề chuẩn

Ba đề cố định để biết repo có thật sự giúp ra thiết kế tốt hơn sau mỗi lần nâng cấp hay không,
chứ không chỉ dày thêm. Kết quả mọi lần chạy nằm trong [`REPORT.md`](REPORT.md).

| Đề | Loại | Cỡ |
|---|---|---|
| [01 Landing xưởng gốm](briefs/01-landing.md) | Website một trang | M |
| [02 App đặt sân cầu lông](briefs/02-app.md) | App 5 màn | L |
| [03 Dashboard kho shop len](briefs/03-dashboard.md) | Trang quản trị | M |

## Quy tắc

- **Không sửa đề.** Đề có sẵn nội dung và số liệu để mọi lần chạy so được với nhau. Muốn đổi
  đề thì tạo đề mới với số mới, giữ đề cũ.
- Làm đề đúng như làm việc thật: theo [`START-HERE.md`](../START-HERE.md), không nhìn lần chạy trước.
- Ghi rõ ai chấm: `agent-heuristic` khi agent tự chấm, `expert-review` khi người ngoài chấm.

## Chạy một lần mới

1. Tạo thư mục `runs/<ngày>-v<n>/` và làm từng đề vào `<đề>/index.html`.
2. Soát và chụp ảnh (cần Playwright):

   ```sh
   node benchmarks/run.cjs benchmarks/runs/<ngày>-v<n>
   ```

   Lệnh này soát 390px, 1024px và 1280px, cả sáng và tối, rồi ghi `checks.json` và ảnh vào `shots/`.
3. Mở ảnh ra xem, chấm theo [rubric](../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md)
   và ghi `scores.json` (mẫu: [lần chạy đầu](runs/2026-10-24-v1/scores.json)). Ghi thêm `NOTES.md`:
   lỗi bắt được trong lúc làm, repo được sửa gì, việc nên làm tiếp.
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
