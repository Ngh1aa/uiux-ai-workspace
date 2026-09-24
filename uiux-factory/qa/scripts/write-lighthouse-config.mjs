import fs from 'node:fs';

const baseURL = process.env.QA_BASE_URL || 'http://127.0.0.1:4173';
const routes = (process.env.QA_ROUTES || '/')
  .split(',')
  .map(route => route.trim())
  .filter(Boolean);

if (!routes.length) {
  throw new Error('QA_ROUTES must contain at least one route.');
}

const source = JSON.parse(fs.readFileSync('lighthouserc.json', 'utf8'));
source.ci ??= {};
source.ci.collect ??= {};
source.ci.collect.url = routes.map(route => new URL(route, baseURL).toString());
source.ci.collect.numberOfRuns = Number(source.ci.collect.numberOfRuns || 1);
source.ci.upload ??= { target: 'filesystem', outputDir: './artifacts/lighthouse' };

fs.writeFileSync(
  'lighthouserc.runtime.json',
  `${JSON.stringify(source, null, 2)}\n`,
  'utf8'
);
console.log(`[QA] Lighthouse routes: ${source.ci.collect.url.join(', ')}`);
