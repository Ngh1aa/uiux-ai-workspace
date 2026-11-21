#!/usr/bin/env node
/**
 * Tạo khung một dự án thiết kế từ starter kit: trang mẫu, design system chép kèm, brand brief
 * và ghi chú giao. Dự án chạy độc lập, không cần nằm trong repo này.
 *
 * Dùng:
 *   node scripts/new-project.cjs <thư mục dự án> --kind <loại> [--kind <loại> ...] [--force]
 *
 * Loại: mobile, web, landing, desktop, ios, android (xem design-system/starter/README.md).
 *
 * Ghi vào thư mục dự án:
 *   <loại>.html                 trang starter, đường dẫn CSS đã đổi sang ds/
 *   brand.css, app.css, ...     lớp thương hiệu (chỗ giữ chỗ, điền theo brand brief) và khối bố cục
 *   ds/                         fonts, tokens.css, components.css chép từ design system, kèm SOURCE.json
 *   BRAND-BRIEF.md              mẫu brand brief để điền
 *   DESIGN-NOTES.md             ghi chú giao: kế hoạch thị giác (CRAFT), màn × trạng thái, cổng duyệt
 *                               hướng, kết quả soát, luồng (FLOW), phần chưa kiểm
 *
 * Không ghi đè file đã có, trừ khi thêm --force. Phần trong ds/ là bản chép: sửa token hay
 * component thì sửa ở design system rồi chạy lại lệnh này với --force, không sửa trong ds/.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { findPython } = require('./doctor.cjs');

const REPO = path.resolve(__dirname, '..');
const DS = path.join(REPO, 'design-system');
const STARTER = path.join(DS, 'starter');
const KINDS = {
  mobile: { page: 'mobile.html', css: [] },
  web: { page: 'web.html', css: [] },
  landing: { page: 'landing.html', css: [] },
  desktop: { page: 'desktop.html', css: ['desktop.css'] },
  ios: { page: 'mobile-ios.html', css: ['native.css'] },
  android: { page: 'mobile-android.html', css: ['native.css'] },
};
const REWRITE = {
  '../fonts/fonts.css': 'ds/fonts/fonts.css',
  '../generated/tokens.css': 'ds/tokens.css',
  '../components/components.css': 'ds/components.css',
};

function parseArgs(argv) {
  const opts = { dir: '', kinds: [], force: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--kind') opts.kinds.push(argv[++i] || '');
    else if (arg === '--force') opts.force = true;
    else if (arg === '-h' || arg === '--help') opts.help = true;
    else if (arg.startsWith('--')) throw new Error(`không hiểu tuỳ chọn ${arg}`);
    else if (opts.dir) throw new Error('chỉ nhận một thư mục dự án');
    else opts.dir = arg;
  }
  const unknown = opts.kinds.filter((kind) => !KINDS[kind]);
  if (unknown.length) throw new Error(`không có loại ${unknown.join(', ')}; chọn trong: ${Object.keys(KINDS).join(', ')}`);
  return opts;
}

/** Đổi đường dẫn CSS của starter sang ds/. Còn link ra ngoài thư mục dự án thì dừng. */
function rewritePage(html) {
  let out = html;
  for (const [from, to] of Object.entries(REWRITE)) out = out.split(`href="${from}"`).join(`href="${to}"`);
  const outside = [...out.matchAll(/\b(?:href|src)="(\.\.\/[^"]*)"/g)].map((m) => m[1]);
  if (outside.length) throw new Error(`starter còn trỏ ra ngoài thư mục dự án: ${[...new Set(outside)].join(', ')}; cập nhật REWRITE trong new-project.cjs`);
  return out;
}

/** Khối ```text đầu tiên của một file: nguồn duy nhất của mẫu vẫn là CRAFT.md và FLOW.md. */
function textBlock(file) {
  const match = /```text\r?\n([\s\S]*?)```/.exec(fs.readFileSync(path.join(REPO, file), 'utf8'));
  if (!match) throw new Error(`không thấy khối text trong ${file}`);
  return match[1].replace(/\r\n/g, '\n').trimEnd();
}

/** Link tương đối trong mẫu trỏ vào repo; dự án nằm chỗ khác nên đổi thành đường dẫn tuyệt đối. */
function absoluteLinks(markdown, from) {
  return markdown.replace(/\]\((?!https?:|#|mailto:)([^)\s]+)\)/g, (all, target) => {
    const [file, anchor] = target.split('#');
    const full = path.resolve(from, file).split(path.sep).join('/');
    return `](${encodeURI(full)}${anchor ? `#${anchor}` : ''})`;
  });
}

function designNotes(kinds) {
  const repo = REPO.split(path.sep).join('/');
  return `# Ghi chú thiết kế

Một file cho cả dự án: điền dần khi làm, giao kèm khi xong. Quy trình ở \`${repo}/WORKFLOWS.md\`.
Điều chưa kiểm ghi \`UNKNOWN\`; hướng chưa ai chọn ghi \`CHƯA DUYỆT\`.

## 1. Việc và cỡ

- Yêu cầu:
- Cỡ việc (XS, S, M, L, XL) và track:
- Nền tảng: ${kinds.join(', ')}
- Giả định đã dùng:

## 2. Kế hoạch thị giác

Điền trước khi dựng, theo CRAFT.md mục 1.

\`\`\`text
${textBlock('CRAFT.md')}
\`\`\`

## 3. Màn × trạng thái

| Màn | Mặc định | Đang tải | Rỗng | Lỗi | Nội dung dài | Tối |
|---|---|---|---|---|---|---|
| | | | | | | |

## 4. Cổng duyệt hướng

- Màn quyết định chính:
- Các hướng đã dựng và ảnh:
- Hướng đề xuất, lý do:
- Trạng thái: \`CHƯA DUYỆT\`

## 5. Kết quả soát

- \`design-check\`: (dán dòng kết luận và đường dẫn qa/design-check.json)
- Cảnh báo giữ lại, kèm lý do:
- Ảnh đã mở (cỡ màn, sáng và tối):
- Rubric: tự chấm / duyệt độc lập:

## 6. Luồng

Theo FLOW.md mục "Kiểm trước khi giao"; từng điều \`PASS / FAIL / UNKNOWN\`.

\`\`\`text
${textBlock('FLOW.md')}
\`\`\`

## 7. Dữ liệu mẫu và phần mô phỏng

Ghi ở đây, không ghi trên màn.
`;
}

function copyDir(from, to, skip = new Set()) {
  fs.mkdirSync(to, { recursive: true });
  for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
    if (skip.has(entry.name)) continue;
    const src = path.join(from, entry.name);
    const dest = path.join(to, entry.name);
    if (entry.isDirectory()) copyDir(src, dest, skip);
    else fs.copyFileSync(src, dest);
  }
}

function repoCommit() {
  const res = spawnSync('git', ['-C', REPO, 'rev-parse', 'HEAD'], { encoding: 'utf8' });
  return res.status === 0 ? res.stdout.trim() : null;
}

function create(dir, kinds, { force = false } = {}) {
  if (!dir) throw new Error('thiếu thư mục dự án');
  if (!kinds.length) throw new Error(`thiếu --kind; chọn trong: ${Object.keys(KINDS).join(', ')}`);
  const target = path.resolve(dir);
  const files = new Map();
  for (const kind of kinds) {
    const spec = KINDS[kind];
    files.set(`${kind}.html`, rewritePage(fs.readFileSync(path.join(STARTER, spec.page), 'utf8')));
    for (const css of ['brand.css', 'app.css', ...spec.css]) files.set(css, fs.readFileSync(path.join(STARTER, css)));
  }
  files.set('BRAND-BRIEF.md', absoluteLinks(fs.readFileSync(path.join(REPO, 'BRAND-BRIEF.template.md'), 'utf8'), REPO));
  files.set('DESIGN-NOTES.md', designNotes(kinds));

  const existing = [...files.keys(), 'ds'].filter((name) => fs.existsSync(path.join(target, name)));
  if (existing.length && !force) throw new Error(`đã có sẵn trong ${target}: ${existing.join(', ')}. Thêm --force để ghi đè.`);

  fs.mkdirSync(target, { recursive: true });
  for (const [name, content] of files) fs.writeFileSync(path.join(target, name), content);
  const ds = path.join(target, 'ds');
  copyDir(path.join(DS, 'fonts'), path.join(ds, 'fonts'), new Set(['README.md', 'manifest.json']));
  fs.copyFileSync(path.join(DS, 'generated', 'tokens.css'), path.join(ds, 'tokens.css'));
  fs.copyFileSync(path.join(DS, 'components', 'components.css'), path.join(ds, 'components.css'));
  fs.writeFileSync(path.join(ds, 'SOURCE.json'), `${JSON.stringify({
    note: 'Bản chép từ design system của uiux-ai-workspace. Không sửa ở đây; sửa ở nguồn rồi chạy lại new-project.cjs --force.',
    repo: REPO.split(path.sep).join('/'),
    commit: repoCommit(),
  }, null, 2)}\n`);
  return { target, pages: kinds.map((kind) => `${kind}.html`), files: [...files.keys()] };
}

function main(argv) {
  const opts = parseArgs(argv);
  if (opts.help || !opts.dir) {
    process.stdout.write(fs.readFileSync(__filename, 'utf8').split('*/')[0].replace(/^#!.*\n\/\*\*?/, '').replace(/^ \* ?/gm, ''));
    return opts.help ? 0 : 2;
  }
  const result = create(opts.dir, opts.kinds, opts);
  const show = (file) => {
    const rel = path.relative(process.cwd(), file) || '.';
    const text = (rel.startsWith('..') ? file : rel).split(path.sep).join('/');
    return /s/.test(text) ? `"${text}"` : text;
  };
  const script = (name) => show(path.join(REPO, name));
  const pages = result.pages.map((page) => show(path.join(result.target, page))).join(' ');
  const found = findPython();
  const python = found ? `${found.command.join(' ')} -X utf8` : 'python';
  process.stdout.write([
    `Đã tạo ${result.target}`,
    `  ${result.files.join(', ')}, ds/`,
    '',
    'Việc tiếp theo:',
    '  1. Điền BRAND-BRIEF.md, rồi brand.css theo brief (giá trị hiện tại chỉ là chỗ giữ chỗ).',
    '  2. Điền kế hoạch thị giác trong DESIGN-NOTES.md trước khi dựng.',
    `  3. Thêm hoặc bớt icon xong: ${python} ${script('design-system/starter/inline-icons.py')} ${pages}`,
    `  4. Soát: node ${script('scripts/design-check.cjs')} ${pages}`,
    '',
  ].join('\n'));
  return 0;
}

module.exports = { KINDS, parseArgs, rewritePage, textBlock, absoluteLinks, designNotes, create };
if (require.main === module) {
  try { process.exitCode = main(process.argv.slice(2)); } catch (err) {
    process.stderr.write(`new-project: ${err.message}\n`);
    process.exitCode = 2;
  }
}
