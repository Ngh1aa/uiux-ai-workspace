# Lưới an toàn hành vi

Lý do chính khiến Claude không dám sửa code cũ là sợ phá hành vi. Cách đúng không phải là tránh đụng
code, mà là có test bảo vệ hành vi rồi sửa mạnh tay phần giao diện.

## 1. Mốc trước khi sửa

Trên nhánh gốc, chạy mọi test và kiểm tra dự án có (unit, e2e, Playwright, axe, build, lint). Ghi:

| Bộ test | Lệnh | Kết quả trên nhánh gốc |
|---|---|---|

Test đã đỏ sẵn trên nhánh gốc thì ghi rõ, không tính là do redesign gây ra.

## 2. Phân loại test

| Loại | Ví dụ | Khi redesign |
|---|---|---|
| **Hành vi** | chuyển tiền xong số dư giảm đúng; quay lại giữ số đã nhập; nút có tên truy cập; lỗi mạng hiện cách thử lại | Giữ nguyên, phải xanh trước và sau |
| **Giao diện** | nền là `#F3F6FA`; có đúng hai thanh điều hướng; class `.nova-hero-card` tồn tại; ảnh so pixel | Đổi sang kiểm hành vi nếu được, không thì cập nhật theo giao diện mới |
| **Lẫn cả hai** | "nút Gửi màu xanh và chuyển sang màn xác nhận" | Tách: giữ phần hành vi, bỏ hoặc cập nhật phần màu |

## 3. Viết test đặc tả trước khi xoá

Luồng chính chưa có test thì viết trước khi thay markup. Kiểm bằng thứ người dùng thấy, không bằng cấu trúc
DOM cũ, để test sống qua redesign:

```js
// tốt: sống qua việc đổi markup
await page.getByRole('button', { name: 'Review transfer' }).click();
await expect(page.getByText('€120.00')).toBeVisible();
await page.getByRole('button', { name: 'Back' }).click();
await expect(page.getByLabel('Amount')).toHaveValue('120');

// tránh: chết ngay khi đổi markup, không nói gì về hành vi
await page.click('.nova-transfer-card > div:nth-child(3) .btn-primary');
```

Tối thiểu cho mỗi luồng chính: đường chính, quay lại sửa rồi xác nhận lại, một nhánh lỗi; số liệu khớp
giữa các màn (tổng tiền, số lượng, ngày giờ).

## 4. Cập nhật test giao diện có chủ đích

Mỗi test giao diện bị đổi ghi một dòng:

| Test | Kiểm gì trước | Kiểm gì sau | Lý do |
|---|---|---|---|
| `foundation.spec` "two navs" | có rail và dock cùng lúc | một điều hướng mỗi khổ màn | Hướng mới bỏ điều hướng đôi |

Không xoá test chỉ để qua. Không nới ngưỡng tương phản, trợ năng hay số liệu.

## 5. Sau mỗi commit

Chạy lại bộ test hành vi sau mỗi bước thay (token, component, renderer, từng màn). Đỏ thì sửa ngay ở bước
đó, đừng dồn tới cuối. Khi giao, đưa bảng mốc trước và kết quả sau.
