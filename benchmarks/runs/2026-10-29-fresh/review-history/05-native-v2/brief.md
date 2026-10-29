# Đề 5: App sổ liên lạc "Nhà Trường", bản iOS và Android, 4 màn mỗi nền tảng

**Thêm vào:** 2026-10-26

**Cỡ việc:** L (một luồng trên hai nền tảng). **Ngưỡng rubric:** không hard fail, trung bình ≥ 4.0,
không chiều nào < 3.5.

## Bối cảnh

App sổ liên lạc cho phụ huynh tiểu học ở Đà Nẵng. Phụ huynh mở app buổi tối để xem con hôm nay học gì,
còn bài nào chưa nộp, và xin phép nghỉ khi con ốm. Khoảng 60% phụ huynh dùng Android máy tầm trung, 40%
dùng iPhone. Nhiều người đặt cỡ chữ hệ thống lớn.

**Việc chính:** xem tóm tắt hôm nay của con, nộp đơn xin nghỉ, huỷ đơn đã gửi nhầm.

## Bốn màn bắt buộc, làm cho cả iOS và Android

1. **Hôm nay:** con là ai, lớp nào; số bài chưa nộp; lịch học ngày mai; thông báo mới nhất của cô.
2. **Chi tiết bài tập:** tên bài, môn, hạn nộp, mô tả, trạng thái nộp, nút nộp ảnh bài làm.
3. **Xin nghỉ:** form chọn ngày, buổi (sáng, chiều, cả ngày), lý do, ghi chú cho cô. iOS mở trong
   sheet, Android mở toàn màn. Thể hiện **trạng thái lỗi**: chọn ngày đã qua.
4. **Huỷ đơn:** xác nhận huỷ đơn xin nghỉ đã gửi. iOS dùng alert, Android dùng hộp thoại.

## Dữ liệu (dùng đúng)

- Học sinh: Trần Gia Hân, lớp 2/3, Trường Tiểu học Minh hoạ, cô chủ nhiệm Lê Thu Hà.
- Bài chưa nộp: "Tập đọc: Cây dừa" (Tiếng Việt, hạn thứ Năm 23/10, 20:00), "Bài 14: Phép cộng có nhớ"
  (Toán, hạn thứ Sáu 24/10, 20:00).
- Lịch ngày mai, thứ Năm 23/10: Tiếng Việt, Toán, Tự nhiên và Xã hội, Âm nhạc; tan học 16:30.
- Thông báo mới nhất: "Thứ Bảy 25/10 trường tổ chức ngày hội đọc sách, phụ huynh đăng ký tham gia
  trước thứ Năm." (cô Hà, 19:12 hôm nay).
- Đơn đã gửi: nghỉ cả ngày thứ Hai 27/10, lý do "Đi khám răng".

## Yêu cầu

- Khung 390 × 844 cho cả hai. Mỗi nền tảng giữ chrome riêng: iOS (tiêu đề lớn, quay lại bằng nút chữ,
  danh sách nhóm, tab bar), Android Material 3 (thanh trên có mũi tên, thanh điều hướng có viên chỉ báo,
  nút nổi nếu hợp). Không làm một giao diện chung rồi đổi icon.
- Cùng token, cùng nghĩa, cùng thứ tự thông tin giữa hai nền tảng. Đổi thương hiệu cho hợp giáo dục tiểu học.
- Cả chế độ sáng và tối. Vùng chạm 44 pt (iOS) và 48 dp (Android).
- Ghi trong `NOTES.md`: chỗ nào hai nền tảng cố ý khác nhau và vì sao; điều gì chưa kiểm được trên thiết bị
  thật (Dynamic Type, font scale 200%, TalkBack, VoiceOver).
- Được dùng `design-system/starter/mobile-ios.html`, `mobile-android.html` và `generated/native/`.

## Giao

Một file `05-native/index.html` chứa cả 8 màn, mỗi màn là một phần tử có `data-screen`, tên bắt đầu
bằng `iOS` hoặc `Android`.
