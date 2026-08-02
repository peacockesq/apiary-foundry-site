const configuredPort = Number(process.env.PLAYWRIGHT_PORT);

export const workspaceHash = [...process.cwd()].reduce(
  (hash, character) => ((hash * 31) + character.charCodeAt(0)) >>> 0,
  0,
);

const workspacePort = 10000 + (workspaceHash % 50000);

export const localPort = Number.isInteger(configuredPort) && configuredPort > 0 && configuredPort <= 65535
  ? configuredPort
  : workspacePort;

export const localBaseURL = `http://127.0.0.1:${localPort}`;

// Keep the OS-backed capture mutex away from this workspace's HTTP server port.
export const captureLockPort = 10000 + ((((localPort - 10000) + 25000) % 50000) + 50000) % 50000;
