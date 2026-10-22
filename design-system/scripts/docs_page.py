"""Renders docs/index.html (the living style guide) from resolved tokens. Called by build.py."""
from __future__ import annotations

import html
import json
from pathlib import Path

from dslib import ROOT, color_hex, contrast, css_name

ROLE_GROUPS = ["surface", "text", "border", "action", "feedback"]


def _swatches(resolved: dict, prefix: str) -> str:
    rows = []
    for group in ROLE_GROUPS:
        cells = []
        for path, (ttype, val) in resolved["light"].items():
            if ttype != "color" or not path.startswith(group + "."):
                continue
            light, dark = color_hex(val), color_hex(resolved["dark"][path][1])
            cells.append(
                f'<li class="sw"><span class="sw__chip" style="background: var({css_name(path, prefix)})"></span>'
                f'<code>{path}</code><span class="ds-text-body-sm ds-text-secondary ds-tabular">{light} / {dark}</span></li>')
        rows.append(f'<h3 class="ds-text-title-sm">{group}</h3><ul class="sw-grid">{"".join(cells)}</ul>')
    return "\n".join(rows)


def _contrast_table(resolved: dict) -> str:
    pairs = json.loads((ROOT / "contrast-pairs.json").read_text(encoding="utf-8"))["pairs"]
    body = []
    for p in pairs:
        cells = []
        for mode in ("light", "dark"):
            r = contrast(color_hex(resolved[mode][p["fg"]][1]), color_hex(resolved[mode][p["bg"]][1]))
            cells.append(f"<td class='ds-tabular'>{r:.2f}:1</td>")
        body.append(f"<tr><td><code>{p['fg']}</code></td><td><code>{p['bg']}</code></td>{''.join(cells)}"
                    f"<td class='ds-tabular'>{p['min']}:1</td><td>{html.escape(p['why'])}</td></tr>")
    return ("<table class='ct'><thead><tr><th>Foreground</th><th>Background</th><th>Light</th><th>Dark</th>"
            "<th>Min</th><th>Why</th></tr></thead><tbody>" + "".join(body) + "</tbody></table>")


TYPE_ROLES = ["display", "title-lg", "title-md", "title-sm", "body-lg", "body-md", "body-sm", "label-lg", "label-md", "label-sm"]


def _type_scale(resolved: dict) -> str:
    rows = []
    for role in TYPE_ROLES:
        v = resolved["light"][f"type.{role}"][1]
        rows.append(f'<div class="ts"><span class="ds-text-body-sm ds-text-secondary ts__meta ds-tabular">{role}<br>'
                    f'{v["fontSize"]["value"]}{v["fontSize"]["unit"]} / {v["lineHeight"]} / {v["fontWeight"]}</span>'
                    f'<p class="ds-text-{role}">Đặt lịch khám nhanh, rõ ràng</p></div>')
    return "\n".join(rows)


COMPONENTS = """
<section class="ds-stack" aria-labelledby="c-button"><h3 class="ds-text-title-sm" id="c-button">Button</h3>
  <div class="ds-cluster">
    <button class="ds-button ds-button--primary" type="button">Primary</button>
    <button class="ds-button ds-button--secondary" type="button">Secondary</button>
    <button class="ds-button ds-button--tertiary" type="button">Tertiary</button>
    <button class="ds-button ds-button--danger" type="button">Hủy lịch</button>
    <button class="ds-button ds-button--primary" type="button" disabled>Disabled</button>
    <button class="ds-button ds-button--primary" type="button" aria-busy="true">Đang gửi</button>
  </div>
  <div class="ds-cluster">
    <button class="ds-button ds-button--secondary ds-button--sm" type="button">Small</button>
    <button class="ds-button ds-button--secondary" type="button">Medium</button>
    <button class="ds-button ds-button--primary ds-button--lg" type="button">Large<svg class="ds-icon" aria-hidden="true"><use href="#ds-i-arrow-right"/></svg></button>
    <button class="ds-icon-button" type="button" aria-label="Tìm kiếm"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-search"/></svg></button>
  </div>
</section>
<section class="ds-stack" aria-labelledby="c-field"><h3 class="ds-text-title-sm" id="c-field">Field</h3>
  <div class="demo-cols">
    <div class="ds-field"><label class="ds-field__label" for="f1">Họ và tên</label><input class="ds-field__control" id="f1" placeholder="Ví dụ: Nguyễn Văn An" aria-describedby="f1h"><p class="ds-field__hint" id="f1h">Như trên giấy tờ tùy thân.</p></div>
    <div class="ds-field"><label class="ds-field__label" for="f2">Số điện thoại</label><input class="ds-field__control" id="f2" value="09012" aria-invalid="true" aria-describedby="f2e"><p class="ds-field__error" id="f2e"><svg class="ds-icon ds-icon--sm" aria-hidden="true"><use href="#ds-i-alert"/></svg>Nhập từ 9 đến 16 ký tự số.</p></div>
    <div class="ds-field"><label class="ds-field__label" for="f3">Chuyên khoa</label><div class="ds-field__wrap ds-field__wrap--select"><select class="ds-field__control" id="f3"><option>Tổng quát</option><option>Mắt</option></select></div></div>
    <div class="ds-field"><label class="ds-field__label" for="f4">Mã hồ sơ</label><input class="ds-field__control" id="f4" value="CF-0001" disabled></div>
  </div>
</section>
<section class="ds-stack" aria-labelledby="c-chip"><h3 class="ds-text-title-sm" id="c-chip">Chip and badge</h3>
  <div class="ds-cluster" role="group" aria-label="Ví dụ bộ lọc">
    <button class="ds-chip" type="button" aria-pressed="true">Sắp tới <span class="ds-chip__count">2</span></button>
    <button class="ds-chip" type="button" aria-pressed="false">Đã khám <span class="ds-chip__count">1</span></button>
  </div>
  <div class="ds-cluster">
    <span class="ds-badge ds-badge--success"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-check-circle"/></svg>Đã xác nhận</span>
    <span class="ds-badge ds-badge--warning"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-clock"/></svg>Chờ xác nhận</span>
    <span class="ds-badge ds-badge--danger"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-x-circle"/></svg>Đã hủy</span>
    <span class="ds-badge ds-badge--info"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-info"/></svg>Mới</span>
    <span class="ds-badge ds-badge--neutral"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-check-circle"/></svg>Đã khám</span>
  </div>
</section>
<section class="ds-stack" aria-labelledby="c-feedback"><h3 class="ds-text-title-sm" id="c-feedback">Banner, toast, empty state</h3>
  <div class="ds-banner ds-banner--success" role="status"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-check-circle"/></svg><div><p class="ds-text-label-lg">Đã đặt lịch</p><p class="ds-text-body-sm">Phòng khám sẽ gọi xác nhận trong 2 giờ làm việc.</p></div></div>
  <div class="ds-banner ds-banner--warning" role="status"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-alert"/></svg><div><p class="ds-text-label-lg">Còn thiếu giấy tờ</p><p class="ds-text-body-sm">Mang theo kết quả xét nghiệm gần nhất nếu có.</p></div></div>
  <div class="ds-banner ds-banner--danger" role="alert"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-x-circle"/></svg><div><p class="ds-text-label-lg">Không gửi được yêu cầu</p><p class="ds-text-body-sm">Kiểm tra kết nối rồi thử lại. Thông tin bạn nhập vẫn được giữ.</p></div></div>
  <div class="ds-toast" role="status"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-check-circle"/></svg>Đã sao chép mã hồ sơ</div>
  <div class="ds-card ds-card--flat"><div class="ds-empty"><span class="ds-empty__icon"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-calendar"/></svg></span><p class="ds-text-title-sm" style="color: var(--ds-text-primary)">Chưa có lịch phù hợp</p><p class="ds-text-body-md">Thử xóa bộ lọc để xem tất cả lịch hẹn.</p><button class="ds-button ds-button--secondary" type="button">Xóa bộ lọc</button></div></div>
</section>
<section class="ds-stack" aria-labelledby="c-list"><h3 class="ds-text-title-sm" id="c-list">Card, list, tab bar</h3>
  <div class="demo-cols">
    <section class="ds-card" aria-label="Ví dụ thẻ"><div class="ds-split"><p class="ds-text-title-md ds-tabular">09:30</p><span class="ds-badge ds-badge--success"><svg class="ds-icon" aria-hidden="true"><use href="#ds-i-check-circle"/></svg>Đã xác nhận</span></div><p class="ds-text-title-sm">Khám tổng quát</p><p class="ds-text-body-sm ds-text-secondary">20/10/2026 · Phòng khám An Bình</p></section>
    <ul class="ds-list">
      <li><button class="ds-list-item" type="button"><span class="ds-list-item__leading"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-document"/></svg></span><span class="ds-list-item__body"><span class="ds-text-label-lg" style="display:block">Giấy tờ cần mang</span><span class="ds-text-body-sm ds-text-secondary">2 mục</span></span><svg class="ds-icon ds-list-item__trailing" aria-hidden="true"><use href="#ds-i-chevron-right"/></svg></button></li>
      <li class="ds-list-item"><span class="ds-avatar" aria-hidden="true">TM</span><span class="ds-list-item__body"><span class="ds-text-label-lg" style="display:block">Trần Thu Mai</span><span class="ds-text-body-sm ds-text-secondary">Người thân</span></span></li>
    </ul>
  </div>
  <nav class="ds-tab-bar" aria-label="Ví dụ thanh điều hướng" style="max-width: 420px; border: var(--ds-border-width-100) solid var(--ds-border-subtle); border-radius: var(--ds-shape-card)">
    <a class="ds-tab-bar__item" href="#c-list" aria-current="page"><span class="ds-tab-bar__icon"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-home"/></svg></span>Trang chủ</a>
    <a class="ds-tab-bar__item" href="#c-list"><span class="ds-tab-bar__icon"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-calendar"/></svg></span>Lịch hẹn</a>
    <a class="ds-tab-bar__item" href="#c-list"><span class="ds-tab-bar__icon"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-user"/></svg></span>Hồ sơ</a>
  </nav>
</section>
"""


def render(resolved: dict, prefix: str, version: str) -> str:
    sprite = (ROOT / "components" / "icons.svg").read_text(encoding="utf-8").strip()
    n_tokens = len(resolved["light"])
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Design system reference</title>
<!-- GENERATED by design-system/scripts/build.py. Edit scripts/docs_page.py, not this file. -->
<link rel="stylesheet" href="../fonts/fonts.css">
<link rel="stylesheet" href="../generated/tokens.css">
<link rel="stylesheet" href="../components/components.css">
<style>
.doc {{ max-width: var(--ds-size-content-max); margin: 0 auto; padding: var(--ds-spacing-stack-xl) var(--ds-spacing-gutter); }}
.doc > section {{ padding-block: var(--ds-spacing-stack-xl); border-top: var(--ds-border-width-100) solid var(--ds-border-subtle); }}
.sw-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--ds-spacing-stack-sm); margin: 0 0 var(--ds-spacing-stack-lg); padding: 0; list-style: none; }}
.sw {{ display: grid; grid-template-columns: 40px 1fr; grid-template-rows: auto auto; column-gap: var(--ds-spacing-inline-md); align-items: center; }}
.sw__chip {{ grid-row: span 2; width: 40px; height: 40px; border-radius: var(--ds-shape-control); border: var(--ds-border-width-100) solid var(--ds-border-subtle); }}
code {{ font-family: var(--ds-font-family-mono); font-size: var(--ds-font-size-200); }}
.ts {{ display: grid; grid-template-columns: 160px 1fr; gap: var(--ds-spacing-inline-md); align-items: baseline; padding-block: var(--ds-spacing-stack-xs); }}
.demo-cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: var(--ds-spacing-stack-md); align-items: start; }}
.ct-wrap {{ overflow-x: auto; }}
.ct {{ width: 100%; border-collapse: collapse; font-size: var(--ds-font-size-300); }}
.ct th, .ct td {{ padding: var(--ds-space-200) var(--ds-space-300); border-bottom: var(--ds-border-width-100) solid var(--ds-border-subtle); text-align: left; vertical-align: top; }}
@media (max-width: 600px) {{ .ts {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body class="ds-root">
{sprite}
<main class="doc ds-stack ds-stack--lg">
  <header class="ds-stack ds-stack--sm">
    <div class="ds-split"><p class="ds-text-label-sm ds-text-secondary">Design system · v{html.escape(version)} · {n_tokens} tokens per mode</p>
      <button class="ds-button ds-button--secondary ds-button--sm" id="theme" type="button" aria-pressed="false"><svg class="ds-icon ds-icon--sm" aria-hidden="true"><use href="#ds-i-moon"/></svg><span>Giao diện tối</span></button></div>
    <h1 class="ds-text-title-lg">Tokens, components and the rules behind them</h1>
    <p class="ds-text-body-lg ds-text-secondary">Generated from the DTCG token source. Every contrast ratio below is computed at build time, so this page cannot drift from the code.</p>
  </header>
  <section class="ds-stack" aria-labelledby="h-color"><h2 class="ds-text-title-md" id="h-color">Color roles</h2>
    <p class="ds-text-body-md ds-text-secondary">Components use roles only. Values shown as light / dark.</p>
    {_swatches(resolved, prefix)}
  </section>
  <section class="ds-stack" aria-labelledby="h-contrast"><h2 class="ds-text-title-md" id="h-contrast">Contrast checks</h2>
    <div class="ct-wrap" role="region" aria-labelledby="h-contrast" tabindex="0">{_contrast_table(resolved)}</div>
  </section>
  <section class="ds-stack" aria-labelledby="h-type"><h2 class="ds-text-title-md" id="h-type">Type scale</h2>
    <p class="ds-text-body-md ds-text-secondary">Be Vietnam Pro. Body line height never drops below 1.5 because Vietnamese stacks diacritics.</p>
    {_type_scale(resolved)}
  </section>
  <section class="ds-stack ds-stack--lg" aria-labelledby="h-comp"><h2 class="ds-text-title-md" id="h-comp">Components and states</h2>
    {COMPONENTS}
  </section>
</main>
<script>
const btn = document.querySelector('#theme');
function setTheme(dark) {{
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  btn.setAttribute('aria-pressed', String(dark));
  btn.querySelector('span').textContent = dark ? 'Giao diện sáng' : 'Giao diện tối';
  btn.querySelector('use').setAttribute('href', dark ? '#ds-i-sun' : '#ds-i-moon');
}}
btn.onclick = () => setTheme(document.documentElement.dataset.theme !== 'dark');
setTheme(matchMedia('(prefers-color-scheme: dark)').matches);
</script>
</body>
</html>
"""
