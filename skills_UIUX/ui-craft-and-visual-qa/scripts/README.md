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
gần đó và thư mục npm toàn cục; không thấy thì in cách xử lý (xem thêm mục "Khi không chạy được
taste-check" trong [`START-HERE.md`](../../../START-HERE.md)).
Test: `node --test skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.test.cjs`.

Script là tín hiệu tự động, không thay việc mở ảnh chụp ra nhìn.

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
