import test from 'node:test';
import assert from 'node:assert/strict';
import { classifyInfraFailure } from '../scripts/infra-failure-classifier.mjs';

test('classifies Vercel build rate limits as provider infrastructure', () => {
  const result = classifyInfraFailure({ source: 'vercel', status: 'failure', text: 'build-rate-limit / upgradeToPro' });
  assert.equal(result.classification, 'PROVIDER_RATE_LIMITED');
  assert.equal(result.retryable, true);
  assert.equal(result.product_quality_blocking, false);
});

test('does not hide semantic state failures as infra noise', () => {
  const result = classifyInfraFailure({ source: 'github-actions', status: 'failure', text: 'UIUX_STATE_COVERAGE_FAILED semantic_passed\": false' });
  assert.equal(result.classification, 'PRODUCT_QA_FAILED');
  assert.equal(result.product_quality_blocking, true);
});

test('classifies authentication blockers separately', () => {
  const result = classifyInfraFailure({ source: 'deployment', status: 'failure', text: '403 Forbidden: permission denied' });
  assert.equal(result.classification, 'AUTH_BLOCKED');
});
