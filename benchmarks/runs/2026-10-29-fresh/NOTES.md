# Fresh benchmark 29/10/2026

Nguồn: baseline d7000758c2e2aa273785455ae91d255fe3be04e0; đủ 5 brief trong benchmarks/briefs. Agent thực hiện chưa mở runs cũ, ảnh cũ, scores, checks hoặc REPORT cũ. Chỉ tham khảo cấu trúc starter, fonts, token/component/pattern nguồn và skill được WORKFLOWS định tuyến. Không có nghiên cứu người dùng hoặc phê duyệt thật.

## Kế hoạch thị giác trước khi dựng

| Đề | Vật gốc và cảm giác | Chữ, hình khối | Màu theo vai trò | Lưới/mật độ và điểm nhìn | Ba khác biệt starter |
|---|---|---|---|---|---|
| Đất Nung | Vòng bàn xoay; chậm, thủ công | Source Serif 4 72/1.1 cho display, Be Vietnam Pro 16/1.6; bo 12px, nét mảnh | Nền #f4f3ef, mặt #ffffff, chữ #242d2c, brand #354f4a, nhấn men #c7a966 | Desktop 7+5 hero, hàng lớp so sánh, mobile xếp dọc; thoáng; cốc SVG tự vẽ | Chữ có chân lớn, bản vẽ bàn xoay, bảng lớp dạng phiếu |
| Cầu Lông Gần Nhà | Vạch sân; nhanh, dứt khoát | Be Vietnam Pro 32/1.2, thân16/1.5; bo10px | Nền #f2f5f1, mặt trắng, chữ #1e2923, brand #246444, nhấn #d5e7a0 | Phone390, 1 cột; vừa; vé lịch tiếp theo ba tầng | Vé đặt sân, chọn giờ dạng ô sân, số giờ lớn |
| Len Nhỏ | Cuộn len và phiếu xuất; gọn, rõ việc | Be Vietnam Pro 30/1.2, thân15/1.6; bo12px | Nền #f5f2f5, mặt trắng, chữ #332c35, brand #704364, cảnh báo #8c3a2e | Rail + 12 cột; bảng8/đơn4 rồi biểu đồ; gọn; ngoại lệ nhập hàng 2 ngày | Bảng tồn kho có thanh đủ bán, hàng đơn xử lý trước, chart số trực tiếp |
| Răng Xinh | Phiếu hẹn; dịu, chính xác | Be Vietnam Pro 30/1.2, thân15/1.6; bo12px | Nền #f1f6f7, mặt trắng, chữ #24343a, brand #116776, lỗi #943a36 | Sidebar + lịch8/chi tiết4; gọn; lịch từng ghế là quyết định đầu tiên | Lịch theo ghế, phân quyền theo vai, banner dị ứng không lẫn điều trị |
| Nhà Trường | Trang vở và thời khoá biểu; rõ, gần gũi | Be Vietnam Pro theo vai chữ 34 iOS/28 Android, thân16/1.6; iOS nhóm12px, M3 dialog28px | Nền #f3f5fa, mặt trắng, chữ #27334b, brand #3c5c93, lỗi #943a36 | Phone390, 1 cột; vừa; 2 bài cần nộp | iOS nhóm danh sách và sheet, Android tonal surfaces/fullscreen form, bảng lịch thay hero |

Đối chiếu CRAFT: không ảnh mạng; không emoji/icon giả; không gradient tím; không card kéo giãn để lấp khung; card nổi bật có nhãn + việc chính + hành động/ngữ cảnh. Source Serif 4 dùng vì hướng thủ công, nạp offline từ pairs.css do parent thêm trong phiên; Be Vietnam Pro có bộ tiếng Việt local từ design-system. Chế độ tối dùng surface/foreground cùng cặp token.

## Cổng duyệt hướng

CHƯA DUYỆT. Đây là benchmark không có người duyệt. So sánh ở mức phương án: landing editorial lệch so với danh mục ảnh (chọn editorial vì cấm ảnh); app vé lịch so với bản đồ (chọn vé vì không có toạ độ); kho bảng ngoại lệ so với dashboard KPI (chọn bảng); nha lịch ghế so với feed thời gian (chọn lịch ghế); giáo dục grouped list so với feed thẻ (chọn grouped list). Hai hướng A/B đã dựng thực trong cùng HTML bằng query ?direction=alternate. Ảnh đối chiếu ở shots/directions/, 390 và1280px, cùng dữ liệu. Hướng A được agent tự chọn, CHƯA DUYỆT.

## Nguồn dữ liệu và giới hạn

Tất cả tên/số liệu từ brief là dữ liệu minh hoạ. Các thao tác đặt chỗ, đặt sân, nhập hàng, gửi đơn, khám và xin nghỉ chỉ thay đổi state trong trình duyệt, không có backend, thanh toán, SMS hay hồ sơ thật. Reset bằng tải lại. Ngày học của Nhà Trường cố định 22/10/2025 để lịch thứ Năm 23/10 và thứ Hai 27/10 khớp brief; không dùng thời gian hệ thống hiện tại. App sân giữ nguyên lượt thứ Sáu 24/10 trong brief; lịch demo tối nay dùng ngữ cảnh đề bài, không tuyên bố lịch hiện tại.

Răng Xinh: brief không có chuỗi doanh thu từng ngày trong tháng. Không bịa chuỗi để vẽ chart; panel công khai thiếu dữ liệu, hiện tổng tháng đã cho và mốc so sánh. Ghế 3 có lịch thực tế nhưng chưa đủ 7 ngày phân tích; hai điều này cùng tồn tại.

## Ma trận quyền Răng Xinh

| Vai trò | Lịch hôm nay/đặt lịch | Bệnh án/ghi chú/khám | Doanh thu và lấp ghế | Đổi vai |
|---|---|---|---|---|
| Nguyễn Thảo, lễ tân | Có | Không | Không; URL ép mở trả màn không quyền và không render số tiền | Có, mô phỏng |
| BS. Phan Minh Đức | Có quyền xem | Có, bệnh nhân của BS. Đức | Không | Có, mô phỏng |
| Lê Quỳnh Anh | Có quyền xem | Không | Có | Có, mô phỏng |

Đổi vai trong demo không phải authentication/authorization backend. Quyền UI được chặn cả URL/sự kiện điều hướng; không dùng CSS để giấu số liệu đã render trong DOM.

## Hai nền tảng Nhà Trường

iOS: title lớn, text-back, inset grouped list, form sheet có Huỷ/Gửi, destructive alert. Android: top app bar64px, mũi tên Up, nav có indicator pill, surface tonal, form toàn màn, dialog28px. Cùng thứ tự dữ liệu và payload form; min hit44/48. Photo upload dùng file input ảnh browser, trạng thái gửi chỉ mô phỏng sau khi chọn tệp; không mở camera native. Native implementation, Dynamic Type thực, font scale Android200%, VoiceOver, TalkBack, predictive back, swipe-dismiss native: UNKNOWN. Browser zoom/reflow có thể kiểm riêng nhưng không thay các mục native.

## Verification

flow.browser.cjs là assertions browser riêng, ghi kết quả vào flow-results.json và ảnh trong captures/. Independent review được parent phối hợp; agent dựng không tự nhận review độc lập. Self review và tool output không là nghiên cứu/human approval. Chưa phát hành, không commit/push/PR.

### Kết quả tự kiểm trước khi giao parent

- `flow.browser.cjs --json flow-results.json`: PASS browser 5/5, có assertions trên dữ liệu, tổng tiền, back/edit, lỗi/khôi phục và phân quyền. Native vẫn UNKNOWN. School đã thử browser Back từ chi tiết về Hôm nay, bên cạnh nút Up/Back hiển thị.
- `taste-check`: 01,02,03,05 ở390/1280px light/dark đều0 lỗi0 cảnh báo, axe-core đã chạy. 04 ở1280/1440px, height900, `--layout strict`, cả hai theme:0 lỗi0 cảnh báo, axe-core đã chạy. Đây là initial visible screens, không tự suy ra mọi dynamic state đã qua axe/contrast check.
- Ảnh final do flow tạo ở `shots/behavior/` (initials, form review, lỗi19:00, lịch kết quả, các màn động light/dark) và `shots/directions/` (A/B,390/1280). `BENCHMARK_SHOTS` cho phép chuyển toàn bộ ảnh về thư mục tạm trong CI. Ghi chú `captures/` ở đoạn trên chỉ mô tả loại đầu ra; đường dẫn thực là hai thư mục shots này.
- Đã mở xem ảnh representative: landing toàn trang desktop light và mobile dark; app trang chủ light/dark, chi tiết dark, lỗi và lịch; dashboard desktop light/mobile dark; nha lịch light/dark, conflict, doctor và owner; native hai chrome desktop light/dark, iOS sheet và Android dialog dark. Cả5 ảnh hướng B đã mở. Không coi xem representative là đã inspect từng pixel ở mọi state/viewport.
- Vòng đầu bắt được Georgia tách dấu tiếng Việt: đã thay bằng Source Serif4 local do parent thêm; accessible-name mismatch của logo/lượt hẹn: đã sửa tại owner. Khung phone ban đầu dài theo nội dung đã đổi về390×844 có vùng nội dung cuộn, nav tách riêng; không kéo card để lấp màn. Form iOS giữ Huỷ/Gửi sticky khi cuộn.
- Các ảnh taste tạm trước sửa đã được giữ ngoài repository tại thư mục work/fresh-qa-history-2026-10-29 của workspace; không đưa vào shots final.

### Tự phản biện theo vai, không phải review độc lập

Người mới trên điện thoại: tác vụ chính có nút rõ; dashboard dùng hàng tồn kho/đơn có số chứ không để ba KPI thay tác vụ. Native cần cuộn để thấy đơn đã gửi; tab Xin nghỉ luôn có ở Hôm nay. Lễ tân thấy quick action10:30 Ghế1 trống ở đầu trang dù lịch dài hơn một viewport.

Trợ năng: browser checker kiểm initial axe/contrast; form date có lỗi cụ thể và giữ input, control chuẩn có focus-visible. Chưa thử VoiceOver/TalkBack, switch control, thiết bị thật hay phóng chữ native200%. Chưa hoàn tất thử toàn bộ thứ tự bàn phím của mọi ô lịch/form bằng automation; không gọi keyboard all-path PASS.

Design-system owner: tái sử dụng fonts, generated tokens, `.ds-button` và bộ SVG icons của repo; thêm semantic palette/surface/foreground ở owner `assets/ui.css`, brand composition riêng mỗi đề. Hướng B chỉ là phương án đánh giá: landing đặt vật gốm lên trước, app ưu tiên tìm sân, dashboard đưa doanh thu lên trước, nha dùng agenda, school ưu tiên lịch ngày mai. Chọn A vì các tác vụ của brief lần lượt là hiểu/đặt lớp, xem lượt sắp tới rồi tìm sân, xử lý ngoại lệ kho, xem trống theo ghế, và nộp bài trước hạn. Tất cả vẫn CHƯA DUYỆT.

## Tích hợp và sửa regression sau lượt tạo mới

Người tạo là agent fresh_benchmark với context sạch, không xem lời giải cũ. Sau freeze, parent sửa kỹ thuật ở 320/1024px theo checker: ticket time co theo không gian, bảng kho đổi layout trung gian và loại min-width gây tràn, lịch nha khoa mobile thành danh sách rõ giờ/ghế với chữ13–15px. Parent không tạo lại từ lời giải lịch sử. Font Source Serif4 được thử/đóng gói ở toolkit; hướng được chọn và alternatives nằm trong assets/directions.css và shots/directions. Đây là lượt tạo mới có vòng sửa regression minh bạch, không gọi là bản đầu chưa sửa.
