# Example — Accessible lead form field

```html
<div class="field">
  <label for="email">Email công việc</label>
  <p id="email-help">Chúng tôi dùng email này để phản hồi yêu cầu.</p>
  <input
    id="email"
    name="email"
    type="email"
    autocomplete="email"
    required
    aria-describedby="email-help email-error"
  />
  <p id="email-error" role="alert" hidden></p>
</div>
```

Khi invalid:
1. set `aria-invalid="true"`;
2. message cụ thể: “Nhập email theo dạng name@example.com” thay vì “Invalid”;
3. mở `#email-error`;
4. không reset các field khác;
5. nếu form dài và nhiều lỗi, cung cấp error summary + focus strategy.

Điểm chính của example là **relationship + recovery**, không phải copy markup y nguyên cho mọi framework.
