# Thư viện pattern

Pattern là tầng nằm giữa component và màn hình: một khối ghép sẵn từ token và component, đã có cấu trúc
bên trong và mật độ tối thiểu. Có tầng này để màn mới không phải tự chế card từ nút và badge, và để luật
"card nổi bật cần 3 tầng", "không để khoảng trắng bị động" trong [`TASTE.md`](../../TASTE.md) có sẵn cách
làm đúng.

- Xem: [`index.html`](index.html), 30 pattern ở cả hai chế độ màu, đổi màu theo `brand.css` của dự án.
- Dùng: nạp `patterns.css` sau `components.css` và `brand.css`, đặt class `pt` trên `body` (hoặc vùng chứa).
- Chỉ dùng token ngữ nghĩa. `validate.py` lint file này như `components.css`.
- Màu biểu đồ lấy từ nhóm token `dataviz`, ảnh giữ chỗ từ nhóm `media` (xem mục cuối).

```html
<link rel="stylesheet" href="design-system/generated/tokens.css">
<link rel="stylesheet" href="design-system/components/components.css">
<link rel="stylesheet" href="brand.css">
<link rel="stylesheet" href="design-system/patterns/patterns.css">
<body class="ds-root pt">…</body>
```

## Cách chọn pattern

1. Viết ra câu hỏi người dùng mang tới màn: "hôm nay phải làm gì", "đã nộp xong chưa", "gói nào hợp".
2. Chọn **một** pattern nổi bật (P01–P05) trả lời câu hỏi chính, nếu màn cần điểm nhấn.
3. Lấp các vùng còn lại theo công thức chia vùng ở
   [`foundations/layout-and-density.md`](../../foundations/layout-and-density.md), mỗi vùng một pattern.
4. Soát bằng `taste-check.cjs`. Màn desktop thêm `--layout strict`.

## Hợp đồng từng pattern

Mỗi dòng gồm: **cấu trúc** (anatomy), **khi dùng**, **mật độ tối thiểu** (dưới mức này là pattern rỗng)
và **dùng sai** thường gặp.

### Card nổi bật (tối đa một mỗi màn)

| Mã | Tên, class | Cấu trúc | Khi dùng | Mật độ tối thiểu | Dùng sai |
|---|---|---|---|---|---|
| P01 | Số và tiến độ, `pt-hero` + `pt-hero__strip` | nhãn, số lớn, thanh tiến độ, dải 3 ô chia nhỏ | Trang chủ app việc, quản trị: "còn bao nhiêu việc" | 3 tầng, dải ô có 2–4 ô | Một con số trên nền màu (mẫu "Chưa đạt" trong gallery) |
| P02 | Số và xu hướng, `pt-hero__spark`, `pt-hero__pill` | nhãn, số lớn, pill so sánh, sparkline, câu hành động | Doanh thu, lượt truy cập, số dư | Có so sánh kỳ trước hoặc mục tiêu | Sparkline không có số so sánh kèm theo |
| P03 | Đếm ngược, `pt-hero__count` | pill vòng, tiêu đề mốc, 4 ô ngày giờ phút giây, nút | Hạn nộp, mở bán, sự kiện | Có hành động đi kèm | Đếm ngược tới mốc không có việc gì để làm |
| P04 | Danh tính, `pt-hero__id`, `pt-hero__code` | avatar, tên, đơn vị, dải mã, hạng, hạn | Thẻ thành viên, thẻ dự thi, hồ sơ | Tên và ít nhất 2 thuộc tính | Dùng làm trang trí ở mọi màn |
| P05 | Thành tích, `pt-hero__medal` | huy hiệu, nhãn, tiêu đề thành tích, mô tả số, thanh điểm | Kết quả, cột mốc, chứng nhận | Có con số chứng minh | Lời chúc mừng không có số |

### Số liệu

| Mã | Tên, class | Cấu trúc | Khi dùng | Mật độ tối thiểu | Dùng sai |
|---|---|---|---|---|---|
| P06 | KPI, `pt-kpi__row`, `pt-spark` | nhãn, số, sparkline, chênh lệch và kỳ so sánh | Hàng KPI 3–4 ô | Có chênh lệch kèm kỳ | KPI không có kỳ so sánh, hoặc 6 KPI cùng hàng |
| P07 | Nhóm chỉ số, `pt-stats` (`--pt-cols`) | 2–4 chỉ số chung một card, chia bằng đường mảnh | Khi các số cùng một chủ đề | Mỗi ô có số và chênh lệch | Gom số không liên quan để lấp chỗ |
| P08 | Biểu đồ cột, `pt-chart`, `pt-axis--cols` | tiêu đề, kỳ, câu kết luận, cột, trục bằng HTML | So sánh 5–12 nhóm hoặc ngày | Có câu kết luận ("cao nhất Chủ nhật") | Tô mọi cột bằng màu nhấn; nhãn trục vẽ bằng chữ SVG bị co theo khung |
| P09 | Biểu đồ đường, `pt-legend`, `.line--2` | tiêu đề, chú giải, đường kỳ này, đường kỳ trước nét đứt, trục | Xu hướng theo thời gian | Có kỳ so sánh | Hơn 4 đường; phân biệt đường chỉ bằng màu |
| P10 | Tỉ lệ, `pt-stack`, `pt-split-list` | thanh xếp chồng, danh sách có số và phần trăm | Phần của tổng, 2–6 nhóm | Danh sách số đi kèm thanh | Biểu đồ tròn nhiều lát; thanh không có số |
| P11 | Xếp hạng, `pt-rank` | thứ hạng, tên, thanh tương đối, số; dòng của người xem được tô | Bảng xếp hạng, top sản phẩm | 3 dòng trở lên | Xếp hạng không có mốc thời gian cập nhật |

### Nội dung

| Mã | Tên, class | Cấu trúc | Khi dùng | Mật độ tối thiểu | Dùng sai |
|---|---|---|---|---|---|
| P12 | Card media, `pt-media`, `pt-media__tag` | ảnh 4:3, nhãn trên ảnh, tiêu đề, meta, hàng số và hành động | Bài dự thi, dự án, tác phẩm | Tiêu đề, meta, một hành động | Ảnh xám trống không chú thích |
| P13 | Sản phẩm, `pt-price` | ảnh, tên, người dạy hoặc thương hiệu, đánh giá, giá, nút | Khoá học, hàng hoá | Giá và nút | Giá gạch không có giá mới; nút "Xem thêm" chung chung |
| P14 | Sự kiện, `pt-date` | ô ngày, tiêu đề, giờ và nơi, chỗ còn lại, nút | Lớp, buổi live, hội thảo | Ngày, giờ, hành động | Thiếu múi giờ hoặc hình thức (online, tại chỗ) |
| P15 | Dòng danh sách, `pt-list`, `pt-thumb` | ảnh nhỏ, tên, meta hai cụm, badge trạng thái | Danh sách duyệt, đơn hàng, bài nộp | Dòng cao ≥ 56 px, 2 tầng chữ | Badge trạng thái chỉ bằng màu, không có chữ và icon |
| P16 | Bài viết | chuyên mục, thời gian đọc, tiêu đề, đoạn trích, liên kết | Blog, hướng dẫn, tin | Trích 2–3 dòng | Card bài viết không có đoạn trích |
| P17 | Lời chứng thực, `pt-quote` | trích dẫn, avatar, tên, vai trò | Landing, trang khoá học | Có vai trò cụ thể | Lời bịa ghi như thật: ghi "minh hoạ" cho tới khi có lời thật |
| P18 | Người, `pt-avatar--lg`, `pt-tags` | avatar, tên, vai trò, thẻ chuyên môn, số năm | Giám khảo, giáo viên, đội ngũ | Vai trò và một bằng chứng năng lực | Ảnh chân dung không tên |

### Quy trình và thời gian

| Mã | Tên, class | Cấu trúc | Khi dùng | Mật độ tối thiểu | Dùng sai |
|---|---|---|---|---|---|
| P19 | Mốc thời gian, `pt-timeline` (`is-done`, `aria-current="step"`) | chấm trạng thái, tên mốc, ngày, đường nối | Lộ trình cuộc thi, theo dõi đơn | 3 mốc, có mốc hiện tại | Không đánh dấu đang ở đâu |
| P20 | Stepper, `pt-steps` | số hoặc dấu tích, tên bước, trạng thái bước | Đầu form nhiều bước | 3–6 bước | Hơn 6 bước; bước không có tên |
| P21 | Checklist, `pt-check` | tiến độ x/y, mục đã xong gạch, mục còn lại có hành động | Hồ sơ, onboarding | Mục chưa xong có hành động ngay tại chỗ | Checklist chỉ để đọc |
| P22 | Lịch ngày, `pt-agenda` | giờ, vạch màu theo loại, tên, thời lượng và nơi | Lịch học, lịch họp | 2 mục trở lên | Màu vạch không có chú giải khi có hơn 3 loại |

### Chuyển đổi và bằng chứng

| Mã | Tên, class | Cấu trúc | Khi dùng | Mật độ tối thiểu | Dùng sai |
|---|---|---|---|---|---|
| P23 | Bảng giá, `pt-plans`, `pt-plan[aria-current]` | tên gói, giá và đơn vị, quyền lợi, nút; gói gợi ý có viền và badge | 2–4 gói | Quyền lợi so sánh được giữa các gói | Ép người dùng vào gói đắt bằng nút mờ ở gói rẻ |
| P24 | So sánh, `pt-compare` trong `pt-scroll` | bảng quyền lợi, dấu có và không có nhãn | Đi cùng P23 khi quyền lợi nhiều | Có `th scope`, có `aria-label` cho dấu | Bảng rộng không cuộn được trên điện thoại |
| P25 | Lời mời cuối, `pt-band` | tiêu đề hạn, câu giảm lo, nút | Cuối landing, cuối trang chi tiết | Một hành động chính | Nhiều nút ngang hàng |
| P26 | Bằng chứng, `pt-proof` (`pt-proof--2`) | 2–4 ô số lớn và nhãn, ghi chú nguồn | Landing, giới thiệu | Có nguồn hoặc ghi "minh hoạ" | Số làm tròn đẹp không có nguồn |

### Trạng thái

| Mã | Tên, class | Cấu trúc | Khi dùng | Mật độ tối thiểu | Dùng sai |
|---|---|---|---|---|---|
| P27 | Rỗng, `pt-empty` + `data-whitespace` | minh hoạ, tiêu đề, câu nói khi có dữ liệu sẽ thấy gì, nút | Lần đầu, chưa có dữ liệu | Có hành động đầu tiên | "Không có dữ liệu" trơn |
| P28 | Lỗi một khối, `pt-block-error` | icon, điều gì hỏng, phần nào vẫn dùng được, nút thử lại | Một khối hỏng trong màn còn lại vẫn chạy | Nói rõ phạm vi lỗi | Đổi cả màn sang trang lỗi |
| P29 | Tiến trình và thông báo, `pt-progress-banner`, `pt-toasts` | tên việc, phần trăm, thanh, chi tiết dung lượng; toast có hoàn tác | Tải lên, xuất file, lưu nháp | Có số cụ thể | Toast cho lỗi cần xử lý (dùng banner) |
| P30 | Ảnh giữ chỗ, `pt-media` (`--pt-ratio`), `pt-mosaic` | nền sọc từ token `media`, chú thích tỉ lệ và nội dung ảnh | Bản nháp chưa có ảnh thật | Chú thích nói ảnh gì, tỉ lệ nào | Khối xám trống; ảnh stock không liên quan |

## Token dùng riêng cho pattern

| Nhóm | Token | Dùng cho |
|---|---|---|
| `dataviz.categorical-1…6` | 6 màu phân loại, đã soát ≥ 3:1 trên nền trang và nền card ở cả hai chế độ | Chuỗi dữ liệu, lát tỉ lệ, chú giải |
| `dataviz.sequential-1…5` | Một sắc độ từ nhạt tới đậm (chế độ tối đảo chiều) | Heatmap, mật độ |
| `dataviz.diverging-negative/neutral/positive` | Hai đầu đỏ và xanh, giữa trung tính | Chênh lệch so với mục tiêu |
| `dataviz.grid`, `axis`, `highlight`, `muted` | Lưới, chữ trục (≥ 4,5:1), cột nhấn, cột nền | Mọi biểu đồ |
| `media.placeholder-bg/pattern/ink` | Nền sọc và chữ chú thích của ảnh giữ chỗ | P12, P13, P15, P30 |
| `media.scrim-ink` | Chữ trên lớp phủ ảnh | Nhãn đặt trên ảnh thật |

Quy tắc màu biểu đồ: một màu nhấn cho điều cần nói, phần còn lại dùng `muted`; không phân biệt chuỗi chỉ
bằng màu (thêm nét đứt, nhãn trực tiếp hoặc chú giải có chữ); nhãn trục và số viết bằng HTML để không bị
co theo khung SVG trên điện thoại.

## Soát

```sh
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs design-system/patterns/index.html \
  --width 320 --width 390 --width 768 --width 1280 --width 1440
```

Mỗi pattern trong gallery được bọc bằng `data-screen` và `data-part`: `data-part` báo cho `taste-check` đây
là khối mẫu chứ không phải màn đầy đủ, nên bỏ qua hai luật đo cả màn (`flat-scale`, `coverage`); các luật
khác (tràn, tương phản, vùng chạm, card nổi bật mỏng) vẫn áp dụng. Mẫu "Chưa đạt" cố ý không có `data-part`
và luôn có cảnh báo `thin-highlight`, để minh hoạ điều luật bắt.
