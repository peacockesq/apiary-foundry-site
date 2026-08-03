import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: 'capture-lock.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  workers: 4,
  reporter: process.env.CI ? 'github' : 'list',
});