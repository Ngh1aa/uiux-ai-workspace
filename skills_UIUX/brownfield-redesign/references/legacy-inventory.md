# Kiểm kê code cũ

Mục tiêu: biết **ai đang sở hữu từng phần giao diện** trước khi sửa, để sửa đúng chỗ và dám xoá. Kiểm kê
xong mới được viết CSS. Ra file `docs/redesign/inventory.md` trong dự án.

## 1. Bản đồ nạp và sở hữu

Lấy thứ tự nạp thật, không đoán:

```sh
# thẻ nạp CSS/JS theo thứ tự trong từng trang
grep -nE '<link[^>]+stylesheet|<script[^>]+src' *.html
# import trong CSS và JS
grep -rnE '@import|import .+\.(css|scss)' src assets 2>/dev/null
# kích thước từng file
wc -l assets/*.css | sort -n
```

Ghi bảng:

| File | Nạp ở đâu, thứ tự | Dòng | Sở hữu gì (màn, component) | Đè lên file nào | Còn dùng? | Quyết định |
|---|---|---|---|---|---|---|

Quyết định: `GIỮ` (là nguồn chính, sẽ sửa tại đây) · `GỘP` (chuyển quy tắc còn dùng về nguồn chính) ·
`XOÁ` (chết hoặc bị thay hết) · `SINH RA` (file sinh tự động, sửa ở nguồn).

Tìm quy tắc chết nhanh: mở trang trong trình duyệt, dùng Coverage của DevTools hoặc Playwright
`page.coverage.startCSSCoverage()` qua mọi màn và trạng thái; selector không khớp phần tử nào ở bất kỳ màn
nào là ứng viên xoá. Xác nhận lại bằng tìm tên class trong renderer trước khi xoá.

## 2. Chuỗi chồng lớp

Dự án sống lâu thường có nhiều lớp "sửa lần n" (`ledger.css`, `ledger-v2.css`, `ledger-final.css`,
`ios26.css`, `ios26-final.css`, `ios26-release.css`). Với mỗi thuộc tính quan trọng của component chính
(nền, màu chữ, bo góc, font, khoảng cách), ghi lớp nào thắng cuối cùng:

```js
// trong DevTools hoặc Playwright: lấy quy tắc thắng cho một phần tử
getComputedStyle(document.querySelector('.hero-card')).backgroundColor
```

Lớp thắng là nơi phải sửa, hoặc là lớp phải gộp ngược về nguồn rồi xoá.

## 3. File sinh tự động và generator

- Đọc đầu file tìm "generated", "do not edit"; đọc `package.json`, `scripts/`, README.
- Ghi: file sinh ra, file nguồn, lệnh sinh, test có kiểm bản sinh khớp nguồn không.
- Quy tắc: không sửa tay bản sinh ra. Sửa nguồn, chạy lệnh, commit cả nguồn và bản sinh.

## 4. Markup đến từ đâu

Màn trống, nhiều chữ, khối lặp thường do **markup**, không do CSS. Ghi cho từng màn:

| Màn | Markup sinh ở (template, renderer, component) | Dữ liệu từ (state, mock, API) | Vấn đề nằm ở markup hay CSS |
|---|---|---|---|

Vấn đề ở markup thì kế hoạch phải sửa renderer hoặc template. CSS không chữa được markup thừa chữ.

## 5. Token

- Liệt kê biến CSS hoặc token hiện có, nhóm theo vai trò.
- Đếm giá trị cứng lặp lại (`grep -oE '#[0-9a-fA-F]{3,8}' -r assets | sort | uniq -c | sort -rn | head`).
- Ghi bảng ánh xạ: vai trò trong hướng mới → token của dự án (có sẵn hoặc thêm mới). Không đưa song song
  một bộ token thứ hai (`--v6-*` cạnh `--nova-*`) trừ khi kế hoạch xoá bộ cũ.

## 6. Test

| Test | Kiểm gì | Loại | Hành động |
|---|---|---|---|

Loại: `HÀNH VI` (luồng, dữ liệu, trạng thái, trợ năng) hoặc `GIAO DIỆN` (màu, class, số phần tử trang trí,
ảnh chụp so pixel). Chi tiết ở [`test-safety-net.md`](test-safety-net.md).

## 7. Ảnh trước

Chụp mọi màn và trạng thái chính ở 390 px và 1280 px (thêm khổ dự án dùng). Lưu cùng tên màn để sau này
chụp ảnh sau đặt cạnh. `taste-check.cjs --screenshot` làm được việc này.
