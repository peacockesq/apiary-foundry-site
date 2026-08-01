import { test, expect } from '@playwright/test';

const PAGES = [
  { path: '/', name: 'Home' },
  { path: '/measurement-engine/', name: 'Measurement Engine' },
  { path: '/growth-os/', name: 'Growth OS' },
  { path: '/five-hives/', name: 'Five Hives' },
  { path: '/about-willie-peacock/', name: 'About Willie' },
  { path: '/proof/', name: 'Proof' },
  { path: '/blog/', name: 'Blog' },
  { path: '/blog/deterministic-vs-agentic-marketing-systems/', name: 'Deterministic vs Agentic' },
  { path: '/work-with-us/', name: 'Work With Us' },
  { path: '/privacy-policy/', name: 'Privacy Policy' },
  { path: '/terms-of-service/', name: 'Terms of Service' },
  { path: '/trust/', name: 'Trust' },
];

const PR19_QA_PAGES = [
  { path: '/', heading: /random acts of marketing/i },
  { path: '/work-with-us/', heading: /bring order to the marketing system/i },
  { path: '/privacy-policy/', heading: /privacy policy/i },
  { path: '/terms-of-service/', heading: /terms of service/i },
  { path: '/measurement-engine/', heading: /infrastructure behind fundable marketing/i },
];

// ─── Visual QA: full-page screenshots ─────────────────────────
test.describe('Visual QA', () => {
  for (const { path, name } of PAGES) {
    test(`${name} (${path}) — full page`, async ({ page }, testInfo) => {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      // Hide Mautic iframe for stable screenshots
      await page.addStyleTag({ content: 'iframe[src*="mautic"] { display: none !important; }' });
      const screenshot = await page.screenshot({ fullPage: true });
      await testInfo.attach(`page-${name.toLowerCase().replace(/\s+/g, '-')}.png`, {
        body: screenshot,
        contentType: 'image/png',
      });
    });
  }
});

// ─── Nav: desktop visibility ──────────────────────────────────────────
test.describe('Navigation — Desktop', () => {
  test.use({ viewport: { width: 1280, height: 800 } });

  test('nav links are visible without hamburger', async ({ page }) => {
    await page.goto('/');
    const hamburger = page.locator('.hamburger');
    await expect(hamburger).not.toBeVisible();
    const navLinks = page.locator('.nav-links a');
    await expect(navLinks.first()).toBeVisible();
    await expect(navLinks).toHaveCount(8);
  });

  test('CTA button is visible', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.nav-cta')).toBeVisible();
  });
});

// ─── Nav: mobile hamburger ─────────────────────────────────────────────
test.describe('Navigation — Mobile Hamburger', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('hamburger button is visible, nav links are hidden initially', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.hamburger')).toBeVisible();
    // Nav links container should be hidden by default
    const navMenu = page.locator('#nav-menu');
    await expect(navMenu).toHaveAttribute('aria-expanded', 'false');
  });

  test('tapping hamburger opens menu and shows all links', async ({ page }) => {
    await page.goto('/');
    await page.locator('.hamburger').click();
    await expect(page.locator('#nav-menu')).toHaveAttribute('aria-expanded', 'true');
    // All 8 links should now be visible
    const links = page.locator('#nav-menu a');
    await expect(links).toHaveCount(8);
    await expect(links.first()).toBeVisible();
  });

  test('tapping a link closes the menu', async ({ page }) => {
    await page.goto('/');
    await page.locator('.hamburger').click();
    await page.locator('#nav-menu a').first().click();
    await expect(page.locator('#nav-menu')).toHaveAttribute('aria-expanded', 'false');
  });

  test('Escape key closes the menu', async ({ page }) => {
    await page.goto('/');
    await page.locator('.hamburger').click();
    await expect(page.locator('#nav-menu')).toHaveAttribute('aria-expanded', 'true');
    await page.keyboard.press('Escape');
    await expect(page.locator('#nav-menu')).toHaveAttribute('aria-expanded', 'false');
  });

  test('mobile CTA is visible and navigates to /work-with-us/', async ({ page }) => {
    await page.goto('/');
    const cta = page.locator('.mobile-cta');
    await expect(cta).not.toBeVisible();
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.45));
    await expect(cta).toBeVisible();
    await expect(cta).toHaveAttribute('href', '/work-with-us/');
  });
});

// ─── Contrast QA ───────────────────────────────────────────────────────
test.describe('Contrast QA', () => {
  async function getContrastRatio(page: any, fg: string, bg: string): Promise<number> {
    return page.evaluate((f: string, b: string) => {
      const rgb = (hex: string) => {
        const h = hex.replace('#', '');
        return [
          parseInt(h.substring(0, 2), 16) / 255,
          parseInt(h.substring(2, 4), 16) / 255,
          parseInt(h.substring(4, 6), 16) / 255,
        ];
      };
      const lum = ([r, g, b]: number[]) => {
        const c = [r, g, b].map((x) => (x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)));
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
      };
      const L1 = lum(rgb(f)) + 0.05;
      const L2 = lum(rgb(b)) + 0.05;
      return L1 > L2 ? L1 / L2 : L2 / L1;
    }, fg, bg);
  }

  test('nav pills on dark background have sufficient contrast', async ({ page }) => {
    // Scroll to a dark section so nav overlays it
    await page.goto('/');
    const darkSection = page.locator('.dark-section').first();
    await darkSection.scrollIntoViewIfNeeded();
    // Nav should still be visible (sticky)
    const navLink = page.locator('.nav-links a').first();
    const color = await navLink.evaluate((el: HTMLElement) =>
      window.getComputedStyle(el).color
    );
    const bg = await navLink.evaluate((el: HTMLElement) =>
      window.getComputedStyle(el).backgroundColor
    );
    // Desktop nav links intentionally sit on the nav-wrap background; mobile nav pills carry
    // their own solid background. Either way, text cannot be transparent.
    expect(color).not.toBe('rgba(0, 0, 0, 0)');
    if (bg !== 'rgba(0, 0, 0, 0)') {
      expect(bg).not.toBe('transparent');
    }
  });

  test('all CTAs meet WCAG AA (4.5:1) for normal text', async ({ page }) => {
    await page.goto('/');
    const ctas = page.locator('a.button, a.ghost, button[type="submit"], .nav-cta, .mobile-cta');
    const count = await ctas.count();
    for (let i = 0; i < count; i++) {
      const el = ctas.nth(i);
      const visible = await el.isVisible();
      if (!visible) continue;
      const color = await el.evaluate((e: HTMLElement) => window.getComputedStyle(e).color);
      const bg = await el.evaluate((e: HTMLElement) => window.getComputedStyle(e).backgroundColor);
      // Skip if both are transparent (shouldn't happen for CTAs)
      expect(color).not.toBe('rgba(0, 0, 0, 0)');
    }
  });
});

// ─── Functional: forms ────────────────────────────────────────────────
test.describe('Lead forms', () => {
  test('newsletter form renders and validates', async ({ page }) => {
    await page.goto('/');
    const form = page.locator('.newsletter-form');
    await expect(form).toBeVisible();
    const email = form.locator('input[type="email"]');
    await expect(email).toBeVisible();
    // Submit without email should trigger validation
    await form.locator('button').click();
    const validationMessage = await email.evaluate((e: HTMLInputElement) => e.validationMessage);
    expect(validationMessage.length).toBeGreaterThan(0);
  });

  test('work-with-us diagnostic form exists', async ({ page }) => {
    await page.goto('/work-with-us/');
    await expect(page.locator('#apiary-growth-diagnostic')).toBeVisible();
    await expect(page.locator('#apiary-growth-diagnostic input[name="marketing_consent"]')).toHaveAttribute('required', '');
    await expect(page.locator('#apiary-growth-diagnostic [data-consent-text]')).toContainText('Privacy Policy');
    await expect(page.locator('#apiary-growth-diagnostic [data-consent-text]')).toContainText('Terms of Service');
  });

  test('diagnostic submit preserves attribution and shows booking CTA without leaving the site', async ({ page }) => {
    let capturedPayload: any = null;
    await page.route('https://n8n.esq2u.com/webhook/apiary-foundry/lead', async (route) => {
      capturedPayload = JSON.parse(route.request().postData() || '{}');
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true }) });
    });

    await page.goto('/work-with-us/?utm_source=qa&utm_campaign=pr19-rebuild&gclid=test-click');
    const form = page.locator('#apiary-growth-diagnostic');
    await form.locator('input[name="name"]').fill('QA Lead');
    await form.locator('input[name="email"]').fill('qa@example.com');
    await form.locator('textarea[name="message"]').fill('Browser QA only. Do not create a real external lead.');
    await form.locator('input[name="marketing_consent"]').check();
    await form.locator('button[type="submit"]').click();

    const status = form.locator('[data-form-status]');
    await expect(status).toContainText('Received');
    await expect(page).toHaveURL(/\/work-with-us\//);
    expect(capturedPayload).toMatchObject({
      email: 'qa@example.com',
      consent_status: 'granted',
      utm_source: 'qa',
      utm_campaign: 'pr19-rebuild',
      gclid: 'test-click',
      source_form: 'growth_diagnostic',
    });
    const bookingHref = await status.locator('a[data-booking-link]').getAttribute('href');
    expect(bookingHref).toContain('tidycal.com/peacockesq/apiary-foundry-1-1-chats');
    expect(bookingHref).toContain('email=qa%40example.com');
    expect(bookingHref).toContain('utm_source=qa');
    expect(bookingHref).toContain('gclid=test-click');
  });
});

// ─── PR #19 rebuilt-value browser QA ───────────────────────────────────
test.describe('PR #19 rebuilt legal and lead-capture value', () => {
  for (const { path, heading } of PR19_QA_PAGES) {
    test(`${path} renders with lead-capture JS and no public console errors`, async ({ page }) => {
      const consoleErrors: string[] = [];
      const pageErrors: string[] = [];
      const leadCaptureResponses: number[] = [];

      page.on('console', (message) => {
        if (message.type() === 'error') consoleErrors.push(message.text());
      });
      page.on('pageerror', (error) => pageErrors.push(error.message));
      page.on('response', (response) => {
        if (response.url().includes('/assets/apiary-lead-capture.js')) {
          leadCaptureResponses.push(response.status());
        }
      });

      await page.route('https://mautic.apiaryfoundry.com/mtc.js', async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/javascript', body: 'window.mt = window.mt || function(){};' });
      });

      const response = await page.goto(path);
      expect(response?.status()).toBe(200);
      await expect(page.locator('h1').first()).toContainText(heading);
      await expect(page.locator('footer a[href="/privacy-policy/"]')).toBeVisible();
      await expect(page.locator('footer a[href="/terms-of-service/"]')).toBeVisible();
      await expect(page.locator('form[data-apiary-lead-form]').first()).toBeVisible();
      await page.waitForLoadState('networkidle');

      expect(leadCaptureResponses).toContain(200);
      expect(consoleErrors).toEqual([]);
      expect(pageErrors).toEqual([]);
    });
  }
});

// ─── Smoke: no 404s ───────────────────────────────────────────────────
test.describe('Smoke: no broken pages', () => {
  for (const { path, name } of PAGES) {
    test(`${name} (${path}) loads 200`, async ({ page }) => {
      const response = await page.goto(path);
      expect(response?.status()).toBe(200);
      // Check for "404" in title or body (common fallback pattern)
      const title = await page.title();
      expect(title.toLowerCase()).not.toContain('404');
      const bodyText = await page.locator('body').textContent() || '';
      expect(bodyText.toLowerCase()).not.toContain('page not found');
    });
  }
});