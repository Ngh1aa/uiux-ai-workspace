import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const targetDir = path.resolve(process.env.QA_TARGET_DIR || '.');
const command = process.env.QA_SERVE_COMMAND || '';
const port = process.env.QA_PORT || '4173';

if (!fs.existsSync(targetDir) || !fs.statSync(targetDir).isDirectory()) {
  throw new Error(`QA_TARGET_DIR does not exist or is not a directory: ${targetDir}`);
}

const child = command
  ? spawn('sh', ['-lc', command], {
      cwd: targetDir,
      env: { ...process.env, PORT: port, QA_PORT: port },
      stdio: 'inherit',
    })
  : spawn('python3', ['-m', 'http.server', port, '--directory', targetDir], {
      cwd: targetDir,
      env: process.env,
      stdio: 'inherit',
    });

const shutdown = () => {
  if (!child.killed) child.kill('SIGTERM');
};
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

child.on('exit', (code, signal) => {
  if (signal) process.exit(1);
  process.exit(code ?? 1);
});

console.log(`[QA] Serving target project ${targetDir} on port ${port}`);
if (command) console.log(`[QA] Command: ${command}`);
