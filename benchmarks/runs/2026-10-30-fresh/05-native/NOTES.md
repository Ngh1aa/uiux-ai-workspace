# 05-native: Nhà Trường, iOS và Android

Cỡ L, track iOS + Android + demo trình duyệt. Hướng thị giác: `CHƯA DUYỆT`.

## Kế hoạch thị giác (CRAFT mục 1)

```text
Ngành và vật gốc:      giáo dục tiểu học; vật gốc là cuốn sổ liên lạc bìa xanh lá và ô lịch ngày trong tuần
Một câu cảm giác:      bình tĩnh, rõ, như sổ liên lạc mở ra buổi tối: con hôm nay thế nào, cần làm gì
Chữ:                   tiêu đề và số Manrope 700 (26–48px, tracking âm); thân Be Vietnam Pro 15–17px, line-height 1.4–1.5; có tiếng Việt: có (đã kiểm glyph Manrope bằng fontTools)
Màu theo vai trò:      nền #f6f8f5, bề mặt #ffffff, chữ #18201c, thương hiệu #1c6a50 (xanh lá sổ), nhấn: chip vàng hổ phách cho "Chưa nộp" từ token feedback-warning; tối nền #0f1411, thương hiệu #8fd4b4
Hình khối:             card 14, control 12, sheet 20; phẳng không bóng; iOS nhóm 10 theo HIG
Bố cục màn chính:      [status 20:41]
                       [tiêu đề lớn "Hôm nay"            Xin nghỉ]
                       [avatar GH  Trần Gia Hân / Lớp 2/3, trường / cô chủ nhiệm]
                       [THẺ NỔI BẬT: Bài chưa nộp  2 bài  hạn gần nhất]
                       [2 dòng bài chưa nộp >]
                       [Ngày mai, thứ Năm 23/10: 4 môn + tan học 16:30]
                       [Thông báo mới nhất của cô Hà]
                       [Đơn xin nghỉ: nghỉ cả ngày thứ Hai 27/10 >]
                       [thanh tab: viên Hôm nay | Bài tập | Đơn nghỉ]
Lưới và mật độ:        1 cột ở 390, lề 16; mật độ vừa; danh sách đơn nghỉ lấp phần cuối
Card nổi bật:          nhãn "Bài chưa nộp"; số lớn "2 bài"; ngữ cảnh "Hạn gần nhất thứ Năm 23/10, 20:00"
Một điểm táo bạo:      con số bài chưa nộp 48px Manrope trên thẻ xanh lá; giảm ngay khi nộp ảnh
Ba điểm khác starter:  1. xanh lá sổ liên lạc thay navy, nền giấy hơi xanh  2. Manrope cho tiêu đề và số  3. chọn ngày nghỉ bằng dải ô ngày như lịch tuần, ngày đã qua tô xám
Đã đối chiếu mục 2:    không eyebrow IN HOA (bỏ kiểu tiêu đề nhóm viết hoa của starter iOS, dùng 15px đậm vừa); không thanh màu trái; không " · "; không emoji; màu thương hiệu chỉ ở thẻ nổi bật, nút chính, viên tab
```

## Hai nền tảng cố ý khác nhau

| Chỗ | iOS | Android | Vì sao |
|---|---|---|---|
| Tiêu đề màn gốc | Tiêu đề lớn 34pt, nút chữ "Xin nghỉ" trên thanh | Thanh trên 64dp, nút nổi mở rộng "Xin nghỉ" | Hành động chính theo quen tay từng nền tảng |
| Quay lại | Nút chữ "‹ Hôm nay" | Mũi tên ← | HIG và Material |
| Danh sách | Nhóm bo 10 trên nền xám, chevron › ở mọi dòng mở được | Dòng 72dp có icon đầu dòng, không chevron | Material không dùng chevron |
| Form xin nghỉ | Sheet có grabber, "Hủy" trái, màn dưới lùi lại | Màn toàn phần, nút ✕ trái | Theo đề |
| Buổi | Segmented control | Nút phân đoạn viền (M3 segmented button) | Control gốc từng nền tảng |
| Lý do, ghi chú | Ô trong nhóm, nhãn là tiêu đề nhóm | Trường viền, nhãn nổi trên viền | Control gốc |
| Nộp ảnh | Action sheet (Chụp ảnh, Chọn từ thư viện, Hủy) | Bottom sheet có icon | Control gốc |
| Huỷ đơn | Alert 270pt hai nút ngang, nút phá huỷ đỏ | Hộp thoại bo 28 có icon, nút chữ căn phải | Theo đề |
| Kết quả | Thẻ trạng thái trong nội dung (iOS không có toast) | Snackbar có "Đóng" | PATTERNS.md |
| Vùng chạm | 44pt (tab, dòng, nút thanh) | 48dp (iconbtn, tab, nút, segmented) | Theo đề |

Giống nhau: token, chữ, thứ tự khối trên Hôm nay, nội dung từng màn, nhãn nút ("Nộp ảnh", "Gửi đơn", "Hủy đơn", "Hủy").

Ngoại lệ có lý do so với chrome gốc (theo TASTE, đứng trên HIG/Material):
- Thanh tab iOS và thanh điều hướng Android đều dùng luật viên của TASTE: tab đang chọn nở thành viên icon trái, nhãn phải; tab khác chỉ icon, nhãn ẩn cho VoiceOver/TalkBack. Vì vậy iOS không có nhãn dưới icon như tab bar gốc.
- Tiêu đề nhóm iOS không viết hoa nhỏ 13pt như HIG; dùng 15px đậm vừa để không thành eyebrow và giữ chữ ≥ 12px.
- Nút "Nộp ảnh" và "Gửi đơn" đặt trên thanh đáy cố định; nội dung có khoảng đệm đáy bằng chiều cao thanh. Màn có thanh hành động không hiện tab bar (màn con đẩy vào).

## Quyết định nội dung

- Thanh tab có ba đích: Hôm nay, Bài tập, Đơn nghỉ. Mỗi tab dẫn tới màn thật (danh sách bài, danh sách đơn). Không thêm tab khác.
- Hôm nay được giả định là thứ Tư 22/10 (ngày mai thứ Năm 23/10 theo đề), giờ máy 20:41. Ngày đã qua để thể hiện lỗi: thứ Ba 21/10.
- Mô tả bài tập ("Đọc to bài Cây dừa ba lần…", "Làm bài 1, 2 và 3…") là chữ giữ chỗ do mình viết, đề không cho mô tả.
- Lý do mẫu "Bị sốt" và các ngày 24/10, 28/10 trong dải ngày là giữ chỗ.
- Mỗi khung là một app độc lập có trạng thái riêng, khởi đầu ở đúng màn cần trình bày; bấm được toàn luồng trong từng khung.

## Kiểm tra

| Điều | Kết quả |
|---|---|
| `taste-check.cjs --width 390 --width 1280 --height 900`, sáng và tối | 0 lỗi, 0 cảnh báo; đã xem ảnh 390 và 1280 sáng/tối |
| `static-check.cjs` | 0 lỗi (cảnh báo IN HOA đến từ CSS dùng chung không dùng trên trang) |
| `flow-check.cjs --mode prototype` | tĩnh PASS, luồng UNKNOWN (thiết kế của checker) |
| `check-brand.py brand.css` | ĐẠT |
| `scenarios.cjs` qua `flow.browser.cjs` (Playwright Chromium thật, 390×844, sáng) | PASS, 12 kịch bản + không lỗi JS |

Sửa sau vòng taste-check đầu: đệm đáy bằng thanh tab/thanh hành động; sheet iOS chỉ giữ thanh tiêu đề màn sau (không còn tab bar dưới lớp phủ); đệm đáy Android đủ cho FAB + thanh điều hướng; tiêu đề thanh trên Android cách mép 16px; ô nhập cao 44–48px; một bán kính card 14px; thân hộp xác nhận là hai dòng dữ liệu (tên đơn, lý do); màn chi tiết thêm khối Bài làm, Giáo viên, Bài chưa nộp khác; màn đơn và form có dòng học sinh, nút Hủy đơn nằm trên thanh đáy.

## Chưa kiểm được (UNKNOWN)

- Dark mode chỉ chạy taste-check và xem ảnh; kịch bản Playwright chỉ chạy chế độ sáng.
- Thiết bị thật: Dynamic Type lớn nhất (AX5), font scale 200% Android, VoiceOver, TalkBack, vuốt mép trái iOS, predictive back Android, máy Android tầm trung.
- Native: chưa dựng SwiftUI/Compose; app thật nên dùng `NavigationStack`, `.sheet`, `.alert`, `confirmationDialog` và `Scaffold`, `NavigationBar`, `AlertDialog`, `ModalBottomSheet` với token trong `design-system/generated/native/`.
- Chọn ảnh, camera và quyền truy cập ảnh chỉ mô phỏng bằng nút; chưa có backend gửi đơn hay nộp bài.
