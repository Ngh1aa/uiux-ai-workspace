import test from 'node:test';
import assert from 'node:assert/strict';
import { verifyDeploymentTruth } from '../scripts/deployment-truth.mjs';

const sha = '6941b80e458282fbf648e24aef5c6e22019ba928';

test('verifies only when release SHA, ready deployment and production probe agree', () => {
  const result = verifyDeploymentTruth({
    expected_sha: sha,
    deployment_sha: sha,
    deployment_status: 'READY',
    production_url: 'https://example.com',
    probe_status: 200,
  });
  assert.equal(result.classification, 'DEPLOYED_VERIFIED');
  assert.equal(result.verified, true);
  assert.equal(result.checks.deployment_sha_matches, true);
});

test('does not mistake provider rate limiting for a product failure', () => {
  const result = verifyDeploymentTruth({
    expected_sha: sha,
    deployment_status: 'failure',
    provider: 'vercel',
    provider_text: 'build-rate-limit / upgradeToPro',
  });
  assert.equal(result.classification, 'PROVIDER_RATE_LIMITED');
  assert.equal(result.product_quality_blocking, false);
  assert.equal(result.retryable, true);
});

test('reports ready product with no deployment separately', () => {
  const result = verifyDeploymentTruth({ expected_sha: sha, product_qa_passed: true });
  assert.equal(result.classification, 'READY_BUT_NOT_DEPLOYED');
  assert.equal(result.verified, false);
});

test('rejects a deployment from the wrong commit', () => {
  const result = verifyDeploymentTruth({
    expected_sha: sha,
    deployment_sha: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    deployment_status: 'READY',
    production_url: 'https://example.com',
    probe_status: 200,
  });
  assert.equal(result.classification, 'DEPLOY_FAILED');
  assert.match(result.reasons.join(' '), /does not match expected release SHA/);
});

test('rejects a non-2xx production route', () => {
  const result = verifyDeploymentTruth({
    expected_sha: sha,
    deployment_sha: sha,
    deployment_status: 'READY',
    production_url: 'https://example.com',
    probe_status: 503,
  });
  assert.equal(result.classification, 'DEPLOY_FAILED');
  assert.equal(result.checks.production_route_2xx, false);
});

test('product QA failure blocks deployment promotion before infra status', () => {
  const result = verifyDeploymentTruth({
    expected_sha: sha,
    product_qa_passed: false,
    provider_text: 'build-rate-limit / upgradeToPro',
  });
  assert.equal(result.classification, 'PRODUCT_QA_FAILED');
  assert.equal(result.product_quality_blocking, true);
});
