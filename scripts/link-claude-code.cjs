#!/usr/bin/env node
/**
 * Cài skill "uiux-workspace" cho Claude Code ở mức người dùng, để ở bất kỳ dự án nào, khi được nhờ
 * thiết kế UI/UX, Claude tự mở repo này và làm theo START-HERE.md.
 *
 * Dùng:
 *   node scripts/link-claude-code.cjs             ghi ~/.claude/skills/uiux-workspace/SKILL.md
 *   node scripts/link-claude-code.cjs --remove    gỡ skill đã cài
 *   node scripts/link-claude-code.cjs --dir <thư mục skills>   cài vào chỗ khác (ví dụ <dự án>/.claude/skills)
 *
 * Skill chỉ ghi đường dẫn tới repo, không chép nội dung: sửa TASTE.md hay WORKFLOWS.md là có hiệu lực ngay.
 * Dời repo sang chỗ khác thì chạy lại lệnh này. Không ghi đè một SKILL.md không do lệnh này sinh ra.
 */
'use strict';
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const REPO = path.resolve(__dirname, '..');
const NAME = 'uiux-workspace';
const MARKER = '<!-- uiux-workspace: sinh bởi scripts/link-claude-code.cjs';

function render(repo = REPO) {
  const template = fs.readFileSync(path.join(REPO, 'integrations', 'claude-code', 'SKILL.template.md'), 'utf8');
  return template.replace(/\r\n/g, '\n').split('{{REPO}}').join(repo.split(path.sep).join('/'));
}

function target(dir) {
  return path.join(path.resolve(dir || path.join(os.homedir(), '.claude', 'skills')), NAME, 'SKILL.md');
}

function ours(file) {
  return !fs.existsSync(file) || fs.readFileSync(file, 'utf8').includes(MARKER);
}

function link(dir) {
  const file = target(dir);
  if (!ours(file)) throw new Error(`${file} đã có và không do lệnh này sinh ra; xem rồi tự xoá nếu muốn thay`);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, render());
  return file;
}

function remove(dir) {
  const file = target(dir);
  if (!fs.existsSync(file)) return '';
  if (!ours(file)) throw new Error(`${file} không do lệnh này sinh ra; không xoá`);
  fs.rmSync(path.dirname(file), { recursive: true });
  return file;
}

function main(argv) {
  let dir = '';
  let doRemove = false;
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--dir') dir = argv[++i] || '';
    else if (argv[i] === '--remove') doRemove = true;
    else if (argv[i] === '-h' || argv[i] === '--help') {
      process.stdout.write(fs.readFileSync(__filename, 'utf8').split('*/')[0].replace(/^#!.*\n\/\*\*?/, '').replace(/^ \* ?/gm, ''));
      return 0;
    } else throw new Error(`không hiểu tuỳ chọn ${argv[i]}`);
  }
  if (doRemove) {
    const gone = remove(dir);
    process.stdout.write(gone ? `Đã gỡ ${gone}\n` : 'Chưa cài, không có gì để gỡ.\n');
    return 0;
  }
  process.stdout.write(`Đã ghi ${link(dir)}\nMở phiên Claude Code mới để skill có hiệu lực. Gỡ: node scripts/link-claude-code.cjs --remove\n`);
  return 0;
}

module.exports = { render, target, link, remove };
if (require.main === module) {
  try { process.exitCode = main(process.argv.slice(2)); } catch (err) {
    process.stderr.write(`link-claude-code: ${err.message}\n`);
    process.exitCode = 2;
  }
}
