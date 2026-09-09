import type { ReactNode } from 'react';

type Props = {
  prompt: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  busy: boolean;
  submitLabel: string;
  error?: string;
  children?: ReactNode;
};

export function DesignPromptComposer({ prompt, onChange, onSubmit, busy, submitLabel, error, children }: Props) {
  return (
    <form
      className="dx-brief-composer"
      onSubmit={(event) => {
        event.preventDefault();

        if (prompt.trim() && !busy) {
          onSubmit();
        }
      }}
    >
      <label htmlFor="dx-user-brief">Bạn muốn tạo website như thế nào?</label>
      <textarea
        id="dx-user-brief"
        value={prompt}
        onChange={(event) => onChange(event.target.value)}
        disabled={busy}
        maxLength={12000}
        rows={5}
        placeholder="Ví dụ: Website cho studio kiến trúc, dành cho chủ nhà muốn tìm đơn vị thiết kế. Phong cách tối giản, ấm áp. Có dự án, dịch vụ và form tư vấn."
        aria-describedby="dx-brief-hint"
        aria-invalid={!!error}
        onKeyDown={(event) => {
          if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' && !event.nativeEvent.isComposing) {
            event.preventDefault();

            if (prompt.trim() && !busy) {
              onSubmit();
            }
          }
        }}
      />
      <p id="dx-brief-hint">Nêu mục tiêu, khách hàng và cảm giác bạn muốn. Bạn không cần viết prompt kỹ thuật.</p>
      {children}
      {error && (
        <p className="dx-brief-error" role="alert">
          {error}
        </p>
      )}
      <div className="dx-brief-submit">
        <span>{prompt.length.toLocaleString('vi-VN')} / 12.000 · Ctrl + Enter</span>
        <button type="submit" className="dx-build" disabled={busy || !prompt.trim()}>
          {busy ? 'Đang xử lý…' : submitLabel}
          <span aria-hidden="true">↑</span>
        </button>
      </div>
    </form>
  );
}
