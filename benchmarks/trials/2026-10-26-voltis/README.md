# Thử toolkit trước commit trên VOLTIS

- Loại: `external-project-audit`; đánh giá một prototype có sẵn, không đo khả năng tạo bản UI đầu.
- Target: `Ngh1aa/Voltis`, SHA `bdcd2bd8b768902ff652f50573716d2d5abadac8`, working tree sạch.
- Toolkit: base `46a9314c0d0d8c5be42ff8788a36788dddd85c3a` + thay đổi chưa commit.
- Reviewer: một agent độc lập, `agent-heuristic`; không xem điểm/benchmark cũ trước review.
- Browser: Chromium headless, 390×900 / 1280×900; spot-check header resources tại 320×900.
- Không gửi form thật; backend, thiết bị thật, người dùng thật và native QA chưa kiểm chứng.

## Kết quả thử dự án

14 kiểm tra luồng: **8 PASS, 6 FAIL**. Điều hướng home → vehicles → contact, form invalid/valid
và Back giữ name/topic đã qua. Kết luận cho scope target là **FAIL**; không chấm điểm toàn sản phẩm.

| Vấn đề target | Bằng chứng và nguyên nhân |
|---|---|
| Search resources và filter stories vẫn hiện mọi kết quả | `js/pages.js:26–43` đổi `hidden`, nhưng `.resource-row` / `.story-card` trong `css/pages.css` đặt `display:grid`, thắng style UA của hidden. |
| Chữ lime trên nền sáng khó đọc | `.index-number` lấy `--energy` trên paper/white; contrast đo và đối chiếu render khoảng 1.12–1.20:1. |
| Menu resources ở 320 px chỉ rộng 14 px | Header CTA vẫn hiện do cascade `.btn`, cộng flex shrink của menu. |
| Escape không đóng menu ở trang phụ | `pages.js` thiếu handler mà home đã có. |
| Ảnh showcase sai nội dung | Mapping trong `media-library.js` gán ảnh dịch vụ và macro vật liệu vào hai product panels. |
| Headline home desktop tràn sang ảnh | Measure/cột hẹp và font display lớn; cần sửa đúng layout owner. |
| Back mất filter stories | State filter chưa được phục hồi cùng history/pageshow. |

Đã mở ảnh top home, vehicles, contact, resources ở hai cỡ; mở thêm ảnh cận cảnh control/content
liên quan. Chưa review mọi vùng của mọi route, không tuyên bố all-route visual PASS.

## Những gì thử nghiệm tìm ra trong toolkit

- Full-bleed section/header/footer bị tính như card: đã phân biệt vùng bố cục và card, có test
  âm chứng minh hai card thật vẫn bị bắt.
- Request ảnh cũ bị hủy khi runtime thay nguồn: đã đối chiếu nguồn ảnh hiện tại; cảnh báo khi
  ảnh cũ không còn lỗi, vẫn fail nếu nguồn hiện tại bị hủy. Có test cả hai nhánh.
- Heading xuống dòng bị gọi là nhãn lỗi: heading/nội dung được ghi cảnh báo để review; nhãn
  điều khiển ngắn gãy dòng vẫn là lỗi. Không đổi layout target để qua bộ soát.

Chạy lại cùng 3 route index/contact/resources, 390/1280 light + reflow320: axe đã chạy;
53 tín hiệu lỗi và 64 cảnh báo. Số đếm không phải số bug: detector vẫn cần người đọc tách ticker
clip có chủ đích, card ở các section khác nhau và các tín hiệu có ngoại lệ theo brief.

## Bằng chứng và giới hạn

Gói evidence giao kèm lượt làm việc có report độc lập, JSON của 14 flow checks, computed styles,
ảnh cận cảnh, kết quả bộ soát trước/sau, diff và source manifest chứa SHA256. Target giữ nguyên;
không chép source hoặc asset của khách vào toolkit. Đây là audit bằng agent, không phải user test.

Smoke-test riêng `benchmarks/run.cjs` trên bản sao v2: landing/app qua với axe; dashboard cũ
bị phát hiện `aria-prohibited-attr` trên panel trạng thái, runner thoát lỗi đúng. Không sửa ảnh,
điểm hay kết quả lịch sử để che lỗi; bảng [REPORT](../../REPORT.md) chỉ thể hiện kết quả ghi nhận
trong điều kiện lúc chạy, không chứng minh bản cũ đạt kiểm tra hiện tại.
