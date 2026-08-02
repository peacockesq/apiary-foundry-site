import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process';
import { once } from 'node:events';
import { createServer } from 'node:net';

import { test, expect } from '@playwright/test';

import { withTcpLock } from './capture-lock';

async function getUnusedPort(): Promise<number> {
  const server = createServer();
  await new Promise<void>((resolve, reject) => {
    server.once('error', reject);
    server.listen({ host: '127.0.0.1', port: 0, exclusive: true }, resolve);
  });
  const address = server.address();
  if (!address || typeof address === 'string') throw new Error('Unable to reserve a TCP test port');
  await new Promise<void>((resolve, reject) => {
    server.close((error) => error ? reject(error) : resolve());
  });
  return address.port;
}

async function startAbruptOwner(port: number): Promise<ChildProcessWithoutNullStreams> {
  const owner = spawn(process.execPath, ['-e', [
    "const { createServer } = require('node:net');",
    'const server = createServer();',
    "server.listen({ host: '127.0.0.1', port: Number(process.env.LOCK_PORT), exclusive: true }, () => process.stdout.write('READY\\n'));",
  ].join('')], {
    env: { ...process.env, LOCK_PORT: String(port) },
    stdio: 'pipe',
  });

  await new Promise<void>((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Abrupt lock owner did not become ready')), 5_000);
    owner.once('error', (error) => {
      clearTimeout(timeout);
      reject(error);
    });
    owner.once('exit', (code) => {
      clearTimeout(timeout);
      reject(new Error(`Abrupt lock owner exited before ready (${code})`));
    });
    owner.stdout.setEncoding('utf8');
    owner.stdout.on('data', (chunk: string) => {
      if (!chunk.includes('READY')) return;
      clearTimeout(timeout);
      resolve();
    });
  });

  return owner;
}

test.describe('full-page capture mutex', () => {
  test('serializes contenders and recovers after abrupt owner exit', async () => {
    const port = await getUnusedPort();
    let active = 0;
    let maximumActive = 0;

    await Promise.all([0, 1, 2].map(() => withTcpLock(port, async () => {
      active += 1;
      maximumActive = Math.max(maximumActive, active);
      await new Promise((resolve) => setTimeout(resolve, 40));
      active -= 1;
    }, 2_000)));
    expect(maximumActive).toBe(1);

    await expect(withTcpLock(port, async () => {
      throw new Error('expected capture failure');
    }, 2_000)).rejects.toThrow('expected capture failure');
    await expect(withTcpLock(port, async () => 'released', 2_000)).resolves.toBe('released');

    const owner = await startAbruptOwner(port);
    const exited = once(owner, 'exit');
    owner.kill('SIGKILL');
    await exited;

    await expect(withTcpLock(port, async () => 'recovered', 2_000)).resolves.toBe('recovered');
  });
});
