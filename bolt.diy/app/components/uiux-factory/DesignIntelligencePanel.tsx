import { useState } from 'react';
import type { DesignContextInput } from '~/lib/persistence/factoryDraft';

export const EMPTY_DESIGN_CONTEXT: DesignContextInput = {
  brand_name: '',
  personality: [],
  avoid: [],
  guideline: '',
  existing_code: '',
  existing_website: '',
  assets: [],
};

export type DesignToken = { value: string | number | null; status: string; source: string };
export type DesignSystemReport = {
  schema_version: string;
  brand: {
    name: string;
    personality: string[];
    source_status: string;
    conflicts: string[];
    evidence: { subject: string; value: string }[];
  };
  foundations: Record<string, Record<string, DesignToken | string>>;
  unresolved_items: string[];
};
export type ReferenceReport = {
  references: {
    url: string;
    title: string;
    status: string;
    role: string;
    patterns: string[];
    warnings: string[];
    screenshots: string[];
    observations: { category: string; subject: string; value: string; source: string; certainty: string }[];
  }[];
};

type Props = {
  context: DesignContextInput;
  onChange: (context: DesignContextInput) => void;
  tokensText: string;
  onTokensChange: (value: string) => void;
  onAnalyze: () => void;
  busy: boolean;
  error: string;
  system: DesignSystemReport | null;
  references: ReferenceReport | null;
  artifactBase: string;
  stale: boolean;
};

export function DesignIntelligencePanel(props: Props) {
  const { context, onChange, system, references } = props;
  const [uploadError, setUploadError] = useState('');
  const [uploading, setUploading] = useState(false);

  async function uploadImage(file: File | undefined, kind: 'logo' | 'screenshot') {
    if (!file) {
      return;
    }

    setUploadError('');

    if (
      !['image/png', 'image/jpeg', 'image/webp'].includes(file.type) ||
      file.size > 2_000_000 ||
      context.assets.length >= 4
    ) {
      setUploadError('Tối đa 4 ảnh PNG/JPEG/WebP, mỗi ảnh không quá 2 MB.');
      return;
    }

    setUploading(true);

    try {
      const dataUrl = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = () => reject(new Error('Không đọc được ảnh.'));
        reader.readAsDataURL(file);
      });
      onChange({ ...context, assets: [...context.assets, { name: file.name, kind, data_url: dataUrl }] });
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Không đọc được ảnh.');
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="dx-intelligence">
      <div className="dx-studio-head">
        <span>DESIGN INTELLIGENCE · V3</span>
        <h1>Brand DNA trước khi build.</h1>
        <p>
          Đưa vào dữ liệu thương hiệu. Đo reference trên desktop/mobile, kiểm tra nguồn và giải quyết xung đột token.
        </p>
      </div>
      <div className="dx-intelligence-columns">
        <section className="dx-context-form" aria-label="Brand context">
          <label>
            Tên thương hiệu
            <input
              value={context.brand_name}
              maxLength={120}
              disabled={props.busy || uploading}
              onChange={(event) => onChange({ ...context, brand_name: event.target.value })}
            />
          </label>
          <label>
            Tính cách thương hiệu (phân cách bằng dấu phẩy)
            <input
              value={context.personality.join(',')}
              disabled={props.busy || uploading}
              onChange={(event) => onChange({ ...context, personality: event.target.value.split(',') })}
              placeholder="premium, trustworthy, modern"
            />
          </label>
          <label>
            Website hiện có
            <input
              type="url"
              value={context.existing_website}
              disabled={props.busy || uploading}
              onChange={(event) => onChange({ ...context, existing_website: event.target.value })}
              placeholder="https://your-brand.com"
            />
          </label>
          <label>
            <span id="dx-guideline-label">Brand guideline</span>
            <textarea
              aria-labelledby="dx-guideline-label"
              value={context.guideline}
              maxLength={30000}
              disabled={props.busy || uploading}
              onChange={(event) => onChange({ ...context, guideline: event.target.value })}
              rows={5}
              placeholder={
                'Primary: #006D6A\nAccent: #90321E\nHeading font: Inter\nBody font: Inter\nCard radius: 16px\nMotion: subtle-premium'
              }
            />
          </label>
          <small>Các nhãn trong ví dụ được trích xuất tự động. Nội dung khác được giữ làm context để rà soát.</small>
          <label>
            <span id="dx-avoid-label">Điều cần tránh (mỗi dòng một quy tắc)</span>
            <textarea
              aria-labelledby="dx-avoid-label"
              value={context.avoid.join('\n')}
              disabled={props.busy || uploading}
              onChange={(event) => onChange({ ...context, avoid: event.target.value.split('\n') })}
              rows={3}
              placeholder={'Không dùng stock photos\nKhông lặp hero trên mọi trang'}
            />
          </label>
          <details>
            <summary>Import design system / CSS hiện có</summary>
            <label>
              <span id="dx-tokens-label">Design system JSON</span>
              <textarea
                aria-labelledby="dx-tokens-label"
                value={props.tokensText}
                disabled={props.busy || uploading}
                onChange={(event) => props.onTokensChange(event.target.value)}
                rows={7}
                spellCheck={false}
                placeholder={'{"colors":{"primary":"#006D6A"},"typography":{"heading":"Inter","body":"Inter"}}'}
              />
            </label>
            <label>
              <span id="dx-css-label">CSS token source</span>
              <textarea
                aria-labelledby="dx-css-label"
                value={context.existing_code}
                maxLength={100000}
                disabled={props.busy || uploading}
                onChange={(event) => onChange({ ...context, existing_code: event.target.value })}
                rows={5}
                spellCheck={false}
                placeholder={':root { --brand-primary: #006D6A; --font-body: Inter; --radius-card: 16px; }'}
              />
            </label>
          </details>
          <div className="dx-asset-inputs">
            <label>
              Logo
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                disabled={props.busy || uploading}
                onChange={(event) => {
                  void uploadImage(event.target.files?.[0], 'logo');
                  event.target.value = '';
                }}
              />
            </label>
            <label>
              Screenshot
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                disabled={props.busy || uploading}
                onChange={(event) => {
                  void uploadImage(event.target.files?.[0], 'screenshot');
                  event.target.value = '';
                }}
              />
            </label>
          </div>
          <small>
            Ảnh được lấy mẫu màu và lưu nguồn. Nhận diện font, bố cục và hình học logo cần review trực quan.
          </small>
          <div className="dx-context-assets">
            {context.assets.map((asset, index) => (
              <div key={`${asset.name}-${index}`}>
                <img src={asset.data_url} alt={`${asset.kind}: ${asset.name}`} />
                <span>{asset.name}</span>
                <button
                  disabled={props.busy || uploading}
                  aria-label={`Xóa ${asset.name}`}
                  onClick={() =>
                    onChange({ ...context, assets: context.assets.filter((_, itemIndex) => itemIndex !== index) })
                  }
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          {(props.error || uploadError) && (
            <div className="dx-error" role="alert">
              {props.error || uploadError}
            </div>
          )}
          <button className="dx-primary-side" onClick={props.onAnalyze} disabled={props.busy || uploading}>
            {props.busy ? 'Đang phân tích…' : 'Phân tích Brand DNA & Reference'}
          </button>
        </section>

        <section className="dx-intelligence-results" aria-label="Design intelligence results" aria-live="polite">
          {props.stale && (
            <div className="dx-warning">
              Context đã thay đổi. Phân tích lại để cập nhật kết quả; lần build tiếp theo sẽ dùng context mới.
            </div>
          )}
          {!system && !references && (
            <div className="dx-quality-note">
              Thêm URL bằng ô Reference bên trái, sau đó chạy phân tích. Token chưa có bằng chứng được ghi là unresolved
              hoặc factory_default.
            </div>
          )}
          {system && (
            <>
              <div className="dx-panel-head">
                <span>DESIGN SYSTEM {system.schema_version}</span>
                <h3>{system.brand.name || 'Brand chưa đặt tên'}</h3>
                <p>
                  {system.brand.source_status} · {system.brand.personality.join(', ') || 'Personality chưa xác định'}
                </p>
              </div>
              <a
                className="dx-primary-side"
                href={`${props.artifactBase}/design-system.json`}
                target="_blank"
                rel="noreferrer"
              >
                Mở design-system.json
              </a>
              <a className="dx-artifact-link" href={`${props.artifactBase}/DESIGN.md`} target="_blank" rel="noreferrer">
                Mở DESIGN.md
              </a>
              {Object.entries(system.foundations)
                .filter(([group]) => ['colors', 'typography', 'radius', 'motion'].includes(group))
                .map(([group, tokens]) => (
                  <details key={group} open={group === 'colors'}>
                    <summary>{group}</summary>
                    <div className="dx-token-list">
                      {Object.entries(tokens).map(([name, token]) =>
                        typeof token === 'string' ? null : (
                          <div key={name}>
                            <strong>{name}</strong>
                            <span>
                              {group === 'colors' &&
                                typeof token.value === 'string' &&
                                /^#[\da-f]{3,6}$/i.test(token.value) && <i style={{ backgroundColor: token.value }} />}
                              {token.value ?? 'Chưa xác định'}
                            </span>
                            <small>
                              {token.status} · {token.source}
                            </small>
                          </div>
                        ),
                      )}
                    </div>
                  </details>
                ))}
              {!!system.brand.conflicts.length && (
                <details open>
                  <summary>Xung đột đã giải quyết ({system.brand.conflicts.length})</summary>
                  <ul>
                    {system.brand.conflicts.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </details>
              )}
              {!!system.brand.evidence.length && (
                <details>
                  <summary>Asset evidence</summary>
                  <ul>
                    {system.brand.evidence.map((item) => (
                      <li key={item.subject}>
                        {item.subject}: {item.value}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
              <details>
                <summary>Cần xác minh ({system.unresolved_items.length})</summary>
                <ul>
                  {system.unresolved_items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </details>
            </>
          )}
          {references && (
            <>
              <h3>Reference DNA</h3>
              {!references.references.length && <p>Chưa cung cấp URL reference hoặc website hiện có.</p>}
              {references.references.map((reference) => (
                <article className="dx-reference-dna" key={reference.url}>
                  <a href={reference.url} target="_blank" rel="noreferrer">
                    {reference.title || reference.url}
                  </a>
                  <small>
                    {reference.role} · {reference.status}
                  </small>
                  <div className="dx-reference-shots">
                    {reference.screenshots.map((path) => (
                      <a key={path} href={`${props.artifactBase}/${path}`} target="_blank" rel="noreferrer">
                        <img
                          loading="lazy"
                          crossOrigin="anonymous"
                          src={`${props.artifactBase}/${path}`}
                          alt={`${reference.url} — ${path.includes('mobile') ? 'mobile' : 'desktop'}`}
                        />
                      </a>
                    ))}
                  </div>
                  {!!reference.patterns.length && (
                    <ul>
                      {reference.patterns.map((pattern) => (
                        <li key={pattern}>{pattern}</li>
                      ))}
                    </ul>
                  )}
                  {reference.warnings.map((warning) => (
                    <p className="dx-quality-note" key={warning}>
                      {warning}
                    </p>
                  ))}
                  <details>
                    <summary>Xem dữ liệu đo ({reference.observations.length})</summary>
                    <div className="dx-token-list">
                      {reference.observations.map((item, index) => (
                        <div key={`${item.subject}-${index}`}>
                          <strong>{item.subject}</strong>
                          <span>{item.value}</span>
                          <small>
                            {item.certainty} · {item.source}
                          </small>
                        </div>
                      ))}
                    </div>
                  </details>
                </article>
              ))}
            </>
          )}
        </section>
      </div>
    </div>
  );
}
