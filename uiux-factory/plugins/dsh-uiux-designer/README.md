# UIUX Factory bridge for DeepSeek Harness

Plugin native dùng `@deepseek-ai/dsh-tools` 0.0.1-rc.1. Cung cấp `uiux_design_start` và `uiux_design_status`; không cài, sao chép hay mở iPolloWork canvas.

Factory bridge phải chạy tại `http://127.0.0.1:8788`. Engine `ai` cần cấu hình theo [FREE_BRAIN.md](../../docs/FREE_BRAIN.md); `template` dùng prototype hiện có.

```powershell
npm ci --ignore-scripts
npm test
```

Thêm entry file tuyệt đối vào overlay Cordis của Harness đang có `systemPrompt` và `tools` services:

```yaml
- name: 'C:/Users/LENOVO/uiux-ai-workspace/uiux-factory/plugins/dsh-uiux-designer/index.mjs'
```

Theo [hướng dẫn overlay của Harness](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cordis-tutorial/07-into-the-harness.md), dùng overlay với `--patch`. Không tự sửa profile hay cài CLI của người dùng.

Đã kiểm tra đăng ký và execute qua registry Cordis/ToolRegistry thực với HTTP fixture: tạo job, đọc trạng thái, validation, cancellation trước dispatch. Chưa chạy giao diện DSH hoặc model DSH thật. SDK được pin trong package-lock; API đang preview cần kiểm tra tương thích khi nâng SDK/CLI.

Tool start trả job bất đồng bộ. Hủy HTTP request không hủy job Factory đã được chấp nhận; theo dõi job bằng status/Workbench. Plugin không tự gửi tin nhắn, không tự poll và không tự bật cloud.
