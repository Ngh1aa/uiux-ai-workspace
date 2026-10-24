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
<section class="ds-stack" aria-labelledby="c-app"><h3 class="ds-text-title-sm" id="c-app">App controls (v0.2): segmented, switch, progress, skeleton, sheet</h3>
  <div class="demo-cols">
    <div class="ds-stack ds-stack--md">
      <div class="ds-segmented" role="group" aria-label="Ví dụ chọn khoảng thời gian">
        <button class="ds-segmented__item" type="button" aria-pressed="false">Tuần</button>
        <button class="ds-segmented__item" type="button" aria-pressed="true">Tháng</button>
        <button class="ds-segmented__item" type="button" aria-pressed="false">Năm</button>
      </div>
      <label class="ds-split"><span class="ds-text-label-lg">Thông báo giao dịch</span><span class="ds-switch"><input type="checkbox" role="switch" checked><span class="ds-switch__thumb" aria-hidden="true"></span></span></label>
      <label class="ds-split"><span class="ds-text-label-lg">Đăng nhập bằng sinh trắc học</span><span class="ds-switch"><input type="checkbox" role="switch"><span class="ds-switch__thumb" aria-hidden="true"></span></span></label>
      <label class="ds-split"><span class="ds-text-label-lg ds-text-secondary">Đồng bộ ngân hàng (không khả dụng)</span><span class="ds-switch"><input type="checkbox" role="switch" disabled><span class="ds-switch__thumb" aria-hidden="true"></span></span></label>
    </div>
    <div class="ds-stack ds-stack--md">
      <div class="ds-stack ds-stack--xs"><div class="ds-split"><span class="ds-text-label-md">Ăn uống</span><span class="ds-text-label-md ds-tabular">62%</span></div><div class="ds-progress" role="progressbar" aria-label="Ăn uống" aria-valuenow="62" aria-valuemin="0" aria-valuemax="100"><span class="ds-progress__bar" style="--value: 62%"></span></div></div>
      <div class="ds-stack ds-stack--xs"><div class="ds-split"><span class="ds-text-label-md">Mua sắm</span><span class="ds-text-label-md ds-tabular">88% · sắp hết</span></div><div class="ds-progress ds-progress--warning" role="progressbar" aria-label="Mua sắm" aria-valuenow="88" aria-valuemin="0" aria-valuemax="100"><span class="ds-progress__bar" style="--value: 88%"></span></div></div>
      <div class="ds-stack ds-stack--xs"><div class="ds-split"><span class="ds-text-label-md">Giải trí</span><span class="ds-text-label-md ds-tabular">112% · vượt</span></div><div class="ds-progress ds-progress--danger" role="progressbar" aria-label="Giải trí" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" aria-valuetext="112%, vượt ngân sách"><span class="ds-progress__bar" style="--value: 100%"></span></div></div>
      <div class="ds-list-item" role="status" aria-busy="true" aria-label="Đang tải"><span class="ds-skeleton ds-skeleton--circle" style="width: 40px; height: 40px" aria-hidden="true"></span><span class="ds-list-item__body ds-stack ds-stack--xs" aria-hidden="true"><span class="ds-skeleton" style="width: 60%"></span><span class="ds-skeleton" style="width: 35%"></span></span></div>
    </div>
    <div class="ds-sheet" role="dialog" aria-labelledby="sheet-demo-title" style="box-shadow: var(--ds-elevation-floating); border: var(--ds-border-width-100) solid var(--ds-border-subtle)">
      <span class="ds-sheet__grabber" aria-hidden="true"></span>
      <div class="ds-sheet__header"><h4 class="ds-text-title-sm" id="sheet-demo-title">Lọc giao dịch</h4><button class="ds-icon-button" type="button" aria-label="Đóng"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-x-circle"/></svg></button></div>
      <div class="ds-cluster"><button class="ds-chip" type="button" aria-pressed="true">Chi tiêu</button><button class="ds-chip" type="button" aria-pressed="false">Thu nhập</button></div>
      <button class="ds-button ds-button--primary ds-button--block" type="button">Xem 24 giao dịch</button>
    </div>
  </div>
</section>
<section class="ds-stack" aria-labelledby="c-web"><h3 class="ds-text-title-sm" id="c-web">Web controls (v0.3): checkbox, radio, tabs, menu, tooltip, dialog, table</h3>
  <div class="demo-cols">
    <div class="ds-stack ds-stack--md">
      <fieldset class="ds-fieldset"><legend>Nhắc lịch qua</legend>
        <label class="ds-check"><input type="checkbox" checked><span class="ds-check__box" aria-hidden="true"><svg class="ds-icon"><use href="#ds-i-check"/></svg></span><span>Tin nhắn</span></label>
        <label class="ds-check"><input type="checkbox"><span class="ds-check__box" aria-hidden="true"><svg class="ds-icon"><use href="#ds-i-check"/></svg></span><span>Email</span></label>
        <label class="ds-check"><input type="checkbox" disabled><span class="ds-check__box" aria-hidden="true"><svg class="ds-icon"><use href="#ds-i-check"/></svg></span><span>Zalo (chưa kết nối)</span></label>
      </fieldset>
      <fieldset class="ds-fieldset"><legend>Hình thức khám</legend>
        <label class="ds-check ds-check--radio"><input type="radio" name="demo-mode" checked><span class="ds-check__box" aria-hidden="true"></span><span>Tại phòng khám</span></label>
        <label class="ds-check ds-check--radio"><input type="radio" name="demo-mode"><span class="ds-check__box" aria-hidden="true"></span><span>Gọi video</span></label>
      </fieldset>
    </div>
    <div class="ds-stack ds-stack--md">
      <div class="ds-tabs" role="tablist" aria-label="Ví dụ tab">
        <button class="ds-tabs__tab" role="tab" type="button" aria-selected="true" aria-controls="demo-tab-1" id="demo-tab-a">Sắp tới</button>
        <button class="ds-tabs__tab" role="tab" type="button" aria-selected="false" aria-controls="demo-tab-2" id="demo-tab-b" tabindex="-1">Đã khám</button>
      </div>
      <div class="ds-tabs__panel" role="tabpanel" id="demo-tab-1" aria-labelledby="demo-tab-a"><p class="ds-text-body-md">2 lịch hẹn trong tuần này.</p></div>
      <div class="ds-tabs__panel" role="tabpanel" id="demo-tab-2" aria-labelledby="demo-tab-b" hidden><p class="ds-text-body-md">Chưa có lần khám nào.</p></div>
      <div class="ds-cluster">
        <div class="ds-menu-anchor">
          <button class="ds-button ds-button--secondary" type="button" aria-haspopup="menu" aria-expanded="true" aria-controls="demo-menu">Thao tác<svg class="ds-icon" aria-hidden="true"><use href="#ds-i-chevron-down"/></svg></button>
          <ul class="ds-menu" role="menu" id="demo-menu" style="position: static; margin-top: var(--ds-space-100)">
            <li role="none"><button class="ds-menu__item" role="menuitem" type="button">Đổi giờ</button></li>
            <li role="none"><button class="ds-menu__item" role="menuitem" type="button">Thêm người đi cùng</button></li>
            <li role="separator" class="ds-menu__divider"></li>
            <li role="none"><button class="ds-menu__item ds-menu__item--danger" role="menuitem" type="button">Huỷ lịch</button></li>
          </ul>
        </div>
        <span class="ds-tooltip-anchor"><button class="ds-icon-button" type="button" aria-label="Thông tin" aria-describedby="demo-tip"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-info"/></svg></button><span class="ds-tooltip" role="tooltip" id="demo-tip">Lịch huỷ trước 2 giờ được hoàn phí</span></span>
      </div>
    </div>
    <div class="ds-dialog ds-dialog--static" role="dialog" aria-labelledby="demo-dialog-title">
      <div class="ds-dialog__body">
        <div class="ds-dialog__header"><h4 class="ds-text-title-sm" id="demo-dialog-title">Huỷ lịch khám 09:30?</h4><button class="ds-icon-button" type="button" aria-label="Đóng"><svg class="ds-icon ds-icon--lg" aria-hidden="true"><use href="#ds-i-x"/></svg></button></div>
        <p class="ds-text-body-md ds-text-secondary">Bạn có thể đặt lại sau. Phí đặt lịch được hoàn trong 3 ngày làm việc.</p>
        <div class="ds-dialog__actions"><button class="ds-button ds-button--secondary" type="button">Giữ lịch</button><button class="ds-button ds-button--danger" type="button">Huỷ lịch</button></div>
      </div>
    </div>
  </div>
  <div class="ds-table-wrap">
    <table class="ds-table">
      <caption>Lịch sử thanh toán</caption>
      <thead><tr><th scope="col">Ngày</th><th scope="col">Dịch vụ</th><th scope="col" class="ds-table__num">Số tiền</th></tr></thead>
      <tbody>
        <tr><td class="ds-tabular">12/10/2026</td><td>Khám tổng quát</td><td class="ds-table__num">350.000 ₫</td></tr>
        <tr><td class="ds-tabular">28/09/2026</td><td>Xét nghiệm máu</td><td class="ds-table__num">1.240.000 ₫</td></tr>
      </tbody>
    </table>
  </div>
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
