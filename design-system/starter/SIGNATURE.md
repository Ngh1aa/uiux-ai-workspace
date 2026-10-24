# Tạo dấu ấn riêng cho từng dự án

Starter kit lo phần **đúng**: bố cục, trạng thái, tương phản, vùng chạm. Phần **của riêng** thì
mỗi dự án phải tự làm. Nếu chỉ đổi màu thương hiệu, màn nào cũng sẽ giống starter kit sơn lại.

Làm 3 bước dưới đây trước khi dựng màn, mất khoảng 15 phút.

## Bước 1: tìm vật gốc của ngành

Trong đời thật, ngành này có vật, đường nét hay nhịp điệu nào ai nhìn cũng nhận ra? Ghi ra 3 thứ,
chọn 1 làm vật gốc.

| Ngành | Vật gốc có thể dùng |
|---|---|
| Xưởng gốm | Vòng xoay của bàn xoay, vệt men chảy, mặt đất nung |
| Sân cầu lông | Vạch kẻ sân, lưới, bảng tỉ số |
| Shop len | Sợi len, hàng mũi đan, cuộn len |
| Trung tâm học thêm | Thời khoá biểu, ô vở kẻ, phiếu điểm |
| Phòng khám | Phiếu hẹn, vạch số thứ tự |

Lấy **tính chất** của vật (đường thẳng hay cong, nhịp đều hay tự do, chất liệu) rồi đưa vào giao
diện. Không vẽ lại nguyên vật thành hình minh hoạ to.

## Bước 2: đổi ít nhất 3 trong 6 "cần gạt", ngoài màu

| Cần gạt | Đổi ở đâu | Ví dụ |
|---|---|---|
| 1. Hình khối | `--ds-card-radius`, `--ds-shape-control` trong `brand.css` | Sân thể thao: góc 12px, cứng cáp. Gốm: góc lớn, mềm |
| 2. Chữ tiêu đề và con số | `--app-font-display` | Số kiểu bảng tỉ số cho thể thao, chữ có chân cho xưởng thủ công |
| 3. Hoạ tiết card nổi bật | `--app-hero-motif` cùng `-size`, `-radius`, `-top`, `-right` | Vạch sân, vòng bàn xoay, hàng mũi đan |
| 4. Cách thể hiện số liệu | Class riêng trong trang | Tỉ số lớn cho lượt đặt, thanh tồn kho như cuộn len đang vơi |
| 5. Giọng chữ | Nội dung | Thể thao: ngắn, động từ. Gốm: chậm, ấm. Kho: rõ, có số |
| 6. Một tương tác đặc trưng | CSS và JS của trang | Chọn khung giờ như chọn ô trên mặt sân |

Ví dụ trong `brand.css` của một app cầu lông:

```css
:root {
  --ds-card-radius: 12px;            /* góc cứng như mép sân */
  --ds-shape-card: 12px;
  --ds-shape-control: 10px;
  --app-font-display: "Be Vietnam Pro", system-ui, sans-serif;
  /* Vạch sân: một đường giữa và một đường ngang, mờ trên nền thương hiệu */
  --app-hero-motif:
    linear-gradient(90deg, transparent calc(50% - 1px), color-mix(in srgb, #fff 18%, transparent) calc(50% - 1px) calc(50% + 1px), transparent calc(50% + 1px)),
    linear-gradient(transparent 38%, color-mix(in srgb, #fff 18%, transparent) 38% calc(38% + 2px), transparent calc(38% + 2px));
  --app-hero-motif-size: 100%;
  --app-hero-motif-radius: 0;
  --app-hero-motif-top: 0;
  --app-hero-motif-right: 0;
}
```

Vòng bàn xoay cho xưởng gốm:

```css
:root {
  --app-hero-motif: repeating-radial-gradient(circle, transparent 0 14px, color-mix(in srgb, #fff 12%, transparent) 14px 16px);
  --app-hero-motif-size: 220px;
}
```

## Bước 3: thử che tên

Che tên sản phẩm và chuyển ảnh chụp sang đen trắng. Vẫn nhận ra đây là ngành gì không? Nếu ảnh
có thể hoán đổi với một dự án khác mà không ai thấy lạ, dấu ấn chưa đủ: quay lại bước 2.

## Giới hạn

- Dấu ấn không được phá [`TASTE.md`](../../TASTE.md): vẫn tối đa một card nổi bật mỗi màn, không
  thêm màu nhấn, bo góc vẫn đồng nhất (đổi bán kính là đổi cho mọi card).
- Hoạ tiết chỉ là nền, không chứa chữ, độ đậm khoảng 10–18% để chữ trên card vẫn đạt tương phản.
  Chạy `taste-check` sau khi thêm.
- Không dùng logo, nhân vật, ảnh có bản quyền hoặc giao diện sao chép của sản phẩm thật.
- Ghi một dòng trong ghi chú dự án: vật gốc đã chọn và 3 cần gạt đã đổi.
