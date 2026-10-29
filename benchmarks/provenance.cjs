'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const hash = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
function git(repo, ...args) {
  const result = spawnSync('git', ['-C', repo, ...args], {encoding:'utf8', maxBuffer:64*1024*1024});
  if (result.status !== 0) throw new Error(result.stderr || 'Git provenance failed');
  return result.stdout;
}
function snapshot(repo, runDir, checkerPaths) {
  const out = path.join(runDir, 'provenance');
  fs.mkdirSync(out, {recursive:true});
  // Exclude generated evaluations to avoid self-referential hashes. Every toolkit
  // source and each evaluated sample is hashed separately, including untracked files.
  const names = git(repo, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split('\0').filter(Boolean);
  const files = {};
  for (const name of [...new Set(names)].sort()) {
    if (name.startsWith('benchmarks/runs/') || name === 'benchmarks/REPORT.md') continue;
    const full = path.join(repo, name);
    files[name] = fs.existsSync(full) && fs.statSync(full).isFile() ? hash(fs.readFileSync(full)) : null;
  }
  const patch = git(repo, 'diff', '--binary', 'HEAD', '--', '.', ':!benchmarks/runs', ':!benchmarks/REPORT.md');
  fs.writeFileSync(path.join(out, 'local.patch'), patch);
  const manifest = {version:1, baseline_commit:git(repo,'rev-parse','HEAD').trim(),
    note:'baseline_commit identifies HEAD only; local evaluated code is identified by files and local.patch hashes. Untracked toolkit files are covered by the manifest.',
    status:git(repo,'status','--porcelain=v1').trim().split('\n').filter(Boolean),
    excluded:['benchmarks/runs/** (samples hashed separately)', 'benchmarks/REPORT.md (generated)'],
    patch_sha256:hash(Buffer.from(patch)), files};
  const content = JSON.stringify(manifest,null,2)+'\n';
  fs.writeFileSync(path.join(out,'manifest.json'),content);
  return {repo_commit:manifest.baseline_commit, dirty:manifest.status.length>0,
    checker_sha256:hash(fs.readFileSync(checkerPaths.render)),
    checkers:Object.fromEntries(Object.entries(checkerPaths).map(([name,file])=>[name,hash(fs.readFileSync(file))])),
    patch:{path:'provenance/local.patch',sha256:manifest.patch_sha256},
    manifest:{path:'provenance/manifest.json',sha256:hash(Buffer.from(content))}};
}
module.exports={hash,git,snapshot};
