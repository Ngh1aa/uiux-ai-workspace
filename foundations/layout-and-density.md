# Bố cục, lưới và mật độ

Chia màn thế nào để gọn mà vẫn đầy đặn. Đọc khi dựng màn từ cỡ S, nhất là desktop và artboard.
[`TASTE.md`](../TASTE.md) thắng mọi số liệu ở đây; brief dự án thắng TASTE.

## 1. Khoảng trắng chủ động và bị động

| Loại | Là gì | Ví dụ |
|---|---|---|
| Chủ động | Đặt có chủ ý để nhóm, tách, dồn chú ý | Lề quanh con số lớn, khoảng giữa hai nhóm form |
| Bị động | Phần thừa vì nội dung không lấp đủ khung | Nửa phải desktop bỏ trống; card cao 240 px chỉ một dòng ở đầu |

Minimalism bớt nhiễu (màu, viền, bóng, câu lặp lại), không bớt thông tin người dùng cần.
Ví dụ: [Sai/Đúng, mục D](examples/README.md).

## 2. Lưới

| Khổ | Cột | Gutter | Lề | Nội dung tối đa |
|---|---|---|---|---|
| Điện thoại (< 600) | 4 | 16 | 16–20 | toàn khung |
| Tablet (600–1023) | 8 | 20–24 | 24 | toàn khung |
| Desktop (1024–1439) | 12 | 24 | 32 | 1200 |
| Desktop rộng (≥ 1440) | 12 | 24–32 | 40 | 1280 (app quản trị có thể dùng toàn khung trừ rail) |

Cột để chia vùng: 8 + 4, 9 + 3, 6 + 6, 4 + 4 + 4. Đoạn văn giữ 60–75 ký tự mỗi dòng; vùng rộng hơn thì
thêm cột phụ, không kéo dòng dài ra.

## 3. Chia vùng theo loại màn (desktop, sau rail 64–280 và topbar 56–64)

| Loại màn | Chia vùng | Vùng phụ chứa gì |
|---|---|---|
| Tổng quan | Card nổi bật 8 + tóm tắt 4; rồi 4 + 4 + 4 hoặc biểu đồ 8 + danh sách 4; rồi bảng 12 | Dữ liệu trong brief, không tự thêm |
| Bảng quản trị | Lọc 12, bảng 12; hoặc bảng 8 + chi tiết 4 | Chi tiết mục đầu tiên khi chưa chọn |
| Master-detail | Danh sách 4 + chi tiết 8 | Mục đang chọn |
| Form nhiều bước | Stepper 12; form 7–8 + cột phụ 4–5 | Tóm tắt đã nhập, mốc, checklist hồ sơ |
| Chi tiết đối tượng | Đầu trang 12; nội dung 8 + phụ 4 | Trạng thái, người liên quan, lịch sử |
| Cài đặt | Mục lục 3 + nội dung 9 | Mỗi nhóm một khối có tiêu đề |
| Đăng nhập | 6 + 6: thương hiệu và form | Đây là chỗ khoảng trắng chủ động được phép |
| Landing | Mỗi section một hình khác (7 + 5, lưới 3–4, dải 12) | Cao theo nội dung, không ép 100vh |

Điện thoại xếp chồng theo thứ tự đọc: thông tin chính, hành động, rồi vùng phụ.

## 4. Ba mức mật độ

| Thông số | Thoáng (marketing) | Vừa (app) | Gọn (quản trị) |
|---|---|---|---|
| Giữa section | 96–128 | 32–48 | 24–32 |
| Giữa nhóm | 32–48 | 24 | 16 |
| Padding card | 32–40 | 20–24 | 16 |
| Cao dòng danh sách / bảng | 72+ | 56–64 | 44–48 |
| Chữ thân | 17–20 | 15–17 | 14–15 |
| Chữ lớn nhất so với thân | ≥ 2,5 lần | ≥ 1,75 lần | ≥ 1,5 lần |

Gọn là bớt khoảng cách, không thu chữ dưới 12 px hay vùng chạm dưới 44 px.

## 5. Khi màn còn trống, sửa theo thứ tự

1. **Thu khung.** Artboard, modal, sheet, card ôm nội dung; đo lại chiều cao sau mỗi lần đổi nội dung.
2. **Chia lại vùng.** Một cột hẹp thành 8 + 4 hoặc master-detail; card mỏng thành dòng danh sách.
3. **Phóng điểm nhìn.** Con số chính, ảnh, biểu đồ to hơn để gánh khoảng trắng chủ động quanh nó.
4. **Đưa lên thông tin đề đã có** mà đang bị giấu. **Không tự thêm** mục, hàng, nút mà brief không yêu cầu.
5. Màn ngắn có nút cố định ở đáy (chi tiết, trạng thái rỗng) được phép trống phần giữa; ghi lý do trong
   phần bàn giao, không lấp bằng nội dung tự chế, không dùng `data-whitespace` để né mảng trống thật.

Không lấp bằng: câu mô tả, ghi chú, ảnh trang trí không mang thông tin, số bịa, card rỗng.

## 6. Cân bằng và nhịp

- Một điểm nhìn mỗi màn, gấp 1,5–3 lần chữ thân.
- Khoảng trong nhóm nhỏ hơn giữa nhóm ít nhất 1,5 lần. Card cùng hàng cao bằng nhau, cạnh thẳng hàng.
- Card chứa danh sách dòng: dòng đầu và cuối sát padding thường của card, không khoảng trống gấp đôi.
- Icon hay avatar trong ô hoặc card: khoảng cách trên, dưới, trái bằng nhau.

## 7. Soát tự động

`taste-check.cjs`: `void` (khoảng trống dọc > 160 px hoặc 18% màn), `coverage` (bỏ trống phải > 28% trên
màn ≥ 1024), `flat-scale` (chữ lớn nhất < 1,5 lần thân; điện thoại 1,3), `thin-highlight` (card nổi bật
dưới 3 tầng). Desktop và canvas thêm `--layout strict`.

Nguồn chính: Material 3 *Layout*, Apple HIG *Layout*, Müller-Brockmann *Grid Systems*. Các ngưỡng là giả
thuyết nghề đã thử trên bộ đề của repo, chưa phải nghiên cứu người dùng.
