import test from 'node:test';
import assert from 'node:assert/strict';
import { semanticTextIncludes, validateContract } from '../scripts/state-coverage.mjs';

const base = {
  schema_version: '1.0',
  name: 'Fixture product',
  entry_route: '/fixture/state-lab.html',
  frame_selector: '#fixtureFrame',
  states: [
    { id: 'normal', label: 'Normal', scope: 'iframe', query: { state: 'normal' }, assertions: [] },
    { id: 'empty', label: 'Empty', scope: 'iframe', query: { state: 'empty' }, assertions: [{ type: 'selector', selector: '[data-state-evidence="empty"]' }], focus: '[data-state-evidence="empty"]' },
    { id: 'loading', label: 'Loading', scope: 'iframe', query: { state: 'loading', pin: 1 }, assertions: [{ type: 'text', text: 'Loading evidence' }], focus: '[data-state-evidence="loading"]' },
    { id: 'error', label: 'Error', scope: 'iframe', query: { state: 'error' }, assertions: [{ type: 'attribute', selector: '[data-state-evidence="error"]', attribute: 'role', equals: 'alert' }], focus: '[data-state-evidence="error"]' },
    { id: 'edge', label: 'Edge', scope: 'iframe', query: { state: 'edge' }, assertions: [{ type: 'selector', selector: '[data-state-evidence="edge"]' }], focus: '[data-state-evidence="edge"]' }
  ],
  matrix: { states: ['empty', 'loading', 'error', 'edge'], columns: 2 }
};

test('normalizes a valid state coverage contract', () => {
  const contract = validateContract(base);
  assert.equal(contract.viewports.length, 3);
  assert.deepEqual(contract.matrix.states, ['empty', 'loading', 'error', 'edge']);
  assert.equal(contract.states.find(state => state.id === 'empty').scope, 'iframe');
});

test('requires semantic assertions for non-normal states', () => {
  const broken = structuredClone(base);
  broken.states.find(state => state.id === 'empty').assertions = [];
  assert.throws(() => validateContract(broken), /requires at least one semantic assertion/);
});

test('rejects a matrix that references unknown states', () => {
  const broken = structuredClone(base);
  broken.matrix.states.push('ghost');
  assert.throws(() => validateContract(broken), /unknown state/);
});

test('semantic text matching survives CSS text-transform casing and whitespace', () => {
  assert.equal(
    semanticTextIncludes('DEFAULT → HOVER\n→ PRESSED → DISABLED', 'Default → Hover → Pressed → Disabled'),
    true,
  );
  assert.equal(semanticTextIncludes('SAVED / SHORTLISTED', 'Saved / shortlisted'), true);
});

test('semantic text can opt into case-sensitive matching', () => {
  assert.equal(semanticTextIncludes('SAVED / SHORTLISTED', 'Saved / shortlisted', true), false);
  assert.equal(semanticTextIncludes('Saved / shortlisted', 'Saved / shortlisted', true), true);
});
