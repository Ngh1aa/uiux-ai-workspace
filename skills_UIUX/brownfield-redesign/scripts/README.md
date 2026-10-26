# Scripts

## Soát phủ đè (`overlay-check.py`)

Đọc `git diff` giữa nhánh gốc và nhánh redesign **của dự án đang làm** và cho biết nhánh đang thay code
giao diện tại nguồn hay đang đè một lớp mới lên. Chỉ cần Python 3 và git.

```sh
python3 skills_UIUX/brownfield-redesign/scripts/overlay-check.py --repo <dự-án> --base origin/main --head <nhánh>
```

Bỏ `--head` để so nhánh gốc với cây làm việc hiện tại (tính cả file mới chưa `git add`).

| Quy tắc | Mức | Bắt gì |
|---|---|---|
| `overlay-ratio` | lỗi | Thêm từ 80 dòng CSS mà số dòng CSS cũ bị xoá hoặc sửa dưới 30% số dòng thêm |
| `new-layer` | lỗi | File CSS mới từ 60 dòng được nạp sau cùng trong một trang (chỉ là file mới: cảnh báo) |
| `important` | lỗi | `!important` tăng ròng quá 5 |
| `dom-patch` | lỗi | File JS mới vừa tìm phần tử (`querySelector`…) vừa chèn hoặc sửa HTML |
| `untouched-owners` | lỗi | Dự án có CSS cũ, nhánh thêm nhiều CSS nhưng không sửa hay xoá file CSS cũ nào |
| `generated` | cảnh báo | Sửa file có dấu "generated", "do not edit" (kiểm đã sửa nguồn và chạy generator) |

Tuỳ chọn: `--min-added`, `--min-ratio`, `--layer-lines`, `--max-important` đổi ngưỡng; `--generated <mẫu>`
(lặp được) đánh dấu thêm file sinh tự động; `--json <file>` ghi kết quả. Thoát mã 1 khi có lỗi, 2 khi
không chạy được (sai `--base`, không phải repo git).

Ngoại lệ có chủ đích: ghi `brownfield-allow: <lý do, gỡ khi nào>` trong file CSS hoặc JS mới để hạ
`new-layer` và `dom-patch` thành cảnh báo. Ghi ngoại lệ vào kế hoạch và gỡ trước bản giao cuối.

Script không đánh giá thẩm mỹ. Đạt script chỉ có nghĩa là nhánh đang thay chứ không đè; vẫn phải soát ảnh,
`taste-check` và duyệt độc lập.

Test: `python3 -m unittest discover -s skills_UIUX/brownfield-redesign/scripts -p "test_*.py"`.
