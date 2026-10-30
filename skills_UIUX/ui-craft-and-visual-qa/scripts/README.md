# Scripts

## Soát theo gu (`taste-check.cjs`)

Soát trang đã render theo [`TASTE.md`](../../../TASTE.md) trong Chromium, cả chế độ sáng và tối.
Mỗi phần tử có `data-screen="Tên màn"` được soát như một màn riêng.

- **Lỗi:** dấu " · " nối cụm từ, chữ dưới ngưỡng tương phản AA, nhãn điều khiển ngắn bị gãy dòng, nội dung
  tràn ngang hoặc bị khung cha cắt mất, hơn một card nổi bật trong một màn, ảnh/font/CSS tải lỗi,
  vi phạm axe-core mức serious/critical (khi có cài axe-core), tràn ngang ở 320 px (với `--reflow`).
- **Cảnh báo:** card có nhiều bán kính bo góc, hơn 3 nhóm màu, vùng chạm dưới 44×44 px, chữ bị cắt
  bằng "…", dòng cuối chỉ còn một chữ, chữ sát mép màn hẹp, heading/nội dung ngắn xuống dòng cần review.
- **Cảnh báo bố cục** (thành lỗi khi thêm `--layout strict`): `void` khoảng trống dọc lớn, `coverage`
  nội dung dồn một bên trên màn rộng, `flat-scale` thang chữ phẳng, `thin-highlight` card nổi bật quá
  mỏng. Ngưỡng và cách sửa: [`layout-and-density.md`](../../../foundations/layout-and-density.md).
  Vùng trống có chủ đích đánh dấu `data-whitespace`.

```bash
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs design-system/starter/mobile.html --screenshot qa/
```

Mặc định soát ở 390 px và 1280 px. Ghi `--width` là thay mặc định; website nên dùng
`--width 390 --width 768 --width 1280 --width 1440 --reflow`. `--reflow` thêm một lượt ở 320 px
(tương đương phóng to 400%, WCAG 1.4.10), chỉ bắt tràn ngang; không dùng cho trang có khung điện
thoại cố định. axe-core chạy khi tìm thấy (`npm install axe-core@4` cùng chỗ với Playwright),
`--no-axe` để tắt; kết quả luôn ghi axe đã chạy hay chưa.

Tuỳ chọn: `--root` (thư mục phục vụ file, mặc định thư mục hiện tại), `--width` (lặp được),
`--height`, `--theme light|dark|both`, `--screenshot <thư mục>`, `--json <file>`,
`--layout warn|strict`. Thoát với mã 1
khi có lỗi, mã 2 khi không chạy được. Cần Playwright: script tự tìm qua `NODE_PATH`, `node_modules`
gần đó và thư mục npm toàn cục; không thấy thì in cách xử lý (xem mục "Khi không chạy được taste-check" bên dưới).
Test: `node --test skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.test.cjs`.

Script là tín hiệu tự động, không thay việc mở ảnh chụp ra nhìn.

Luật theo [`TASTE.md`](../../../TASTE.md), là **lỗi**: `demo-note` (ghi chú bản mẫu trên màn), `template-var`
(`{{…}}`), `small-text` (chữ < 12 px), `left-bar` (thanh màu bên trái card), `decor-overlap` (hoạ tiết đè chữ),
`fixed-overlap` (thanh cố định ở đáy che nội dung khi đã cuộn hết). `subtitle` (dòng giải thích phụ dưới tiêu
đề) là cảnh báo phải xem từng chỗ. Nhãn artboard hay gallery nằm ngoài màn thì đánh dấu `data-annotation`.

### Khi không chạy được taste-check

Theo thứ tự:

1. Cài Playwright ngoài repo rồi chạy lại:
   `npm install --prefix /tmp/pw playwright@1 && npx --prefix /tmp/pw playwright install chromium`,
   sau đó đặt `NODE_PATH=/tmp/pw/node_modules`.
2. Mạng chặn, không cài được: mở trang bằng trình duyệt có sẵn trong phiên, chụp 390 px và 1280 px ở
   cả sáng và tối, soát bằng mắt theo checklist "Trước khi giao" trong [`TASTE.md`](../../../TASTE.md).
3. Luôn chạy thêm `static-check.cjs` (không cần cài gì).

Khi giao, ghi rõ đã soát bằng cách nào và phần nào chưa soát được. Không nói "đã đạt" khi mới chỉ
soát tĩnh.

Trên website, section/header/footer full-bleed là vùng bố cục, không tự động tính là card nổi bật.
Các card thật và canvas `data-screen` vẫn được kiểm tra. Khi runtime thay nguồn ảnh, request cũ
bị hủy được ghi cảnh báo; ảnh hiện tại chưa tải được vẫn là lỗi. Mọi tín hiệu cần đối chiếu brief
và render, không phải bằng chứng luồng dữ liệu hay khả năng sử dụng đã đạt.

## Soát tĩnh khi không có trình duyệt (`static-check.cjs`)

Chỉ cần Node, không cài gì. Đọc mã nguồn trang và CSS cục bộ nó nạp, bắt những lỗi thấy được mà
không cần render: dấu " · " nối cụm từ, thiếu `lang`/viewport/`title`, viewport chặn phóng to, ảnh
thiếu `alt`, nút hoặc liên kết không có tên, chữ "Lorem ipsum"; cảnh báo màu viết cứng ngoài token,
`transition: all`, bỏ outline mà không có `:focus-visible`, chữ dưới 12px, emoji làm icon.

```bash
node skills_UIUX/ui-craft-and-visual-qa/scripts/static-check.cjs <trang.html>
```

Không đo được tương phản thật, tràn chữ hay gãy dòng, nên không thay được taste-check.
Test: `node --test skills_UIUX/ui-craft-and-visual-qa/scripts/static-check.test.cjs`.

## Soát lớp thương hiệu (`design-system/scripts/check-brand.py`)

Soát `brand.css` của dự án chồng lên design system: mọi cặp chữ/nền ở chế độ sáng và tối, hai khối
tối có giống nhau không, tên token có gõ nhầm không. Chỉ cần Python.

```bash
python3 design-system/scripts/check-brand.py <dự-án>/brand.css
```

## Phạm vi kiểm tra

`taste-check` kiểm trang ở state đã render; nó không tự đi qua mọi hover/focus, seed dữ liệu,
auth hay nhánh lỗi. Các tình huống đó cần browser test của dự án hoặc thao tác review riêng.
Giữ [elementary visual sanity checklist](../checklists/elementary-visual-sanity-gate.md) để soát
matched foreground/surface, state và crop khi shared owner thay đổi. Các thuộc tính khai báo crop
không thay cho mở ảnh thật. Không suy ra coverage mà lệnh đã chạy chưa thực hiện.


## Soát luồng (`flow-check.cjs`)

Chỉ cần Node. Đọc cây HTML nguồn bằng tokenizer có trạng thái; không thực thi JS và không suy ra
đồ thị điều hướng hay nghiệp vụ từ regex. Dùng cùng browser test của dự án:

```sh
node skills_UIUX/ui-craft-and-visual-qa/scripts/flow-check.cjs page.html --mode prototype --json qa/flow-source.json
node --test skills_UIUX/ui-craft-and-visual-qa/scripts/flow-check.test.cjs
node --test design-system/tests/gom-moc-flow.test.cjs
```

- `errors` / `FAIL`: liên kết giữ chỗ hoặc đích fragment thiếu trong nguồn khi không có khả năng
  JS xử lý; biến mẫu/ghi chú nội bộ trong text; khai báo rủi ro cao nhưng cố tình bỏ review.
- `warnings` / `WARN`: `no-entry`, `no-confirm`, `no-result`, `disabled-no-reason`, `row-mismatch`,
  `label-long`, `time-no-date`, `caption` cần xem từng chỗ; quy tắc gốc ở `TASTE.md` không có ngoại lệ ngoài brief. Các nhóm có thể trở
  thành lỗi chắc chắn khi có hợp đồng tường minh. Không lấy từ khóa để kết luận giao dịch xảy ra.
- `unknown` / `UNKNOWN`: event handler, submit form, thao tác tại chỗ, Back và navigation động cần
  kiểm hành vi thực tế. `static_status: PASS` và exit 0 chỉ nghĩa không thấy lỗi chắc chắn trong
  nguồn; `flow_status` luôn `UNKNOWN` ở lớp này. Không đổi UNKNOWN thành PASS trong báo cáo.
- `--mode gallery` hoặc `data-flow-mode="gallery"`: artboard không hứa hoạt động như prototype.
  Màn gốc đầu tiên, `data-entry`, `data-deep-link` có thể không có đường vào nội bộ.
- `data-confirm` hoặc dialog/alertdialog cho bước review; `data-confirm-action` và `data-result`
  mô tả hợp đồng kết quả. `data-review="inline|undo"` mô tả lựa chọn theo hậu quả. Metadata là
  chỉ dẫn kiểm tra, không chứng minh hành vi hoạt động.
- Nhãn số và chọn giờ hợp lệ; ngày có thể ở tiêu đề màn, `datetime` hoặc ngữ cảnh. Đơn vị biểu đồ,
  nguồn, thời điểm cập nhật và nhãn minh họa được giữ khi hữu ích. “Thu gọn” không phải thu tiền.

Fixture hợp lệ, sai và ngoại lệ cho cả 10 nhóm nằm trong `flow-check.test.cjs`. Booking regression
chạy 390/1280 px, sáng/tối: root → review → kết quả, Back/sửa, tổng tiền, đúng lớp/khách, buổi kín và
chọn lại, modal Escape/focus, lịch .ics. Đây là kiểm browser trên fixture, chưa xác minh backend,
thiết bị native hoặc người dùng thật.

| Checker | Chịu trách nhiệm |
|---|---|
| `static-check` | HTML/CSS cơ bản, accessible name, metadata, placeholder nội dung (Lorem/John Doe) |
| `taste-check` | State đã render, layout, contrast, reflow, tài nguyên và axe; không đi luồng |
| `flow-check` | Liên kết/hợp đồng nguồn và tín hiệu cần kiểm; biến template; không đo thị giác |
| Browser tests | Hành động thật, dữ liệu, đối tượng/vai trò và khôi phục theo kịch bản cụ thể |

`dead-link` chỉ nằm ở flow-check, không báo trùng `href` trong static-check. Một số phép đo như
accessible name/contrast có thể được checker tĩnh hoặc render kiểm ở tầng bằng chứng khác nhau;
không cộng lặp chúng thành nhiều lỗi nghiệp vụ.

Trên Windows, chạy Python với `python -X utf8 ...` hoặc `$env:PYTHONUTF8='1'`; đọc/ghi file UTF-8.
Node đã dùng `utf8` cho source/JSON. Không suy từ chữ console sai encoding rằng dữ liệu nguồn hỏng.

`--locale vi-VN` chọn locale trình duyệt cho ngày/số/control bản địa. Benchmark ghi locale này tường minh; không suy format từ screenshot ở locale khác.
