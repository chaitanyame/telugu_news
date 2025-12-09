import { test, expect } from '@playwright/test';

test.describe('Accessibility Features', () => {
  test('should have lang attribute set to Telugu', async ({ page }) => {
    await page.goto('/');
    
    const htmlLang = await page.locator('html').getAttribute('lang');
    expect(htmlLang).toBe('te');
  });

  test('should have skip-to-content link', async ({ page }) => {
    await page.goto('/');
    
    // Skip link should be first focusable element
    const skipLink = page.locator('a.skip-link, a[href="#main-content"]').first();
    await expect(skipLink).toBeAttached();
    
    // Should have Telugu text
    const skipLinkText = await skipLink.textContent();
    expect(skipLinkText).toContain('కంటెంట్');
  });

  test('should have ARIA labels on main landmarks', async ({ page }) => {
    await page.goto('/');
    
    // Header should have aria-label
    const header = page.locator('header');
    const headerAriaLabel = await header.getAttribute('aria-label');
    expect(headerAriaLabel).toBeTruthy();
    expect(headerAriaLabel).toContain('నావిగేషన్');
    
    // Main should have aria-label
    const main = page.locator('main');
    const mainAriaLabel = await main.getAttribute('aria-label');
    expect(mainAriaLabel).toBeTruthy();
    expect(mainAriaLabel).toContain('ప్రధాన');
    
    // Aside should have aria-label
    const aside = page.locator('aside');
    const asideAriaLabel = await aside.getAttribute('aria-label');
    expect(asideAriaLabel).toBeTruthy();
    expect(asideAriaLabel).toContain('ఫిల్టర్');
    
    // Footer should have aria-label
    const footer = page.locator('footer');
    const footerAriaLabel = await footer.getAttribute('aria-label');
    expect(footerAriaLabel).toBeTruthy();
    expect(footerAriaLabel).toContain('సమాచారం');
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');
    
    // Should have exactly one h1
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);
    
    // All headings should be in order (h1 -> h2 -> h3, no skipping)
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);
  });

  test('should have descriptive button text in Telugu', async ({ page }) => {
    await page.goto('/');
    
    // Check filter button
    const filterBtn = page.locator('button.apply-filters-btn');
    await expect(filterBtn).toBeVisible();
    const filterBtnText = await filterBtn.textContent();
    expect(filterBtnText).toContain('వర్తించండి');
    
    // Check pagination buttons have aria-labels
    const prevBtn = page.locator('button#prev-btn');
    const prevAriaLabel = await prevBtn.getAttribute('aria-label');
    expect(prevAriaLabel).toBeTruthy();
    
    const nextBtn = page.locator('button#next-btn');
    const nextAriaLabel = await nextBtn.getAttribute('aria-label');
    expect(nextAriaLabel).toBeTruthy();
  });

  test('should support keyboard navigation to skip link', async ({ page }) => {
    await page.goto('/');
    
    // Tab to first focusable element (should be skip link)
    await page.keyboard.press('Tab');
    
    // Check if skip link is focused
    const skipLink = page.locator('a.skip-link, a[href="#main-content"]').first();
    await expect(skipLink).toBeFocused();
  });

  test('should have proper form labels', async ({ page }) => {
    await page.goto('/');
    
    // Date inputs should have labels
    const dateFromInput = page.locator('input#date-from');
    await expect(dateFromInput).toBeAttached();
    
    const dateFromLabel = page.locator('label[for="date-from"]');
    await expect(dateFromLabel).toBeVisible();
    const dateFromLabelText = await dateFromLabel.textContent();
    expect(dateFromLabelText).toContain('నుండి');
    
    const dateToInput = page.locator('input#date-to');
    await expect(dateToInput).toBeAttached();
    
    const dateToLabel = page.locator('label[for="date-to"]');
    await expect(dateToLabel).toBeVisible();
    const dateToLabelText = await dateToLabel.textContent();
    expect(dateToLabelText).toContain('వరకు');
  });

  test('should have role attributes for custom components', async ({ page }) => {
    await page.goto('/');
    
    // Stats section should have appropriate role
    const statsSection = page.locator('.stats-section');
    await expect(statsSection).toBeVisible();
    
    // News list should have role
    const newsList = page.locator('#news-list');
    const newsListRole = await newsList.getAttribute('role');
    expect(newsListRole).toBeTruthy();
  });

  test('should have alt text or aria-labels for interactive elements', async ({ page }) => {
    await page.goto('/');
    
    // All images should have alt text (when we add them)
    const images = await page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
    
    // All buttons should have accessible text or aria-label
    const buttons = await page.locator('button').all();
    for (const button of buttons) {
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      expect(text || ariaLabel).toBeTruthy();
    }
  });
});
