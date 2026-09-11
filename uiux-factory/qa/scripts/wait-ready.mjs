const baseURL = process.env.QA_BASE_URL || 'http://127.0.0.1:4173';
const firstRoute = (process.env.QA_ROUTES || '/').split(',')[0].trim() || '/';
const timeoutMs = Number(process.env.QA_READY_TIMEOUT_MS || 60_000);
const intervalMs = Number(process.env.QA_READY_INTERVAL_MS || 500);
const deadline = Date.now() + timeoutMs;
const url = new URL(firstRoute, baseURL).toString();

let lastError = '';
while (Date.now() < deadline) {
  try {
    const response = await fetch(url, { redirect: 'follow' });
    if (response.ok) {
      console.log(`[QA] Target ready: ${response.status} ${url}`);
      process.exit(0);
    }
    lastError = `HTTP ${response.status}`;
  } catch (error) {
    lastError = String(error);
  }
  await new Promise(resolve => setTimeout(resolve, intervalMs));
}

throw new Error(`Target server was not ready within ${timeoutMs}ms at ${url}. Last error: ${lastError}`);
