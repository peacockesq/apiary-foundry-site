import { createServer, type Server } from 'node:net';

import { captureLockPort } from './runtime-ports';

const CAPTURE_LOCK_HOST = '127.0.0.1';
const CAPTURE_LOCK_TIMEOUT_MS = 120_000;
const CAPTURE_LOCK_RETRY_MS = 25;

const wait = (milliseconds: number) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function tryAcquireTcpLock(port: number): Promise<Server | null> {
  return new Promise((resolve, reject) => {
    const server = createServer((socket) => socket.destroy());

    const handleError = (error: NodeJS.ErrnoException) => {
      if (error.code === 'EADDRINUSE') {
        resolve(null);
        return;
      }
      reject(error);
    };

    server.once('error', handleError);
    server.listen({ host: CAPTURE_LOCK_HOST, port, exclusive: true }, () => {
      server.removeListener('error', handleError);
      server.unref();
      resolve(server);
    });
  });
}

async function releaseTcpLock(server: Server): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    server.close((error) => error ? reject(error) : resolve());
  });
}

export async function withTcpLock<T>(
  port: number,
  criticalSection: () => Promise<T>,
  timeoutMs = CAPTURE_LOCK_TIMEOUT_MS,
): Promise<T> {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() < deadline) {
    const server = await tryAcquireTcpLock(port);
    if (server) {
      try {
        return await criticalSection();
      } finally {
        await releaseTcpLock(server);
      }
    }
    await wait(CAPTURE_LOCK_RETRY_MS);
  }

  throw new Error(
    `Timed out waiting for full-page capture mutex at ${CAPTURE_LOCK_HOST}:${port}`,
  );
}

export function withFullPageCaptureLock<T>(capture: () => Promise<T>): Promise<T> {
  return withTcpLock(captureLockPort, capture);
}
