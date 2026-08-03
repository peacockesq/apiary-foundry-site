import { spawn, execFileSync, type ChildProcessWithoutNullStreams } from 'node:child_process';
import { once } from 'node:events';
import { createServer as createHttpServer } from 'node:http';
import { createServer, connect, type Server } from 'node:net';
import { resolve } from 'node:path';

import { test, expect } from '@playwright/test';

async function getUnusedPort(): Promise<number> {
  const server = createServer();
  await new Promise<void>((resolveListen, reject) => {
    server.once('error', reject);
    server.listen({ host: '127.0.0.1', port: 0, exclusive: true }, resolveListen);
  });
  const address = server.address();
  if (!address || typeof address === 'string') throw new Error('Unable to reserve a TCP test port');
  await closeServer(server);
  return address.port;
}

async function closeServer(server: Server): Promise<void> {
  await new Promise<void>((resolveClose, reject) => {
    server.close((error) => error ? reject(error) : resolveClose());
  });
}

async function isPortOpen(port: number): Promise<boolean> {
  return new Promise((resolveOpen) => {
    const socket = connect({ host: '127.0.0.1', port });
    const finish = (open: boolean) => {
      socket.destroy();
      resolveOpen(open);
    };
    socket.setTimeout(250, () => finish(false));
    socket.once('connect', () => finish(true));
    socket.once('error', () => finish(false));
  });
}

async function waitForPortState(port: number, expectedOpen: boolean, timeoutMs: number): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await isPortOpen(port) === expectedOpen) return true;
    await new Promise((resolveWait) => setTimeout(resolveWait, 50));
  }
  return await isPortOpen(port) === expectedOpen;
}

function killServerProcessesForPort(port: number): void {
  if (process.platform === 'win32') return;
  const processRows = execFileSync('ps', ['-eo', 'pid=,args='], { encoding: 'utf8' });
  for (const row of processRows.split('\n')) {
    if (!row.includes(String(port)) || !/(http\.server|serve-playwright)/.test(row)) continue;
    const pid = Number(row.trim().split(/\s+/, 1)[0]);
    if (!Number.isInteger(pid) || pid === process.pid) continue;
    try {
      process.kill(pid, 'SIGKILL');
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ESRCH') throw error;
    }
  }
}

function killRunnerGroup(runner: ChildProcessWithoutNullStreams): void {
  if (!runner.pid) return;
  try {
    process.kill(process.platform === 'win32' ? runner.pid : -runner.pid, 'SIGKILL');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'ESRCH') throw error;
  }
}

function runnerExit(runner: ChildProcessWithoutNullStreams): Promise<unknown> {
  return runner.exitCode !== null || runner.signalCode !== null
    ? Promise.resolve()
    : once(runner, 'exit');
}

function startRunner(port: number): { runner: ChildProcessWithoutNullStreams; output: string[] } {
  const cliPath = resolve('node_modules/@playwright/test/cli.js');
  const runner = spawn(process.execPath, [cliPath, 'test', '--config=playwright.config.ts'], {
    cwd: process.cwd(),
    detached: true,
    env: {
      ...process.env,
      PLAYWRIGHT_PORT: String(port),
      PLAYWRIGHT_SERVER_LIFECYCLE_PROBE: '1',
    },
    stdio: 'pipe',
  });
  const output: string[] = [];
  runner.stdout.setEncoding('utf8');
  runner.stderr.setEncoding('utf8');
  runner.stdout.on('data', (chunk: string) => output.push(chunk));
  runner.stderr.on('data', (chunk: string) => output.push(chunk));
  runner.once('error', (error) => output.push(`Runner spawn error: ${error.message}`));
  return { runner, output };
}

test.describe('Playwright web server lifecycle', () => {
  test.skip(process.platform === 'win32', 'The CI lifecycle contract uses POSIX process-group termination');

  test('releases the workspace HTTP port after the actual runner is killed', async () => {
    const port = await getUnusedPort();
    const { runner, output } = startRunner(port);

    try {
      const opened = await waitForPortState(port, true, 15_000);
      expect(opened, `Runner exited before its web server opened:\n${output.join('')}`).toBe(true);

      const exited = runnerExit(runner);
      killRunnerGroup(runner);
      await exited;

      const closed = await waitForPortState(port, false, 5_000);
      expect(closed, `Web server still owns 127.0.0.1:${port} after runner SIGKILL`).toBe(true);
    } finally {
      killRunnerGroup(runner);
      killServerProcessesForPort(port);
    }
  });

  test('fails instead of borrowing an occupied workspace port', async () => {
    const port = await getUnusedPort();
    const foreignServer = createHttpServer((_request, response) => {
      response.writeHead(200, { 'Content-Length': '0' });
      response.end();
    });
    await new Promise<void>((resolveListen, reject) => {
      foreignServer.once('error', reject);
      foreignServer.listen({ host: '127.0.0.1', port, exclusive: true }, resolveListen);
    });
    const { runner, output } = startRunner(port);

    try {
      await runnerExit(runner);
      expect(runner.exitCode, output.join('')).not.toBe(0);
      expect(output.join('')).toContain('is already used');
      expect(await isPortOpen(port)).toBe(true);
    } finally {
      killRunnerGroup(runner);
      await closeServer(foreignServer);
    }
  });
});
