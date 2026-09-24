import { defineTool } from '@deepseek-ai/dsh-tools';

export const name = 'uiux-designer';
export const inject = ['tools'];
const bridge = 'http://127.0.0.1:8788';

async function request(path, signal, body) {
  const response = await fetch(bridge + path, {
    method: body ? 'POST' : 'GET',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.any([signal, AbortSignal.timeout(15000)]),
    redirect: 'error',
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Factory HTTP ${response.status}`);
  return data;
}

export function apply(ctx) {
  ctx.tools.register(defineTool({
    name: 'uiux_design_start',
    description: 'Start an asynchronous UIUX Factory design job after a user requests generation. AI cloud requires separately configured free-tier credentials. Returns a job ID; use uiux_design_status to poll. Does not install or use iPolloWork.',
    parameters: {
      prompt: { type: 'string', required: true, description: 'Business brief, desired pages and design constraints' },
      engine: { type: 'string', required: true, description: 'ai or template' },
    },
    output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] },
    async execute(args, exec) {
      if (!args.prompt.trim() || args.prompt.length > 20000) throw new Error('Brief must contain 1-20000 characters.');
      if (!['ai', 'template'].includes(args.engine)) throw new Error('Engine must be ai or template.');
      const job = await request('/run', exec.signal, { prompt: args.prompt, engine: args.engine });
      return JSON.stringify({ job_id: job.id, status: job.status, workbench: 'http://localhost:5173/uiux' });
    },
  }));
  ctx.tools.register(defineTool({
    name: 'uiux_design_status',
    description: 'Read the status and output links for a UIUX Factory job. A completed run still requires human visual review.',
    parameters: { job_id: { type: 'string', required: true, description: '12-character Factory job ID' } },
    output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] },
    async execute(args, exec) {
      if (!/^[a-f0-9]{12}$/.test(args.job_id)) throw new Error('Invalid Factory job ID.');
      const job = await request(`/jobs/${args.job_id}`, exec.signal);
      return JSON.stringify({ job_id: job.id, status: job.status, active_stage: job.active_stage,
        error: job.error, design_document: `${bridge}/jobs/${args.job_id}/artifacts/DESIGN.md`,
        preview: job.project_slug ? `${bridge}/preview/${job.project_slug}/` : null });
    },
  }));
}
