# Đề 01: Đất Nung, lượt theo trang chủ repo chọn (30/10/2026)

Các file: `index.html`, `brand.css`, `site.js`. Font lấy từ `design-system/fonts/pairs.css` (Source Serif 4 và Manrope, OFL, có `₫` và dấu tiếng Việt).
Không mở `benchmarks/runs/` và `benchmarks/evidence/`. Duyệt của con người: `CHƯA DUYỆT`.

## Kế hoạch thị giác

```text
Ngành và vật gốc:      xưởng gốm; vật gốc là chiếc cốc mộc trên bàn xoay và lớp men lam chảy
Một câu cảm giác:      "chậm, mát tay, như men lam vừa chảy qua thân cốc mộc"
Chữ:                   tiêu đề Source Serif 4, 54 px (390) tới 136 px (1280), độ đậm 380, line-height .96, tracking -3,5%;
                       thân Manrope 17/1.6, độ đậm 500/700; có tiếng Việt: có
Màu theo vai trò:      nền #ebe6de (đất mộc), bề mặt #f5f2ed, chữ #1d1814, nhấn men lam #2340b0,
                       nền section trước khi men chảy #221c17; màu đất trong hình #a88d74 tới #d6c2aa
                       Tối: nền #15120f, chữ #efe8df, men #2a47b8 (chữ nhấn #9fb3ff)
Hình khối:             bo 14 px cho mọi bề mặt, nút dạng viên; không viền card, chỉ đường kẻ ngang 1–1,5 px; không bóng
Bố cục màn chính:      [Đất Nung ............ Lớp học  Buổi học  Lịch học  Hỏi đáp  0912 345 678]
                       [Ba tiếng, một         |              ]
                       [khối đất, một         |   cốc mộc    ]  7 + 5 cột, chữ lệch trái, cốc bám đáy
                       [chiếc cốc của         |  trên bàn    ]
                       [riêng bạn.            |    xoay      ]
                       [(Đặt chỗ)  Mỗi buổi từ 300.000 ₫  Mở lớp Thứ Bảy, Chủ nhật]
                       [Ba lớp + 2 câu "đã gồm" (4 cột, ghim) | 3 dòng lớp lớn có chevron (7 cột)]
                       [===== men lam chảy phủ section: Một buổi học, 3 bậc thang 01/02/03 =====]
                       [Lịch học (5 cột, giờ cỡ 56) | Hỏi đáp (6 cột)]
                       [Địa chỉ cỡ 60 | (Đặt chỗ)]  [ĐẤT NUNG chữ khổng lồ, men lam chảy trên đầu chữ]
Lưới và mật độ:        390: 1 cột, lề 20; 1280: 12 cột, gutter 24, lề 40; mật độ thoáng
Card nổi bật:          chỉ trong sheet kết quả: nhãn (Lớp, Ngày, Ca...); thông tin chính (giá trị); ngữ cảnh (Tổng tiền, Đặt lúc)
Một điểm táo bạo:      men lam chảy theo cuộn: từ miệng cốc xuống thân cốc, rồi phủ cả section "Một buổi học"
Ba điểm khác starter:  1. tiêu đề serif 136 px, line-height .96  2. không card, chỉ chữ lớn và đường kẻ  3. hình vẽ SVG có chuyển động gắn với cuộn
Đã đối chiếu mục 2:    "nền kem + nhấn đất nung" gần chạm vì ngành gốm: đổi nhấn sang men lam (Bát Tràng), nền là đất mộc xám ấm, không vàng kem.
                       Ba lớp không thành 3 card giống nhau: thành danh sách chữ lớn. Không eyebrow trên mọi tiêu đề
                       (nhãn in hoa chỉ ở hai số liệu hero và legend trong form).
```

## Trang chủ repo chọn đã theo

- **BCG Building Design**: chỉ hai màu vật liệu (đất mộc và mực nâu đen) cộng một nhấn; một họ chữ chính cỡ rất lớn;
  chữ trồi lên từng dòng. Lấy luôn công thức R1 và nhịp 80 ms giữa các dòng.
- **DOD**: nền trung tính ấm, đúng một màu nhấn dùng triệt để (men lam thay cam gỉ), hình là nhân vật chính và "nở"
  theo cuộn. Ở đây không có ảnh nên hình vẽ cốc gánh vai trò đó, và thứ "nở" là lớp men chứ không phải khung ảnh.
- Phụ: **Corekara** cho ý dải màu quét đổi màu cả section (R4), làm lại thành men chảy từ trên xuống có giọt men.

## Chữ ký thị giác

Men lam chảy. Cốc vẽ bằng SVG đứng trên bàn xoay ở màu đất mộc. Lần đầu mở trang, men rót sẵn một chút ở miệng cốc (1,2 s).
Khi cuộn, men chảy xuống phủ hai phần ba thân cốc kèm giọt men, thân đất đổi từ màu đất sống sang màu đất đã nung,
còn các vòng trên bàn xoay quay theo cuộn. Cùng hình giọt men đó xuất hiện ở ba chỗ: mép dưới lớp men phủ section
"Một buổi học", biểu tượng lớp "Tráng men", và đầu chữ "Đất Nung" khổng lồ ở cuối trang. Ý tưởng lặp lại trong
hình khối, không chỉ nằm trong một hình minh hoạ.

## Ba hiệu ứng kể chuyện

| # | Hiệu ứng | Thời lượng / đường cong | Kích hoạt | Bản giảm chuyển động |
|---|---|---|---|---|
| 1 | Chữ trồi từng dòng (R1) ở H1 và 5 tiêu đề H2. Tách theo từ, mỗi từ có mặt nạ riêng, độ trễ theo dòng thật đo bằng `offsetTop` nên không vỡ dòng ở mọi bề rộng | 1100 ms, `cubic-bezier(.16,1,.3,1)`, trễ 80 ms mỗi dòng | mép trên qua 85% màn (`rootMargin -15%`) | không tách chữ, chữ hiện ngay |
| 2 | Men chảy trên cốc + bàn xoay quay (chữ ký) | rót lần đầu 1200 ms ease-out-cubic; sau đó tuyến tính theo cuộn: men đầy khi đã cuộn 70% chiều cao hero | tải trang, rồi theo cuộn | men ở trạng thái cuối, bàn xoay đứng yên |
| 3 | Men phủ section "Một buổi học" (biến thể R4): lớp men lam có mép giọt men trượt xuống trên nền đất tối | tuyến tính theo cuộn | bắt đầu khi mép trên qua 85% màn, phủ kín sau 80% chiều cao màn | section nền men lam sẵn, ẩn lớp trượt |

Nhịp thao tác (không tính vào 3 hiệu ứng): gạch chân menu 400 ms `cubic-bezier(.625,.05,0,1)`; nền dòng lớp, chevron,
chấm trong nút 300–400 ms `cubic-bezier(.25,1,.5,1)`; sheet mở 340 ms. Không có màn chờ. Không dùng Lenis.

## Luồng đặt chỗ

Nút "Đặt chỗ" ở hero và cuối trang, cùng ba dòng lớp (mở sheet và chọn sẵn đúng lớp đó) → sheet `#dat-cho`
(bottom sheet trên điện thoại, panel phải trên máy tính): Lớp, Ngày (4 ngày cuối tuần tới, tính theo ngày máy, có thứ + ngày/tháng),
Ca, Số người (giới hạn theo số chỗ của lớp, nút + khoá khi đạt tối đa), Họ tên, Số điện thoại, Tổng.
Nút "Đặt chỗ" khoá (`aria-disabled`) kèm lý do hiện ngay trên nút: Chọn ngày học / Chọn ca học / Nhập họ tên /
Nhập số điện thoại / Số điện thoại cần 10 chữ số → sheet xác nhận tiêu đề "Đặt chỗ", nút "Hủy" (về form, giữ dữ liệu) và
"Đặt chỗ" → màn kết quả "Đã đặt chỗ": thẻ người (avatar chữ đầu, tên, số điện thoại), thẻ men lam với Lớp, Ngày, Ca, Số người,
Tổng tiền, Đặt lúc; một dòng tóm tắt; nút "Xong". Đóng sheet thì cả hai chỗ đặt nút hiện dòng trạng thái
"Đã đặt chỗ: <lớp>, <ngày>, <giờ>". Esc, nút X và bấm nền mờ đều đóng sheet về đúng chỗ cũ.

Đã kiểm bằng Playwright (390 sáng, 1280 tối, giảm chuyển động): mở từ dòng "Nặn tay" thì chọn sẵn Nặn tay; bấm khi
đang khoá thì không qua bước sau; nút + dừng ở 10; 2 người × 350.000 = 700.000 ₫; Hủy về form và giữ tên; kết quả đúng
tiêu đề; trạng thái trên trang cập nhật. Đây là đánh giá theo kịch bản, không phải test với người dùng. Không có máy chủ:
chỗ trống thật, gửi xác nhận và thanh toán chưa làm.

## Kết quả checker (lượt cuối)

- `taste-check.cjs --width 390 --width 1280 --height 900 --reflow`, sáng và tối: **0 lỗi, 8 cảnh báo**. Reflow 320 px: ĐẠT.
  Cả 8 cảnh báo là `subtitle` trên hai câu trả lời Hỏi đáp (4 lượt × 2). Giữ vì đó là nội dung brief bắt buộc,
  là câu trả lời chứ không phải dòng giải thích.
- `taste-check.cjs --width 1280 --layout strict`: 0 lỗi (không có void, coverage, flat-scale, thin-highlight).
- `static-check.cjs`: ĐẠT, 0 lỗi, 0 cảnh báo.
- `flow-check.cjs`: tĩnh PASS, luồng UNKNOWN (đã kiểm runtime bằng kịch bản ở trên). 0 cảnh báo; các dòng UNKNOWN là nút xử lý bằng JS.
- axe-core: **chưa chạy** (không cài trong môi trường này).
- Taste-check chạy với giảm chuyển động nên chỉ soát trạng thái tĩnh cuối; trạng thái giữa chừng của hiệu ứng chỉ được soát bằng mắt.

Ảnh: `../shots/` (1,4 MB). Toàn trang: `01-landing-{390,1280}-{light,dark}.jpg`. Theo cuộn, có chuyển động:
`scroll-1280-light-{000,010,042,100}.jpg`, `scroll-390-dark-{000,010,045}.jpg`. Sheet: `sheet-{390-light,1280-dark}-{form,confirm,result}.jpg`.
`scroll-1280-light-v1-before.jpg` là bản đầu (giọt men dạng thanh chữ nhật, cột trái trống) để so.

## Các vòng sửa sau khi nhìn ảnh

1. Bản đầu: giọt men trông như thanh chữ nhật; chữ khổng lồ ở cuối gần như không thấy men; cột trái "Ba lớp" trống;
   địa chỉ rớt một chữ "Nội". Sửa: vẽ lại giọt men (cổ thắt, đầu tròn, mép gợn), `slice` để giọt không bị bóp ở 390 px;
   chuyển hai câu "đã gồm" sang cột trái; ngắt dòng địa chỉ có chủ đích.
2. Hero bị đẩy cốc xuống hàng thứ hai (lưới 8 + 5 cột chồng nhau); tiêu đề lên 136 px; cốc to hơn và bám đáy cùng tiêu đề.
3. Chữ khổng lồ lên độ đậm 640 để men đọc được; mobile tiêu đề lên 54 px; avatar trong thẻ kết quả bị rule `.person span`
   làm mờ chữ, thẻ xác nhận bị kéo dài trên desktop; lớp men phủ bị checker coi là card nổi bật ở trạng thái tĩnh
   (sửa đúng tầng: khi giảm chuyển động thì section tự mang nền men, ẩn lớp trượt).

4. Theo góp ý của chủ repo về ba điểm yếu (agent điều phối sửa):
   - **Cốc có khối và chất liệu:** bóng khối trụ nhiều tầng, vân đất (`feTurbulence`), chấm sắt kiểu gốm sành,
     men đọng sẫm ở mép giọt, viền miệng bắt sáng, lòng cốc tối dần, bóng đổ mềm trên bàn xoay. Vệt bóng loáng
     chỉ hiện theo lượng men (`opacity: calc(var(--g) * …)`), đất mộc giữ mờ.
   - **"Một buổi học" ở desktop:** tiêu đề cột trái (5 cột), ba bước bậc thang **đi xuống** ở 7 cột phải, bước 01
     ngang hàng tiêu đề, nên góc trên phải không còn trống. Tên bước 26 px, không xuống dòng.
   - **Cuộn mượt:** tự viết trong `site.js` (~30 dòng, kiểu Lenis): nội suy 0,1 mỗi khung hình cho con lăn chuột.
     Chỉ bật khi có chuột (`pointer: fine`) và không giảm chuyển động. Bỏ qua khi sheet đặt chỗ mở, khi zoom
     (Ctrl), khi cuộn ngang hoặc trong vùng cuộn riêng; phím và kéo thanh cuộn giữ cuộn gốc.
   - Thêm: nút "Đặt chỗ" ở 390 px không còn sát tiêu đề; câu trả lời Hỏi đáp dùng `text-wrap: pretty` để không còn
     một chữ lẻ ở 1024 px.

## Vòng 5: đổi hướng chữ, màu và ảnh (chủ repo: "animation đã có nhưng typo, hình ảnh, màu sắc hoàn toàn không đạt")

Chủ repo chọn: **cho dùng ảnh**, chữ và màu theo **DOD / Wedding**. Các vòng 1–4 ở trên là lịch sử của hướng men lam
đã bị loại; cốc SVG, men chảy và section xanh đã bỏ.

| | Vòng 1–4 | Vòng 5 |
|---|---|---|
| Hình ảnh | Cốc vẽ SVG | 7 ảnh thật (Unsplash), ảnh rộng đầu trang và ảnh trong khung vòm như miệng lò nung |
| Chữ | Có chân Source Serif mảnh + Be Vietnam Pro | Một họ không chân hình học Plus Jakarta Sans 600 (tiêu đề 124 px, giãn chữ −0,045em); đúng một từ nghiêng có chân Cormorant Garamond mỗi tiêu đề lớn ("riêng bạn.", "học"), như chữ viết tay của Wedding |
| Màu | Nền đất xám + men lam | Trắng ngà #f8f6f2, mực #1f1d1b, một màu đất nung #b9441f cho nút, số bước, dải cuối trang |
| Bố cục | Cốc bên phải tiêu đề | DOD: tiêu đề lớn trái, dữ kiện và nút phải; ảnh rộng nở ra tràn màn khi cuộn; lưới 3 lớp so le; 3 bước ảnh vòm so le; dải đất nung cuối trang có địa chỉ lớn và chữ "Đất Nung" khổng lồ |

Chuyển động giữ lại: chữ trồi từng dòng; ảnh đầu trang nở theo cuộn; ảnh hiện từ dưới lên trong khung vòm
(`clip-path`, 1,3 s, `cubic-bezier(.16,1,.3,1)`); cuộn mượt cho chuột. Giảm chuyển động: mọi thứ hiện ngay.

Ảnh: tải từ Unsplash (giấy phép Unsplash, dùng tự do) bằng workflow GitHub Actions tạm vì máy dựng không ra được mạng;
đã xoá workflow sau khi tải. Mã ảnh: 1764507768733-667e135d8cb9 (đầu trang), 1590605095243-072811dbe64c,
1771523350747-638a89667c8f, 1673339065013-f8411fb93848 (ba lớp), 1507022787381-b30170b5ebf4,
1607556671927-78a6605e290b, 1771523351104-03d9c2cc347c (ba bước). Khi có ảnh thật của xưởng thì thay cùng tên file.
Font: Plus Jakarta Sans và Cormorant Garamond (OFL), tự host trong `fonts/`, chỉ các cỡ dùng tới.

Soát vòng 5: `taste-check` 390/1024/1280/1440 sáng/tối, reflow 320: 0 lỗi; 24 cảnh báo đều là `subtitle` cho
câu trả lời Hỏi đáp và dòng "Giá đã gồm…" mà đề bắt buộc. `static-check` 0 lỗi. Luồng đặt chỗ chạy lại bằng kịch bản.

Điểm yếu vòng 5:
- Ảnh là ảnh kho, không phải xưởng Đất Nung; tông ảnh khá đồng đều nhưng chưa được chỉnh màu chung.
- Lưới "Ba lớp" và "Một buổi học" cùng kiểu ảnh vòm so le, hai section liền nhau hơi giống nhau.
- Chữ nghiêng Cormorant ở cỡ lớn có dấu tiếng Việt hơi mảnh; cần chủ repo xem có hợp không.

## Điểm yếu còn lại (vòng 1–4)

- Cốc đã có khối và chất liệu nhưng vẫn là hình vẽ; ảnh thật (khi brief cho phép) sẽ mạnh hơn.
- Ba bước chỉ có tên vì đề không cho mô tả; phần dưới cột tiêu đề "Một buổi học" ở desktop vẫn để thoáng.
- Cuộn mượt tự viết chưa thử trên touchpad Mac và chuột của nhiều hãng; Lenis bản chính thức xử lý nhiều trường hợp hơn.
- Lịch học: nhãn "Thứ Bảy" và "Chủ nhật" 17 px đặt cạnh giờ 56 px trông hơi lạc trên điện thoại.
- Ngày trong sheet tính theo ngày máy và không biết lớp đã kín chỗ hay chưa (chưa có dữ liệu thật).
- Chữ "Đất Nung" khổng lồ có men chỉ là trang trí (`aria-hidden`), dùng `background-clip: text`; có `@supports` lùi về
  chữ mực đặc, nhưng chưa thử trên trình duyệt cũ.
- axe chưa chạy; chưa kiểm thiết bị thật, chưa kiểm phóng chữ 200%.
