import { test } from '@playwright/test';

test('keeps the actual runner alive for forced-termination verification', async () => {
  test.setTimeout(120_000);
  await new Promise((resolve) => setTimeout(resolve, 120_000));
});
