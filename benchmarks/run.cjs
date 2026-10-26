#!/usr/bin/env node
/**
 * Soát và chụp ảnh một lần chạy bộ đề chuẩn.
 *
 * Dùng:  node benchmarks/run.cjs benchmarks/runs/<lần-chạy>
 *
 * Với mỗi đề có file <đề>/index.html trong thư mục lần chạy, chạy taste-check ở 390px, 1024px và 1280px,
 * cả sáng và tối; lưu ảnh JPEG vào <lần-chạy>/shots/ và kết quả vào <lần-chạy>/checks.json.
 * Cần Playwright (đặt NODE_PATH hoặc cài playwright).
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { spawnSync } = require('node:child_process');

const REPO = path.resolve(__dirname, '..');
const CHECKER = path.join(REPO, 'skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs');
const BRIEFS = fs.readdirSync(path.join(__dirname, 'briefs')).filter((f) => f.endsWith('.md')).map((f) => f.replace(/\.md$/, '')).sort();
// Đề thêm sau ghi "**Thêm vào:** YYYY-MM-DD"; lần chạy trước ngày đó không phải làm đề này (như report.py).
const BRIEF_SINCE = Object.fromEntries(BRIEFS.map((b) => {
  const m = fs.readFileSync(path.join(__dirname, 'briefs', `${b}.md`), 'utf8').match(/\*\*Thêm vào:\*\*\s*(\d{4}-\d{2}-\d{2})/);
  return [b, m ? m[1] : '0000-00-00'];
}));

function main() {
  const runArg = process.argv[2];
  if (!runArg) {
    process.stderr.write('Dùng: node benchmarks/run.cjs benchmarks/runs/<lần-chạy>\n');
    return 2;
  }
  const runDir = path.resolve(runArg);
  if (!fs.existsSync(runDir)) {
    process.stderr.write(`không có thư mục ${runArg}\n`);
    return 2;
  }
  const shots = path.join(runDir, 'shots');
  fs.rmSync(shots, { recursive: true, force: true });
  const git = (...args) => {
    const result = spawnSync('git', ['-C', REPO, ...args], { encoding: 'utf8' });
    if (result.status !== 0) throw new Error('không đọc được Git provenance của toolkit');
    return result.stdout.trim();
  };
  const summary = {
    run: path.basename(runDir), checked_at: new Date().toISOString(),
    source: {
      repo_commit: git('rev-parse', 'HEAD'),
      dirty: Boolean(git('status', '--porcelain')),
      checker_sha256: createHash('sha256').update(fs.readFileSync(CHECKER)).digest('hex'),
    },
    briefs: {},
  };
  let failed = false;
  const day = path.basename(runDir).slice(0, 10);
  for (const brief of BRIEFS.filter((b) => BRIEF_SINCE[b] <= day)) {
    const page = path.join(runDir, brief, 'index.html');
    if (!fs.existsSync(page)) {
      summary.briefs[brief] = { status: 'MISSING' };
      process.stdout.write(`${brief}: chưa có index.html\n`);
      failed = true;
      continue;
    }
    const json = path.join(runDir, `.${brief}.taste.json`);
    fs.rmSync(json, { force: true });
    const res = spawnSync(process.execPath, [
      CHECKER, page, '--root', REPO, '--width', '390', '--width', '1024', '--width', '1280', '--height', '900',
      '--screenshot', shots, '--format', 'jpeg', '--name', brief, '--json', json,
    ], { encoding: 'utf8' });
    process.stdout.write(res.stdout);
    if (!fs.existsSync(json)) {
      process.stderr.write(res.stderr);
      summary.briefs[brief] = { status: 'CHECK_FAILED' };
      failed = true;
      continue;
    }
    const data = JSON.parse(fs.readFileSync(json, 'utf8'));
    fs.rmSync(json);
    const issues = {};
    for (const result of data.results) {
      for (const screen of result.screens) {
        for (const item of [...screen.errors, ...screen.warnings]) {
          const key = `${screen.name}: ${item.message}`;
          issues[key] = issues[key] || { level: screen.errors.includes(item) ? 'lỗi' : 'cảnh báo', where: [] };
          issues[key].where.push(`${result.width}px ${result.theme}`);
        }
      }
    }
    summary.briefs[brief] = {
      status: res.status === 0 && data.errorCount === 0 ? 'PASS' : 'FAIL',
      checker_exit_code: res.status,
      axe: data.axe,
      errors: data.errorCount,
      warnings: data.warningCount,
      issues: Object.entries(issues).map(([message, v]) => ({ level: v.level, message, where: v.where })),
    };
    if (res.status !== 0 || data.errorCount) failed = true;
  }
  fs.writeFileSync(path.join(runDir, 'checks.json'), `${JSON.stringify(summary, null, 2)}\n`);
  process.stdout.write(`\nĐã ghi ${path.relative(REPO, path.join(runDir, 'checks.json'))} và ảnh trong ${path.relative(REPO, shots)}/\n`);
  return failed ? 1 : 0;
}

process.exitCode = main();
