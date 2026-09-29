import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { classifyInfraFailure } from './infra-failure-classifier.mjs';

function normalizeStatus(value) {
  return String(value || '').trim().toLowerCase().replace(/[\s-]+/g, '_');
}

function isReadyStatus(value) {
  return ['ready', 'success', 'succeeded', 'deployed', 'production', 'active'].includes(normalizeStatus(value));
}

function normalizeSha(value) {
  return String(value || '').trim().toLowerCase();
}

function shaMatches(expected, actual) {
  const a = normalizeSha(expected);
  const b = normalizeSha(actual);
  if (!a || !b) return false;
  return a === b || (a.length >= 7 && b.startsWith(a)) || (b.length >= 7 && a.startsWith(b));
}

function statusIs2xx(status) {
  const number = Number(status);
  return Number.isInteger(number) && number >= 200 && number < 300;
}

export function verifyDeploymentTruth(input = {}) {
  const expectedSha = normalizeSha(input.expected_sha);
  const deploymentSha = normalizeSha(input.deployment_sha);
  const deploymentStatus = String(input.deployment_status || '');
  const productionUrl = String(input.production_url || '').trim();
  const provider = String(input.provider || 'generic').trim() || 'generic';
  const providerText = String(input.provider_text || '');
  const probeStatus = input.probe_status === undefined || input.probe_status === null || input.probe_status === ''
    ? null
    : Number(input.probe_status);
  const productQaPassed = input.product_qa_passed !== false;
  const deploymentFound = Boolean(deploymentSha || deploymentStatus || productionUrl);

  const result = {
    schema_version: '1.0',
    expected_sha: expectedSha,
    deployment_sha: deploymentSha,
    deployment_status: deploymentStatus,
    production_url: productionUrl,
    provider,
    probe_status: probeStatus,
    product_qa_passed: productQaPassed,
    checks: {
      expected_sha_present: Boolean(expectedSha),
      deployment_found: deploymentFound,
      deployment_sha_present: Boolean(deploymentSha),
      deployment_sha_matches: false,
      deployment_ready: false,
      production_url_present: Boolean(productionUrl),
      production_route_2xx: false,
    },
    classification: 'UNKNOWN_FAILURE',
    verified: false,
    product_quality_blocking: false,
    retryable: false,
    reasons: [],
  };

  if (!productQaPassed) {
    result.classification = 'PRODUCT_QA_FAILED';
    result.product_quality_blocking = true;
    result.reasons.push('Product QA is not green; deployment truth cannot promote the release.');
    return result;
  }

  const providerClassification = classifyInfraFailure({
    source: provider,
    status: deploymentStatus,
    text: providerText,
  });
  if (['PROVIDER_RATE_LIMITED', 'AUTH_BLOCKED', 'BUILD_FAILED', 'DEPLOY_FAILED', 'INFRA_UNAVAILABLE'].includes(providerClassification.classification)) {
    result.classification = providerClassification.classification;
    result.retryable = providerClassification.retryable;
    result.product_quality_blocking = providerClassification.product_quality_blocking;
    result.reasons.push(providerClassification.operator_action);
    return result;
  }

  if (!expectedSha) {
    result.reasons.push('Expected release SHA is required.');
    return result;
  }

  if (!deploymentFound || !deploymentSha) {
    result.classification = 'READY_BUT_NOT_DEPLOYED';
    result.retryable = true;
    result.reasons.push('Product QA is green but no deployment tied to the expected SHA is available.');
    return result;
  }

  result.checks.deployment_sha_matches = shaMatches(expectedSha, deploymentSha);
  if (!result.checks.deployment_sha_matches) {
    result.classification = 'DEPLOY_FAILED';
    result.reasons.push(`Deployment SHA ${deploymentSha} does not match expected release SHA ${expectedSha}.`);
    return result;
  }

  result.checks.deployment_ready = isReadyStatus(deploymentStatus);
  if (!result.checks.deployment_ready) {
    result.classification = 'READY_BUT_NOT_DEPLOYED';
    result.retryable = true;
    result.reasons.push(`Deployment for the expected SHA is not ready (status: ${deploymentStatus || 'unknown'}).`);
    return result;
  }

  if (!productionUrl) {
    result.classification = 'READY_BUT_NOT_DEPLOYED';
    result.retryable = true;
    result.reasons.push('Deployment is ready but no production URL/alias was supplied for route verification.');
    return result;
  }

  if (probeStatus === null) {
    result.classification = 'READY_BUT_NOT_DEPLOYED';
    result.retryable = true;
    result.reasons.push('Deployment metadata is ready, but the production route has not been probed yet.');
    return result;
  }

  result.checks.production_route_2xx = statusIs2xx(probeStatus);
  if (!result.checks.production_route_2xx) {
    result.classification = 'DEPLOY_FAILED';
    result.retryable = true;
    result.reasons.push(`Production route probe returned HTTP ${probeStatus}.`);
    return result;
  }

  result.classification = 'DEPLOYED_VERIFIED';
  result.verified = true;
  result.reasons.push('Expected SHA, deployment SHA, ready status, production alias and 2xx route probe all agree.');
  return result;
}

async function probe(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(url, { redirect: 'follow', signal: controller.signal });
    return { status: response.status, final_url: response.url };
  } finally {
    clearTimeout(timeout);
  }
}

function arg(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : '';
}

async function main() {
  const inputPath = arg('--input') || process.env.DEPLOYMENT_TRUTH_INPUT || '';
  const outputPath = arg('--output') || process.env.DEPLOYMENT_TRUTH_OUTPUT || '';
  let input = {};
  if (inputPath) input = JSON.parse(fs.readFileSync(path.resolve(inputPath), 'utf8'));

  input.expected_sha = arg('--expected-sha') || process.env.EXPECTED_SHA || input.expected_sha || '';
  input.deployment_sha = arg('--deployment-sha') || process.env.DEPLOYMENT_SHA || input.deployment_sha || '';
  input.deployment_status = arg('--deployment-status') || process.env.DEPLOYMENT_STATUS || input.deployment_status || '';
  input.production_url = arg('--production-url') || process.env.PRODUCTION_URL || input.production_url || '';
  input.provider = arg('--provider') || process.env.DEPLOYMENT_PROVIDER || input.provider || 'generic';
  input.provider_text = arg('--provider-text') || process.env.DEPLOYMENT_PROVIDER_TEXT || input.provider_text || '';
  const productQaEnv = arg('--product-qa-passed') || process.env.PRODUCT_QA_PASSED || '';
  if (productQaEnv) input.product_qa_passed = !['0', 'false', 'no'].includes(productQaEnv.toLowerCase());

  const explicitProbe = arg('--probe-status') || process.env.PRODUCTION_PROBE_STATUS || '';
  if (explicitProbe) {
    input.probe_status = Number(explicitProbe);
  } else if (input.production_url) {
    try {
      const observed = await probe(input.production_url);
      input.probe_status = observed.status;
      input.final_url = observed.final_url;
    } catch (error) {
      const classified = classifyInfraFailure({ source: input.provider || 'generic', status: 'failure', text: String(error) });
      const result = verifyDeploymentTruth(input);
      result.classification = classified.classification === 'UNKNOWN_FAILURE' ? 'INFRA_UNAVAILABLE' : classified.classification;
      result.retryable = true;
      result.verified = false;
      result.reasons.push(`Production probe failed: ${String(error)}`);
      const payload = `${JSON.stringify(result, null, 2)}\n`;
      if (outputPath) {
        const target = path.resolve(outputPath);
        fs.mkdirSync(path.dirname(target), { recursive: true });
        fs.writeFileSync(target, payload);
      }
      process.stdout.write(payload);
      process.exitCode = 2;
      return;
    }
  }

  const result = verifyDeploymentTruth(input);
  if (input.final_url) result.final_url = input.final_url;
  const payload = `${JSON.stringify(result, null, 2)}\n`;
  if (outputPath) {
    const target = path.resolve(outputPath);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, payload);
  }
  if (process.env.GITHUB_OUTPUT) {
    fs.appendFileSync(process.env.GITHUB_OUTPUT, `classification=${result.classification}\nverified=${result.verified}\n`);
  }
  process.stdout.write(payload);
  if (!result.verified) process.exitCode = 2;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
