# Thay thế, không phủ đè

## 1. Phủ đè trông như thế nào

| Dấu hiệu | Vì sao hại |
|---|---|
| File CSS mới nạp sau mọi file cũ ("final layer", "v6", "overrides") | Thêm một lớp vào chuỗi chồng; lần sửa sau lại thêm lớp nữa |
| Nhiều `!important` | Thắng cascade bằng sức mạnh, không bằng sửa nguồn; trạng thái hover, focus, tối dễ hỏng |
| JS tìm phần tử sau render rồi chèn, sửa HTML | Hai nguồn sự thật cho cùng một màn; dữ liệu bị lặp; nhấp nháy khi tải |
| Bộ token song song (`--v6-*` cạnh token cũ) | Hai hệ màu cùng sống, không ai biết token nào đúng |
| Chỉ đổi màu, font, bo trên markup cũ | Màn trống, nhiều chữ, khối lặp do markup vẫn nguyên |
| Code cũ bị thay nhưng không bị xoá | Người sau không biết file nào thật |

## 2. Thay thế trông như thế nào

- Giá trị mới nằm **trong file token gốc**; token cũ không còn dùng bị xoá.
- Quy tắc mới nằm **trong file CSS đang sở hữu component**; quy tắc cũ bị viết lại hoặc xoá trong cùng commit.
- Markup mới được **sinh ra từ renderer, template, component**; không có bước vá sau render.
- Lớp chồng thừa được **gộp ngược về nguồn rồi xoá**, thẻ nạp được gỡ.
- Diff có nhiều dòng `-`. Một redesign thật thường xoá gần bằng hoặc nhiều hơn số dòng thêm.

## 3. Thứ tự làm

1. **Token:** đổi giá trị và vai trò trong file token gốc. Nhiều màn đổi theo ngay; chụp lại và xem.
2. **Component:** viết lại CSS từng component trong file sở hữu nó; xoá biến thể chết.
3. **Markup:** sửa renderer, template để cấu trúc màn theo hướng mới (bỏ chữ thừa, gộp khối, đổi bố cục,
   điều hướng). Có generator thì chạy lại.
4. **Từng màn:** hoàn thiện theo hướng đã duyệt, chạy test hành vi sau mỗi màn.
5. **Dọn:** gộp các lớp CSS còn lại về nguồn, xoá file và thẻ nạp thừa, xoá class không còn dùng.

## 4. Khi chuỗi chồng lớp quá dày

Dự án có hàng chục file CSS chồng nhau (Nova: 36 file, `nova-current.css` sinh từ 21 nguồn). Hai cách hợp lệ:

- **Gộp về nguồn:** chọn một file làm nguồn chính cho mỗi nhóm (token, layout, component, màn), chuyển quy
  tắc còn thắng vào đó, xoá phần còn lại. Tốt khi phần lớn cấu trúc được giữ.
- **Thay hẳn tầng giao diện:** viết hệ CSS mới theo hướng đã duyệt, chuyển trang sang hệ mới theo từng
  màn, gỡ toàn bộ file cũ khi màn cuối chuyển xong. Tốt khi hướng mới khác hẳn. Trong lúc chuyển có thể
  có hai hệ song song, đánh dấu `brownfield-allow: <màn nào còn dùng hệ cũ, gỡ khi nào>`; bản giao cuối
  không còn hệ cũ.

Không hợp lệ: thêm file thứ 37 nạp sau cùng và để nguyên 36 file kia.

## 5. Ánh xạ với design system của repo

Dự án đã có token và class riêng thì `ds-*` và `pt-*` của repo không lắp thẳng vào được. Cách dùng:

- Lấy **hợp đồng** của pattern (giải phẫu, mật độ tối thiểu, dùng sai) làm checklist cho khối tương ứng.
- Lấy **giá trị** (thang khoảng cách, thang chữ, bo góc) từ hướng đã duyệt, viết vào token của dự án.
- Chỉ chép `design-system/` vào dự án khi kế hoạch là thay hẳn hệ thống của dự án bằng hệ của repo, và
  khi đó xoá hệ cũ theo mục 4.

## 6. Đo

```sh
python3 skills_UIUX/brownfield-redesign/scripts/overlay-check.py --repo <dự-án> --base <nhánh-gốc> --head <nhánh-redesign>
```

Script không phán đẹp hay xấu; nó chỉ cho biết nhánh đang thay hay đang đè. Đẹp hay không vẫn soát bằng
ảnh, `taste-check` và duyệt độc lập.
