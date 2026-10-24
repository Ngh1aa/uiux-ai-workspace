# Mẫu giao việc cho người review "người lạ" (vòng 3)

Vòng 3 của [critique 3 vòng](quality-bar-rubric.md#three-round-critique-l-and-xl) chỉ có giá trị khi
người review **chưa thấy quá trình làm**. Người làm không tự chấm vòng này. Có người thật ngoài dự
án thì nhờ người đó (ghi `expert-review`). Không có thì giao cho một agent mới, không chia sẻ lịch sử
trò chuyện, và ghi `agent-heuristic`.

## Chuẩn bị trước khi giao

1. Render mọi màn cần chấm ra file (HTML chạy được hoặc ảnh chụp), đặt trong một thư mục chỉ đọc.
2. Ghi đường dẫn tới: rubric, `TASTE.md`, spec gốc (nếu có), danh sách màn.
3. Không gửi kèm ghi chú thiết kế, lý do chọn phương án hay bản tự chấm. Người review phải tự nhìn.
4. Ghi những điều người review **không được coi là lỗi**: chỗ trống của template (`{{biến}}`), ảnh
   không tải được do chạy cục bộ, dữ liệu giả đã ghi chú.

## Mẫu nội dung giao việc

Chép, thay phần trong ngoặc nhọn, giữ nguyên các mục.

```text
Bạn là người review thiết kế độc lập. Bạn CHƯA thấy quá trình làm. Chấm nghiêm, không nới tay.
Trả lời bằng <ngôn ngữ>.

Đọc trước, theo thứ tự:
- <repo>/TASTE.md
- <repo>/skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md
- <repo>/skills_UIUX/ui-craft-and-visual-qa/references/craft-standards.md
- Spec: <đường dẫn hoặc "không có, chỉ chấm theo rubric">

Màn cần chấm: <thư mục>, <số màn>, cỡ <390px / 1280px>. Mở và NHÌN từng màn
(render bằng Playwright, chụp ảnh, xem ảnh). Không chấm chỉ bằng đọc mã.
Chạy thêm: node <repo>/skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <các file> --root <thư mục> [--screen <selector>]
Không coi là lỗi: <danh sách>.
Không sửa file nào. Lưu ảnh và script của bạn vào <thư mục review mới>.

Giao lại:
1. Kết luận ĐẠT / CHƯA ĐẠT theo ngưỡng cỡ <L>, điểm từng chiều (1–5, một dòng bằng chứng mỗi chiều), trung bình.
2. Hard fail (HF-x) kèm mã màn và bằng chứng, hoặc ghi "không có".
3. Độ phủ spec: từng yêu cầu → đủ / một phần / thiếu, kèm mã màn.
4. Đối chiếu TASTE.md: từng mục → đạt / có lỗi, kèm mã màn.
5. Tối đa 15 vấn đề xếp theo mức (chặn / lớn / nhỏ): mã màn, sai gì, cách sửa cụ thể.
6. Ghi loại bằng chứng: agent-heuristic (không có người dùng thật).
```

## Sau khi nhận kết quả

- Kiểm lại từng phát hiện trên màn thật trước khi sửa. Người review cũng có thể đọc sai, ví dụ đo
  kích thước nhìn thấy mà bỏ qua vùng chạm mở rộng. Phát hiện nào không đồng ý thì ghi lý do.
- Sửa ở đúng tầng: lỗi lặp lại nhiều màn thì sửa component hoặc token, không vá từng màn.
- Báo cho chủ dự án: kết luận, những gì đã sửa, những gì giữ nguyên và vì sao.
