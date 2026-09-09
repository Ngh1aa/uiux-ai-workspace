import test from 'node:test';
import assert from 'node:assert/strict';
import { Context } from '@deepseek-ai/cordis';
import ToolRegistry from '@deepseek-ai/dsh-tools';
import SystemPrompt from '@deepseek-ai/dsh-system-prompt';
import * as plugin from './index.mjs';

test('native Harness registry: start, status, invalid args and cancellation', async () => {
  const ctx = new Context();
  const fibers = [ctx.plugin(SystemPrompt), ctx.plugin(ToolRegistry), ctx.plugin(plugin)];
  for (const fiber of fibers) await fiber.await();
  const originalFetch = globalThis.fetch;
  const requests = [];
  globalThis.fetch = async (url, options) => {
    options.signal.throwIfAborted();
    requests.push({url, options});
    return Response.json({id:'abcdef123456',status:options.method === 'POST' ? 'queued' : 'completed',project_slug:'test-draft'});
  };
  const execute = (name, args, signal = new AbortController().signal) => ctx.tools.execute({
    callId: `fixture-${name}`, name, arguments: args, signal,
  });
  try {
    const start = await execute('uiux_design_start', {prompt:'Studio landing page',engine:'ai'});
    assert.ok(!start.isError, JSON.stringify(start));
    const status = await execute('uiux_design_status', {job_id:'abcdef123456'});
    assert.ok(!status.isError, JSON.stringify(status));
    assert.equal(requests.length, 2);
    assert.equal(requests[0].url, 'http://127.0.0.1:8788/run');
    assert.equal(JSON.parse(requests[0].options.body).engine, 'ai');
    const invalid = await execute('uiux_design_status', {job_id:'../../secret'});
    assert.equal(invalid.isError, true);
    const cancelled = await execute('uiux_design_start', {prompt:'Studio',engine:'ai'}, AbortSignal.abort());
    assert.equal(cancelled.isError, true);
    assert.equal(requests.length, 2);
  } finally {
    globalThis.fetch = originalFetch;
    for (const fiber of fibers.reverse()) await fiber.dispose();
  }
});
