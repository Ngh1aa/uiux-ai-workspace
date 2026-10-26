---
name: brownfield-redesign
description: |
  Thiết kế lại giao diện một sản phẩm đã có code chạy được (prototype HTML/CSS/JS, website, web app,
  app). Dùng khi được nhờ "làm lại", "nâng cấp", "thiết kế lại toàn bộ" một dự án có sẵn. Kiểm kê code
  cũ, giữ ADN thị giác của sản phẩm, dựng lưới test hành vi, rồi thay thế code giao diện tại nguồn và
  xoá phần bị thay, thay vì đè thêm một lớp CSS/JS mới lên trên.
---

# Redesign sản phẩm có sẵn (brownfield)

## Vì sao có skill này

Phần còn lại của repo giỏi dựng giao diện mới từ đầu: starter kit, `brand.css`, 30 pattern đều giả định
một trang trắng. Khi gặp một sản phẩm đã có code, Claude thường chọn đường ít rủi ro nhất cho chính nó:
viết một file CSS mới nạp sau cùng, thêm `!important` để thắng cascade cũ, và chèn DOM bằng JS sau khi
trang đã render. Code cũ không bị đụng, test cũ vẫn xanh, nhưng sản phẩm không thật sự được thiết kế lại.

Ca gốc: Nova PR #76 (26/10/2026). Yêu cầu là làm lại toàn bộ giao diện. Kết quả là `nova-v6.css` 552 dòng
với 699 `!important`, nạp sau 36 file CSS cũ, cộng `nova-v6.js` vá DOM trang chủ; 0 dòng CSS cũ bị sửa
hay xoá. Hướng mới bỏ chất pastel iOS vốn là nhận diện của Nova, màn trống và nhiều chữ vẫn còn vì
markup sinh ra từ renderer cũ không đổi. Xem [`references/nova-case.md`](references/nova-case.md).

Skill này là đường đi cho loại việc đó. Nó đi cùng cỡ việc trong [`WORKFLOWS.md`](../../WORKFLOWS.md)
(thường là L), không thay thế.

## 1. Quyền sửa và xoá code cũ

Khi người dùng yêu cầu thiết kế lại một sản phẩm có sẵn, yêu cầu đó **là** sự cho phép, và cũng là nghĩa
vụ, để làm những việc sau trên một nhánh riêng, không cần hỏi lại từng file:

- sửa file đang sở hữu giao diện: token, CSS component, template, renderer, component JS/TS;
- **xoá** quy tắc CSS, file CSS/JS, markup và class bị thay thế; gộp các lớp CSS chồng nhau;
- đổi cấu trúc markup do renderer hoặc template sinh ra, rồi chạy lại generator;
- cập nhật test đang khoá cứng giao diện cũ (màu nền, class, số thanh điều hướng), có ghi lý do.

Những thứ **giữ nguyên** trừ khi người dùng nói khác: hành vi nghiệp vụ, dữ liệu và công thức, URL,
API và tên sự kiện, nội dung pháp lý, câu chữ đã được kiểm chứng với người dùng. Thứ nào trong số này
buộc phải đổi thì ghi vào kế hoạch và báo khi giao.

Mọi thay đổi nằm trên nhánh và hoàn tác được bằng git, nên "sợ làm hỏng" không phải lý do để phủ đè.
Rủi ro thật được kiểm soát bằng lưới test ở bước 4, không bằng cách tránh đụng vào code.

Quy tắc "giữ thay đổi gọn, đúng phạm vi" trong [`AGENTS.md`](../../AGENTS.md) nói về việc sửa repo này.
Trong dự án của khách, phạm vi chính là cái người dùng yêu cầu: yêu cầu redesign thì phạm vi là toàn bộ
lớp giao diện.

## 2. Xác định mức thay đổi

| Mức | Người dùng nói | Được đụng tới |
|---|---|---|
| **Polish** | "sửa", "chỉnh", "trau chuốt" | Token và CSS component hiện có; không đổi markup |
| **Refresh** | "làm mới", "hiện đại hơn" | Token, CSS component, một phần markup; giữ bố cục chính |
| **Redesign** | "thiết kế lại", "làm lại toàn bộ", "nâng cấp giao diện" | Toàn bộ lớp giao diện: token, CSS, markup, renderer, bố cục, điều hướng |

Không tự hạ mức. Yêu cầu Redesign mà giao một lớp Polish đè lên là giao sai việc. Không chắc thì chọn
mức theo từ người dùng dùng và nói rõ đã chọn mức nào.

## 3. Quy trình

### Bước 1 — Kiểm kê code cũ

Theo [`references/legacy-inventory.md`](references/legacy-inventory.md). Ra file `docs/redesign/inventory.md`
trong dự án, gồm:

- **Bản đồ sở hữu giao diện:** mỗi file CSS/JS/template, thứ tự nạp, số dòng, phần nào còn dùng, phần
  nào chết, file nào đè file nào.
- **File sinh tự động** và generator của chúng (ví dụ `nova-current.css` sinh từ 21 nguồn). Chỉ sửa nguồn.
- **Token hiện có** và chỗ đang viết giá trị cứng.
- **Test** chia hai loại: test hành vi và test khoá giao diện.
- **Ảnh chụp mọi màn** ở cỡ điện thoại và máy tính: đây là ảnh "trước".

Chưa có bản đồ sở hữu thì chưa được viết CSS.

### Bước 2 — Ghi ADN của sản phẩm

Theo [`references/product-dna.md`](references/product-dna.md). Liệt kê 5–8 đặc điểm làm người dùng nhận
ra sản phẩm: bảng màu và cách dùng màu, chất liệu (kính mờ, phẳng, giấy), độ bo, font và giọng chữ, hình
khối, nhịp chuyển động, chi tiết riêng.

Với mỗi đặc điểm, tách **ADN** (giữ và làm tốt hơn) khỏi **lỗi thực thi** (sửa). Ví dụ Nova: pastel
mint, sky, lavender và cảm giác iOS là ADN; mỗi dòng một màu pastel không mang nghĩa là lỗi thực thi.
Sửa lỗi bằng cách cho màu pastel một vai trò, không phải bỏ pastel.

ADN là một phần của brief. [`TASTE.md`](../../TASTE.md) và [`CRAFT.md`](../../CRAFT.md) quyết định cách
thể hiện ADN cho tốt, không được dùng để xoá ADN.

### Bước 3 — Hướng thị giác qua cổng duyệt

Như [cổng duyệt hướng](../../WORKFLOWS.md#cổng-duyệt-hướng-m-l-xl), cộng hai điều kiện:

- ít nhất một hướng là **tiến hoá ADN**: giữ các đặc điểm ADN, sửa toàn bộ lỗi thực thi;
- mỗi hướng ghi rõ giữ, đổi, bỏ đặc điểm ADN nào. Hướng bỏ ADN chỉ được chọn khi người quyết định chọn
  nó và biết mình đang bỏ gì. Không đề xuất hướng bỏ ADN chỉ vì nó hợp `TASTE.md` hơn.

Dựng các hướng bằng **markup mới** cho màn quyết định, không bằng CSS đè lên markup cũ: nếu markup cũ
là nguyên nhân màn trống hay nhiều chữ thì hướng nào đè CSS cũng thừa hưởng lỗi đó.

### Bước 4 — Lưới an toàn hành vi

Theo [`references/test-safety-net.md`](references/test-safety-net.md):

1. Chạy toàn bộ test hiện có trên nhánh gốc, ghi kết quả làm mốc.
2. Viết thêm test đặc tả hành vi (characterization) cho luồng chính chưa có test: chọn, nhập, xác
   nhận, quay lại sửa, nhánh lỗi; kiểm bằng vai trò, nhãn và dữ liệu, không bằng class hay màu.
3. Test khoá giao diện cũ: đổi sang kiểm hành vi nếu được; không được thì cập nhật theo giao diện
   mới và ghi vào bảng "test đã đổi" kèm lý do.

Không làm yếu test để qua. Test hành vi phải xanh cả trước và sau.

### Bước 5 — Kế hoạch thay thế

Theo [`references/replace-not-overlay.md`](references/replace-not-overlay.md) và mẫu
[`references/plan-template.md`](references/plan-template.md). Mỗi dòng của kế hoạch là:
`chủ sở hữu cũ → thay bằng gì → xoá gì → test nào bảo vệ`.

Thứ tự thay: token → component → markup/renderer → từng màn → dọn file chết.

Starter kit và [thư viện pattern](../../design-system/patterns/README.md) dùng làm **hợp đồng cấu
trúc** (giải phẫu khối, mật độ tối thiểu, cách dùng sai): dựng lại khối đó bằng token và class của dự án.
Chỉ chép `ds-*`, `pt-*` vào dự án khi kế hoạch chủ động thay hệ thống cũ bằng hệ thống của repo.

### Bước 6 — Thay tại nguồn

- Sửa giá trị trong file token gốc; thêm token theo vai trò ở đúng tầng của dự án.
- Sửa quy tắc trong file CSS đang sở hữu component; xoá quy tắc cũ bị thay ngay trong cùng commit.
- Sửa renderer, template hoặc component để sinh ra markup mới; không tìm phần tử sau render rồi chèn
  HTML. Có generator thì sửa nguồn, chạy generator, commit cả hai.
- Gộp hoặc xoá các lớp CSS chồng nhau đã trở nên thừa; gỡ thẻ nạp file đã xoá.
- Mỗi commit một chủ sở hữu hoặc một màn, test hành vi xanh sau mỗi commit.

Ngân sách mặc định (vượt thì phải có lý do trong kế hoạch):

| Dấu hiệu phủ đè | Ngân sách |
|---|---|
| File CSS mới nạp sau tất cả file cũ | 0 |
| `!important` tăng ròng | ≤ 5 |
| File JS mới vá DOM sau render | 0 |
| Tỉ lệ dòng CSS cũ bị xoá hoặc sửa / dòng CSS thêm | ≥ 0.3 |
| File sinh tự động sửa tay | 0 |

Ngoại lệ có thật (ví dụ chuyển dần từng màn) đánh dấu `brownfield-allow: <lý do và khi nào gỡ>` trong
file, ghi vào kế hoạch, và gỡ trước khi giao bản cuối.

### Bước 7 — Soát

```sh
python3 skills_UIUX/brownfield-redesign/scripts/overlay-check.py --repo <dự-án> --base <nhánh-gốc> --head <nhánh-redesign>
```

Script đo các dấu hiệu phủ đè ở bảng trên từ `git diff` (xem
[`scripts/README.md`](scripts/README.md)). Bỏ `--head` để so với cây làm việc hiện tại. Sau đó:

- test hành vi của dự án xanh, bằng số liệu so với mốc ở bước 4;
- [`taste-check.cjs`](../ui-craft-and-visual-qa/scripts/README.md) theo cỡ việc;
- ảnh trước và sau đặt cạnh nhau, cùng màn, cùng khổ, cùng dữ liệu;
- **phép thử nhận ra hai chiều**: che logo, người quen sản phẩm vẫn nhận ra đây là sản phẩm cũ (ADN còn),
  và nhìn trước/sau thấy ngay khác biệt ngoài màu và khoảng cách (redesign thật). Hỏng chiều nào cũng
  là chưa xong;
- duyệt độc lập theo [hồ sơ ảnh](../design-critique-and-rationale/references/independent-review.md),
  gửi kèm danh sách ADN để người duyệt chấm cả độ giữ ADN.

## 4. Thứ phải giao

- `docs/redesign/inventory.md`: bản đồ sở hữu, file sinh tự động, test, ảnh trước.
- Bảng ADN: giữ, làm tốt hơn, bỏ (kèm ai đã chọn bỏ).
- Kế hoạch thay thế đã làm xong, có cột "đã xoá".
- Bảng test: mốc trước, sau, test đã đổi và lý do.
- Kết quả `overlay-check.py`, `taste-check`, ảnh trước/sau.
- Thống kê diff: số dòng CSS thêm, xoá; số file xoá. Một redesign thật thường xoá nhiều.

## 5. Acceptance criteria

- [ ] Mức thay đổi khớp lời người dùng; không giao Polish cho yêu cầu Redesign.
- [ ] Có bản đồ sở hữu giao diện trước khi viết CSS.
- [ ] ADN được ghi, cổng duyệt có hướng tiến hoá ADN, bỏ ADN chỉ khi người quyết định chọn.
- [ ] Test hành vi xanh trước và sau; test giao diện đã đổi có lý do.
- [ ] `overlay-check.py` không còn lỗi; cảnh báo còn lại có lý do.
- [ ] Không file CSS mới nạp cuối, không vá DOM sau render, không sửa tay file sinh tự động.
- [ ] Code và file bị thay đã được xoá; không còn quy tắc chết đè nhau.
- [ ] Phép thử nhận ra hai chiều đạt.

## 6. Anti-patterns

- "Final layer" CSS nạp sau cùng với hàng trăm `!important`.
- JS tìm `.hero-card` sau render để chèn thêm khối, lặp lại dữ liệu đã có trong state.
- Đổi màu, font, bo góc trên markup cũ rồi gọi là redesign: màn trống và nhiều chữ vẫn y nguyên.
- Áp gu chung (nền trung tính, ít màu) xoá mất nhận diện của sản phẩm.
- Giữ code cũ "cho chắc" khi đã có test bảo vệ hành vi.
- Sửa tay file sinh tự động; lần chạy generator sau sẽ xoá mất.
- Sửa test cho khớp giao diện mới mà không phân biệt test đó kiểm hành vi hay kiểm giao diện.
