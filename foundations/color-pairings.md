# Bộ màu chủ repo thích

Chủ repo gửi 11 cặp màu ngày 25/11/2026 và duyệt thêm 5 cặp agent đề xuất cùng ngày. Dùng khi brand brief chưa
có màu, hoặc khi chủ repo bảo chọn màu. Brief hay design system của dự án đã có màu thì theo dự án. Cách dựng thang màu và tương phản: [`color-oklch.md`](color-oklch.md).

## 1. Cách dùng

- **Vẫn một màu nhấn** ([`TASTE.md`](../TASTE.md)). Mỗi cặp chia màu theo vai trò: nền trang, mặt card, chữ, **nhấn**
  (nút chính, liên kết, trạng thái đang chọn) và **mảng phụ** (nền nhạt của một khối, chip, ảnh). Cặp có hai
  màu rực (cam + xanh lá, sky + hồng, vàng + xanh dương) thì một màu làm nhấn, màu kia chỉ làm mảng phụ. Không
  chia đều hai màu, không tô mỗi ô một màu.
- Một màn tối đa ba nhóm màu: trung tính, nhấn, một màu trạng thái.
- Mã hex dưới đây là điểm bắt đầu. Đưa vào `brand.css` ở tầng ngữ nghĩa, dựng thang bằng
  `oklch-scale.py` theo sắc của màu nhấn, rồi chạy `check-brand.py` cho cả hai chế độ.
- Chọn cặp theo cảm giác của ngành. Ghi cặp đã chọn và lý do vào kế hoạch thị giác.
- **Mảng phụ nhạt** (sky, matcha nhạt, xanh nhạt, tím nhạt) chỉ dùng làm nền. Không dùng cho chữ, icon mang
  nghĩa hay viền ô nhập, vì chỉ đạt 1–2,6:1 trên nền trang.
- **Vàng không làm màu nhấn trên nền trắng** (1,6:1). Đặt vàng trên nền tối, hoặc dùng vàng làm nền khối với chữ đen.

## 2. 16 cặp chủ repo chọn

Hai cột cuối là tỉ lệ tương phản của chữ trên nền trang và chữ trên nút nhấn. Số tính bằng công thức WCAG, chưa phải kết quả
đo trên màn đã render.

| # | Cặp | Nền trang | Mặt card | Chữ | Nhấn / chữ trên nút | Mảng phụ | Hợp với | Chữ / nền | Chữ / nút |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Be + xanh navy | `#F5EFE6` | `#FFFFFF` | `#1C2333` | `#1F3A68` / trắng | `#E9DFD0` | Tài chính, luật, giáo dục, B2B | 13,7 | 11,3 |
| 2 | Xanh nhạt + đỏ rượu vang + trắng + be | `#F6F1E9` | `#FFFFFF` | `#231B1D` | `#7A1E2C` / trắng | `#DCE8F2` (xanh nhạt) | Nhà hàng, rượu vang, khách sạn, thời trang cổ điển | 15,0 | 10,3 |
| 3 | Vàng + đen | `#121212` | `#1C1C1C` | `#F5F2EA` | `#F5C518` / `#111111` | `#2A2A2A` | Sự kiện, thể thao, xây dựng, agency | 16,8 | 11,6 |
| 4 | Tím + trắng | `#FFFFFF` | `#F6F3FB` | `#1D1A24` | `#5B3CC4` / trắng | `#EDE7FA` | Công nghệ, SaaS, sáng tạo | 17,1 | 7,3 |
| 5 | Xanh dương sky + hồng | `#F3F8FD` | `#FFFFFF` | `#14243A` | `#C2185B` / trắng | `#4FA3E0` hoặc `#F9DCE6` | Mỹ phẩm, trẻ em, app lối sống | 14,6 | 5,9 |
| 6 | Hồng phấn + xanh matcha | `#FBF1F1` | `#FFFFFF` | `#1F2A1E` | `#4E6B3A` / trắng | `#F3D9DB`, `#9DB57A` | Café, mỹ phẩm thiên nhiên, wellness | 13,5 | 6,0 |
| 7 | Cam + xanh lá | `#FAF7F2` | `#FFFFFF` | `#1B2A21` | `#C2410C` / trắng | `#E3EFE5` | Thực phẩm, nông sản, đồ ngoài trời | 14,0 | 5,2 |
| 8 | Vàng + xanh dương | `#FFFFFF` | `#F4F7FC` | `#0F1E3D` | `#1D4ED8` / trắng | `#FFE07A` (vàng) | Giáo dục, giao hàng, dịch vụ công | 16,5 | 6,7 |
| 9 | Tím nhạt + be | `#F4EFE7` | `#FFFFFF` | `#2A2433` | `#6E58A8` / trắng | `#E4DDF2` | Spa, cưới, nội thất | 13,1 | 5,8 |
| 10 | Nâu choco + blue sky | `#F7F2EC` | `#FFFFFF` | `#3B2418` | `#4A2C1D` / trắng | `#CFE6F7` | Bánh, café, đồ da, thời trang | 13,0 | 12,6 |
| 11 | Tím + đen + be | `#EFE8DC` | `#F8F4EC` | `#141414` | `#5B2A86` / trắng | `#141414` (khối đen, chữ be) | Thời trang, nghệ thuật, âm nhạc | 15,1 | 9,9 |
| 12 | Xanh rêu + kem | `#F7F3EA` | `#FFFFFF` | `#1E2419` | `#4D5B2C` / trắng | `#E6E6D2` | Nội thất, du lịch sinh thái | 14,4 | 7,4 |
| 13 | Đất nung + kem | `#FAF5EE` | `#FFFFFF` | `#2A1A14` | `#A2452A` / trắng | `#F0DCCF` | Gốm, thủ công, ẩm thực | 15,4 | 6,1 |
| 14 | Xám than + cam cháy | `#F4F4F2` | `#FFFFFF` | `#1F2124` | `#B4441A` / trắng | `#E4E4E0` | Dashboard kỹ thuật, ô tô, công cụ | 14,7 | 5,6 |
| 15 | Xanh teal + cát | `#F6F1E7` | `#FFFFFF` | `#14272A` | `#0F5E63` / trắng | `#E9DCC3` | Y tế, du lịch biển, fintech | 13,8 | 7,5 |
| 16 | Navy + hồng đất | `#F8F1EE` | `#FFFFFF` | `#16213A` | `#16213A` / trắng | `#E8C4B8` | Thời trang nữ, studio, portfolio | 14,3 | 16,0 |

Cặp 1–11 chủ repo gửi; cặp 12–16 agent đề xuất, chủ repo duyệt ngày 25/11/2026.

Ở cặp 7, màu xanh lá (`#2F6B4F`, 5,9:1) có thể làm màu trạng thái "thành công" thay cho xanh mặc định.
