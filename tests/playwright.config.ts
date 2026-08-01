import { defineConfig, devices } from '@playwright/test';

// Keep concurrent workspaces from borrowing and later losing each other's test server.
const configuredPort = Number(process.env.PLAYWRIGHT_PORT);
const workspaceHash = [...process.cwd()].reduce(
  (hash, character) => ((hash * 31) + character.charCodeAt(0)) >>> 0,
  0,
);
const workspacePort = 10000 + (workspaceHash % 50000);
const localPort = Number.isInteger(configuredPort) && configuredPort > 0 && configuredPort <= 65535
  ? configuredPort
  : workspacePort;
const localBaseURL = `http://127.0.0.1:${localPort}`;

export default defineConfig({
  testDir: '.',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    process.env.CI ? ['github'] : ['list'],
  ],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || localBaseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'chromium-mobile',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'chromium-mobile-landscape',
      use: { ...devices['Pixel 7 landscape'] },
    },
    {
      name: 'webkit-mobile',
      use: { ...devices['iPhone 14'] },
    },
  ],
  webServer: {
    command: `cd .. && python3 -m http.server ${localPort} --bind 127.0.0.1`,
    url: localBaseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});