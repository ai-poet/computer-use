import { spawn, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.resolve(__dirname, '..');
const backendScript = path.resolve(webRoot, '../backend/start_server.py');

const candidates = [
  process.env.PYTHON_BIN,
  '/opt/anaconda3/bin/python3',
  '/opt/homebrew/bin/python3',
  'python3',
  'python'
].filter(Boolean);

function canRunBackend(command) {
  if (command.includes('/') && !existsSync(command)) return false;
  const probe = spawnSync(command, ['-c', 'import fastapi, uvicorn'], {
    stdio: 'ignore'
  });
  return probe.status === 0;
}

const python = candidates.find(canRunBackend);

if (!python) {
  console.error('Could not find a Python interpreter with fastapi and uvicorn installed.');
  console.error('Install requirements or run with PYTHON_BIN=/path/to/python npm run dev:all.');
  process.exit(1);
}

const child = spawn(python, [backendScript, ...process.argv.slice(2)], {
  cwd: webRoot,
  stdio: 'inherit'
});

function forward(signal) {
  if (!child.killed) child.kill(signal);
}

process.on('SIGINT', () => forward('SIGTERM'));
process.on('SIGTERM', () => forward('SIGTERM'));

child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code ?? 0);
});
