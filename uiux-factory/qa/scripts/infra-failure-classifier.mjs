import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const INFRA_FAILURE_CLASSES = [
  'PASS',
  'PRODUCT_QA_FAILED',
  'PROVIDER_RATE_LIMITED',
  'AUTH_BLOCKED',
  'BUILD_FAILED',
  'DEPLOY_FAILED',
  'READY_BUT_NOT_DEPLOYED',
  'DEPLOYED_VERIFIED',
  'INFRA_UNAVAILABLE',
  'UNKNOWN_FAILURE'
];

function normalized(value) {
  return String(value || '').toLowerCase();
}

export function classifyInfraFailure({ source = 'generic', status = '', text = '' } = {}) {
  const haystack = `${source}\n${status}\n${text}`.toLowerCase();
  const statusNorm = normalized(status).replace(/[\s-]+/g, '_');
  const matched = [];
  const has = (...patterns) => patterns.some(pattern => {
    const ok = pattern instanceof RegExp ? pattern.test(haystack) : haystack.includes(pattern);
    if (ok) matched.push(String(pattern));
    return ok;
  });

  let classification = 'UNKNOWN_FAILURE';
  let retryable = false;
  let productQualityBlocking = false;
  let operatorAction = 'Inspect the originating provider or workflow logs before retrying.';

  if (statusNorm === 'pass' || statusNorm === 'success' || statusNorm === 'ok') {
    classification = 'PASS';
    operatorAction = 'No failure action required.';
  } else if (statusNorm === 'deployed_verified' || has('deployed_verified', 'deployment verified', 'production verified')) {
    classification = 'DEPLOYED_VERIFIED';
    operatorAction = 'Release evidence is complete for the declared verification scope.';
  } else if (statusNorm === 'ready_but_not_deployed' || has('ready_but_not_deployed', 'ready but not deployed')) {
    classification = 'READY_BUT_NOT_DEPLOYED';
    retryable = true;
    operatorAction = 'Keep product QA evidence distinct from release status and retry deployment when infrastructure is available.';
  } else if (has('uiux_state_coverage_failed', 'product_qa_failed', 'semantic_passed\": false', 'state coverage failed')) {
    classification = 'PRODUCT_QA_FAILED';
    productQualityBlocking = true;
    operatorAction = 'Repair the product/state implementation or its semantic contract, then rerun rendered QA. Do not classify this as infrastructure noise.';
  } else if (has('build-rate-limit', 'upgradetopro', 'rate limit', 'too many requests', /\b429\b/)) {
    classification = 'PROVIDER_RATE_LIMITED';
    retryable = true;
    operatorAction = 'Do not rewrite product code solely to clear this status. Retry after quota/reset or change provider capacity.';
  } else if (has('unauthorized', 'forbidden', 'authentication failed', 'permission denied', 'access denied', /\b401\b/, /\b403\b/)) {
    classification = 'AUTH_BLOCKED';
    operatorAction = 'Repair credentials, token scope, repository access, or deployment protection before retrying.';
  } else if (has('could not resolve host', 'name or service not known', 'dns', 'network is unreachable', 'connection timed out', 'econnrefused')) {
    classification = 'INFRA_UNAVAILABLE';
    retryable = true;
    operatorAction = 'Preserve the last verified product evidence and retry when the network/runtime dependency is available.';
  } else if (has('build failed', 'failed to compile', 'compilation failed', 'npm err!', 'command failed with exit code', 'typecheck failed')) {
    classification = 'BUILD_FAILED';
    productQualityBlocking = true;
    operatorAction = 'Repair the build-owning source/configuration and rerun build plus downstream rendered QA.';
  } else if (has('deployment failed', 'deploy failed', 'failed deployment', 'deployment_error', 'release failed')) {
    classification = 'DEPLOY_FAILED';
    retryable = true;
    operatorAction = 'Inspect deployment logs. If product/build evidence is green, treat deployment repair separately from product QA.';
  }

  return {
    schema_version: '1.0', source, status, classification, retryable,
    product_quality_blocking: productQualityBlocking,
    operator_action: operatorAction,
    matched_signals: [...new Set(matched)]
  };
}

function arg(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : '';
}

function main() {
  const source = arg('--source') || process.env.INFRA_SOURCE || 'generic';
  const status = arg('--status') || process.env.INFRA_STATUS || '';
  const input = arg('--input') || process.env.INFRA_INPUT || '';
  const output = arg('--output') || process.env.INFRA_OUTPUT || '';
  let text = arg('--text') || process.env.INFRA_TEXT || '';
  if (input) text += `\n${fs.readFileSync(path.resolve(input), 'utf8')}`;
  const result = classifyInfraFailure({ source, status, text });
  const payload = `${JSON.stringify(result, null, 2)}\n`;
  if (output) {
    const target = path.resolve(output);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, payload);
  }
  if (process.env.GITHUB_OUTPUT) {
    fs.appendFileSync(process.env.GITHUB_OUTPUT, `classification=${result.classification}\nretryable=${result.retryable}\nproduct_quality_blocking=${result.product_quality_blocking}\n`);
  }
  process.stdout.write(payload);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
