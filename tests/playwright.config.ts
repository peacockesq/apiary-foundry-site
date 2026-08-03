import { defineConfig, devices } from '@playwright/test';

import { localBaseURL, localPort } from './runtime-ports';

export default defineConfig({
  testDir: '.',
  testMatch: process.env.PLAYWRIGHT_SERVER_LIFECYCLE_PROBE === '1'
    ? 'server-lifecycle-probe.spec.ts'
    : 'e2e.spec.ts',
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
    command: `python3 serve-playwright.py --port ${localPort} --owner-pid ${process.pid} --directory ..`,
    url: localBaseURL,
    reuseExistingServer: false,
    timeout: 120000,
  },
});