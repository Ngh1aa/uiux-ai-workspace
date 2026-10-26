# Bố cục, lưới và mật độ

Trang này trả lời: **chia màn thế nào để vừa gọn vừa đầy đặn?** Đọc khi dựng màn từ cỡ S trở lên,
nhất là màn desktop và artboard canvas. Đi cùng [`TASTE.md`](../TASTE.md) và
[`CRAFT.md`](../CRAFT.md); số liệu ở đây là điểm xuất phát, brief của dự án thắng.

## 1. Minimalism không có nghĩa là trống

Có hai loại khoảng trắng:

| Loại | Là gì | Ví dụ đúng | Ví dụ sai |
|---|---|---|---|
| **Khoảng trắng chủ động** | Khoảng trống được đặt để nhóm, tách hoặc dồn chú ý | Lề quanh con số lớn, khoảng giữa hai nhóm form, hero trang giới thiệu | |
| **Khoảng trắng bị động** | Phần còn thừa vì nội dung không đủ lấp khung | | Nửa phải màn desktop bỏ trống, 300 px trống ở đáy artboard, card cao 240 px chỉ có một dòng chữ ở đầu |

Minimalism bớt **nhiễu**: màu thừa, viền thừa, bóng, hoạ tiết, câu mô tả lặp lại điều giao diện đã nói.
Nó không bớt **thông tin có ích**. Màn tối giản tốt vẫn trả lời đủ ba câu: đây là gì, tình hình ra sao,
làm gì tiếp.

## 2. Lưới

| Khổ | Cột | Gutter | Lề | Nội dung tối đa |
|---|---|---|---|---|
| Điện thoại (< 600) | 4 | 16 | 16–20 | toàn khung |
| Tablet (600–1023) | 8 | 20–24 | 24 | toàn khung |
| Desktop (1024–1439) | 12 | 24 | 32 | 1200 |
| Desktop rộng (≥ 1440) | 12 | 24–32 | 40 | 1280 (app quản trị có thể dùng toàn khung trừ rail) |

Cột là để **chia vùng**, không phải để căn từng chữ. Mỗi vùng chiếm số cột chẵn hoặc chia hết, ví dụ
8 + 4, 9 + 3, 6 + 6, 4 + 4 + 4. Chữ dài vẫn giữ 60–75 ký tự mỗi dòng: khi vùng rộng hơn thì đặt cột phụ
bên cạnh, không kéo dòng chữ dài ra.

## 3. Công thức chia vùng theo loại màn (desktop 1280–1440)

Khung app gồm rail hoặc sidebar (64–280 px) và topbar (56–64 px). Các công thức dưới đây áp cho vùng
nội dung còn lại.

| Loại màn | Chia vùng (12 cột) | Phần lấp khung |
|---|---|---|
| Tổng quan, dashboard | Hàng 1: card nổi bật 8 + tóm tắt phụ 4. Hàng 2: 4 + 4 + 4 KPI hoặc biểu đồ 8 + danh sách 4. Hàng 3: bảng 12 | Biểu đồ và bảng giãn theo chiều cao còn lại |
| Danh sách, bảng quản trị | Bộ lọc 12, rồi bảng 12; hoặc bảng 8 + chi tiết mục đang chọn 4 | Bảng có phân trang; vùng chi tiết hiện mục đầu tiên khi chưa chọn |
| Master-detail (hộp thư, duyệt bài) | Danh sách 4 + chi tiết 8 | Chi tiết luôn có nội dung: mục đang chọn hoặc hướng dẫn chọn |
| Form nhiều bước | Stepper 12; form 7–8 + cột phụ 4–5 | Cột phụ: tóm tắt đã nhập, mốc thời gian, checklist hồ sơ, trợ giúp |
| Chi tiết một đối tượng | Đầu trang 12 (ảnh, tên, hành động); nội dung 8 + thông tin phụ 4 | Thông tin phụ: trạng thái, người liên quan, lịch sử gần đây |
| Cài đặt | Mục lục 3 + nội dung 9 (hoặc 6 + 3 mô tả) | Mỗi nhóm cài đặt là một khối có tiêu đề, không phải một danh sách dài liền |
| Đăng nhập, xác thực | Chia đôi 6 + 6: bên thương hiệu (ảnh, lời hứa, minh hoạ) và bên form | Form căn giữa theo chiều dọc; đây là chỗ khoảng trắng chủ động được phép |
| Phòng live, video | Video 8 + tương tác 4 (chat, hỏi đáp, chương trình) | Dưới video là thông tin buổi và hành động |
| Trang giới thiệu, landing | Mỗi section một bố cục khác (lệch 7 + 5, lưới 3 hoặc 4, dải số liệu 12) | Mỗi section cao theo nội dung, không ép bằng 100vh |

Trên điện thoại, các vùng xếp chồng theo thứ tự đọc: thông tin chính, hành động, rồi vùng phụ. Vùng phụ có
thể thu thành accordion hoặc bottom sheet.

## 4. Ba mức mật độ

Chọn một mức cho mỗi loại màn và ghi vào khối kế hoạch thị giác.

| Thông số | Thoáng (marketing, onboarding) | Vừa (app người dùng) | Gọn (quản trị, bảng dữ liệu) |
|---|---|---|---|
| Khoảng cách giữa section | 96–128 | 32–48 | 24–32 |
| Khoảng cách giữa nhóm | 32–48 | 24 | 16 |
| Padding trong card | 32–40 | 20–24 | 16 |
| Chiều cao dòng danh sách / bảng | 72+ | 56–64 | 40–48 |
| Chữ thân | 17–20 | 15–17 | 14–15 |
| Thang chữ (tỉ lệ) | 1,25–1,333 | 1,2 | 1,125–1,2 |
| Chữ lớn nhất so với chữ thân | ≥ 2,5 lần | ≥ 1,75 lần | ≥ 1,5 lần |

Mật độ gọn vẫn giữ vùng chạm và tương phản theo `CRAFT.md`. Gọn là bớt khoảng cách, không phải thu nhỏ chữ
dưới 14 px.

## 5. Khi màn còn trống: sửa theo thứ tự này

1. **Thu khung.** Artboard, modal, sheet ôm theo nội dung. Màn app thật thì khung là màn hình, chuyển sang bước 2.
2. **Chia lại vùng.** Một cột hẹp thành 8 + 4 hoặc 6 + 6; danh sách thành master-detail.
3. **Đưa lên thông tin có ích đang bị giấu**: tóm tắt, tiến độ, so sánh kỳ trước, bước tiếp theo, mục gần
   đây, trạng thái của người khác trong nhóm. Mỗi khối thêm vào phải trả lời một câu hỏi thật của người dùng.
4. **Phóng điểm nhìn.** Con số chính, ảnh, biểu đồ được to hơn để gánh khoảng trống chủ động quanh nó.
5. Cuối cùng mới tăng khoảng cách, và chỉ tới mức trần của mật độ đã chọn.

Không lấp bằng: chữ mô tả lặp lại, ảnh trang trí không mang thông tin, số liệu bịa, card rỗng giữ chỗ.

## 6. Cân bằng và điểm nhìn

- Mỗi màn có **một điểm nhìn** (con số lớn, ảnh, tiêu đề), lớn hơn hẳn phần còn lại: tối thiểu 1,5 lần chữ
  thân, thường 2–3 lần.
- Cân bằng trái phải: khối nặng (ảnh, card màu, biểu đồ) bên này thì bên kia cần khối có khối lượng tương
  đương, hoặc khoảng trắng chủ động có lý do (ví dụ hero lệch trái).
- Nhịp dọc: khoảng cách trong nhóm nhỏ hơn giữa nhóm ít nhất 1,5 lần. Các khối cùng hàng có cạnh trên
  và cạnh dưới thẳng nhau; dùng `align-items: stretch` và cho phần thân card giãn.
- Card cùng hàng cao bằng nhau, nội dung bên trong phủ ít nhất khoảng 60% chiều cao. Thiếu nội dung thì
  đổi sang dòng danh sách thay vì card.

## 7. Khoảng trống có chủ đích

Một số màn trống là đúng: đăng nhập, trạng thái rỗng, màn xác nhận thành công, hero trang giới thiệu.
Đánh dấu vùng đó bằng `data-whitespace` để `taste-check` không cảnh báo, và ghi một dòng lý do trong ghi
chú giao:

```html
<div class="empty" data-whitespace="trạng thái rỗng, căn giữa để tập trung vào một hành động">…</div>
```

## 8. Soát tự động

`taste-check.cjs` có bốn cảnh báo bố cục. Màn desktop và canvas chạy thêm `--layout strict` để chúng thành lỗi.

| Luật | Bắt gì | Ngưỡng |
|---|---|---|
| `void` | Khoảng trống dọc liền mạch lớn nhất trong màn | Màn: > 160 px hoặc 18% chiều cao. Trang: > 320 px hoặc nửa khung nhìn |
| `coverage` | Nội dung dồn một bên trên màn ≥ 1024 px | Bỏ trống bên phải > 28% bề ngang và > 280 px |
| `flat-scale` | Chữ lớn nhất không đủ khác chữ thân | Dưới 1,5 lần (màn dưới 600 px: 1,3 lần, vì tiêu đề app trên điện thoại nhỏ hơn) |
| `thin-highlight` | Card nổi bật quá mỏng | Dưới 3 dòng chữ, chỉ một cỡ chữ, hoặc nội dung phủ dưới nửa card |

Các luật này đo khoảng trống bằng hộp chữ thật, ảnh, ô nhập và các khối có nền đậm hoặc ảnh nền. Card trắng
trên nền xám nhạt không được tính là "đã lấp": card cao mà chữ chỉ nằm ở đầu vẫn bị bắt.

```sh
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <trang.html> --width 1440 --height 900 --layout strict
```

## Nguồn

- Material Design 3, *Layout: applying layout*, phần window size classes và panes.
- Apple Human Interface Guidelines, *Layout*.
- Nielsen Norman Group, bài về khoảng trắng và mật độ thông tin trong ứng dụng doanh nghiệp.
- Josef Müller-Brockmann, *Grid Systems in Graphic Design*, cho tư duy chia vùng theo lưới.

Các ngưỡng số trong trang này là giả thuyết nghề nghiệp đã thử trên bộ đề chuẩn của repo, chưa phải kết
quả nghiên cứu người dùng.
