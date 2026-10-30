# Bộ tham khảo theo loại màn

Trang này trả lời: **khi dựng loại màn này, nên nhìn ai làm tốt, học điều gì, và ghép pattern nào?**
Mỗi dòng nối ba thứ: pattern có sẵn trong [`design-system/patterns/`](../design-system/patterns/README.md),
hệ thống thiết kế công khai có tài liệu tốt cho đúng loại màn đó, và một điều cụ thể cần học từ nó.

Đây là điểm xuất phát, không thay bước tìm tham khảo cho từng dự án. Khi cần tham khảo theo ngành, theo
thương hiệu hoặc cần đối thủ thật, dùng skill
[`design-reference-research-and-benchmark`](../skills_UIUX/design-reference-research-and-benchmark/SKILL.md)
và cách chọn nguồn trong
[`source-strategy.md`](../skills_UIUX/design-reference-research-and-benchmark/references/source-strategy.md).

## Cách dùng

1. Tìm dòng của loại màn đang làm.
2. Mở tài liệu tham khảo, chỉ đọc phần ghi ở cột "Học gì". Ghi một câu vào khối kế hoạch thị giác: học
   điều gì, áp vào vùng nào.
3. Ghép pattern ở cột cuối, rồi chỉnh theo brief. Không chép bố cục nguyên trang.

## Màn app và quản trị

| Loại màn | Tham khảo | Học gì | Pattern |
|---|---|---|---|
| Tổng quan, dashboard | IBM Carbon, *Data visualization* và *Dashboards*; Shopify Polaris, trang Home của admin | Tiêu đề biểu đồ nói luôn kết luận, không thêm dòng phụ; KPI kèm số so sánh kỳ trước; màu nhấn chỉ cho điều cần nói | P01 hoặc P02, P06, P07, P08, P09, P10 |
| Danh sách, bảng quản trị | Carbon, *Data table*; Atlassian Design System, *Dynamic table* | Bộ lọc nằm trên bảng, hành động hàng loạt hiện khi chọn, trạng thái có chữ | P15, P11, P28 |
| Master-detail | Material Design 3, *Canonical layouts: list-detail* | Vùng chi tiết không bao giờ trống; cách thu về một cột trên điện thoại | P15, P18, P19 |
| Form nhiều bước | GOV.UK Design System, *Question pages* và *Check answers*; Material 3, *Steppers* (M2) | Một câu hỏi mỗi trang khi người dùng không quen; trang xem lại trước khi gửi | P20, P21, P29 |
| Chi tiết một đối tượng | Polaris, *Resource details layout* | Cột chính 2/3 cho nội dung, cột phụ 1/3 cho trạng thái và người liên quan | P04, P19, P22 |
| Cài đặt | Apple HIG, *Settings*; Atlassian, cài đặt dự án | Nhóm theo việc người dùng muốn làm, không theo cấu trúc dữ liệu | (khung `dk-settings` trong starter/desktop.html) |
| Trạng thái rỗng, lỗi, đang tải | Polaris, *Empty state*; Carbon, *Empty states pattern* | Rỗng lần đầu khác rỗng do bộ lọc; lỗi một khối không chặn cả màn; trạng thái rỗng gọn, không lấp bằng nội dung tự thêm | P27, P28, P29 |

## Màn điện thoại

| Loại màn | Tham khảo | Học gì | Pattern |
|---|---|---|---|
| Trang chủ app | Apple HIG, *Layout* và *Tab bars*; Material 3, *Navigation bar* | Điểm nhìn ở nửa trên; tab bar tối đa 5 mục, kiểu viên theo TASTE | P01–P05, P06 |
| Danh sách và tìm kiếm | Apple HIG, *Lists and tables*, *Search fields* | Dòng 44 pt trở lên, hành động vuốt có nút thay thế | P15 |
| Thanh toán, xác nhận | Material 3, *Bottom sheets*; Apple HIG, *Sheets* | Tổng tiền luôn nhìn thấy cạnh nút chính | P13, P23 |

## Website và landing

| Loại màn | Tham khảo | Học gì | Pattern |
|---|---|---|---|
| Landing sản phẩm, khoá học | Stripe, Linear (trang chủ); gallery Land-book, Lapa Ninja theo ngành | Mỗi section một bố cục khác; bằng chứng (số, lời chứng thực) đặt ngay sau lời hứa | P26, P17, P25 |
| Bảng giá | Trang pricing của Notion, Figma, Linear | Gói gợi ý nổi bằng viền và badge, không bằng cách làm mờ gói khác; bảng so sánh tách riêng | P23, P24 |
| Sự kiện, lịch | Trang sự kiện của Luma | Ngày, giờ, hình thức và số chỗ nằm trên một hàng | P14, P22 |
| Bài viết, hướng dẫn | GOV.UK *Guidance*; Smashing Magazine | Dòng 60–75 ký tự, mục lục bên cạnh trên desktop | P16 |

## Biểu đồ

| Câu hỏi | Tham khảo | Học gì |
|---|---|---|
| Chọn loại biểu đồ | Financial Times, *Visual Vocabulary* | Chọn theo quan hệ dữ liệu (so sánh, xu hướng, phần của tổng), không theo độ đẹp |
| Màu và nhãn | Carbon, *Color palettes* cho dataviz; skill [`data-visualization-and-dashboard-ux`](../skills_UIUX/data-visualization-and-dashboard-ux/SKILL.md) | Màu phân loại giới hạn 6; nhãn đặt trực tiếp trên dữ liệu, không chú giải (TASTE) |

## Màn tham chiếu trong repo

Chưa có màn nào được chủ repo duyệt. Màn do agent dựng ([sổ đơn hàng](../design-system/examples/data-table/README.md),
các lượt benchmark) là `CHƯA DUYỆT`: dùng để xem cấu trúc, không dùng làm chuẩn gu. Khi có màn đã duyệt,
chúng nằm ở [`examples/`](examples/README.md) và được ưu tiên trên mọi tham khảo ngoài.

Ghi nguồn đã xem vào phần bàn giao. Không chép logo, ảnh, chữ của sản phẩm khác.
