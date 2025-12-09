import { test, expect } from '@playwright/test';

/**
 * Feature #21: Create index.html with Semantic Structure
 * 
 * TDD Workflow:
 * 1. RED: Create tests that expect HTML structure (will fail)
 * 2. GREEN: Create index.html with semantic elements
 * 3. REFACTOR: Verify all tests pass
 */

test.describe('HTML Structure', () => {
  test('should have valid HTML5 doctype and structure', async ({ page }) => {
    await page.goto('/');
    
    // Check for proper HTML structure
    const html = page.locator('html');
    await expect(html).toHaveAttribute('lang', 'te');
    
    // Check meta tags
    const metaCharset = page.locator('meta[charset]');
    await expect(metaCharset).toHaveAttribute('charset', 'UTF-8');
    
    const metaViewport = page.locator('meta[name="viewport"]');
    await expect(metaViewport).toHaveAttribute('content', /width=device-width/);
  });

  test('should have site title in Telugu', async ({ page }) => {
    await page.goto('/');
    
    const title = await page.title();
    expect(title).toContain('తెలుగు'); // Should contain Telugu text
  });

  test('should have semantic header element', async ({ page }) => {
    await page.goto('/');
    
    const header = page.locator('header');
    await expect(header).toBeVisible();
    
    // Header should have site title in Telugu
    const headerText = await header.textContent();
    expect(headerText).toContain('తెలుగు');
  });

  test('should have main element with aside and article', async ({ page }) => {
    await page.goto('/');
    
    // Check for main element
    const main = page.locator('main');
    await expect(main).toBeVisible();
    
    // Check for aside (sidebar)
    const aside = page.locator('aside');
    await expect(aside).toBeVisible();
    
    // Check for article (content)
    const article = page.locator('article');
    await expect(article).toBeVisible();
  });

  test('should have semantic footer element', async ({ page }) => {
    await page.goto('/');
    
    const footer = page.locator('footer');
    await expect(footer).toBeVisible();
    
    // Footer should have last updated timestamp
    const footerText = await footer.textContent();
    expect(footerText).toMatch(/\d{4}/); // Should contain year
  });

  test('should load Google Fonts for Telugu', async ({ page }) => {
    await page.goto('/');
    
    // Check for Google Fonts link (stylesheet only, not preconnect)
    const googleFontsLink = page.locator('link[href*="fonts.googleapis.com/css2"]');
    await expect(googleFontsLink).toHaveCount(1);
    
    // Should include Noto Sans Telugu
    const href = await googleFontsLink.getAttribute('href');
    expect(href).toContain('Noto+Sans+Telugu');
  });

  test('should have proper document structure hierarchy', async ({ page }) => {
    await page.goto('/');
    
    // Verify semantic structure exists
    const body = page.locator('body');
    await expect(body).toBeVisible();
    
    // Verify header comes before main
    const header = page.locator('header');
    const main = page.locator('main');
    const footer = page.locator('footer');
    
    await expect(header).toBeVisible();
    await expect(main).toBeVisible();
    await expect(footer).toBeVisible();
    
    // Get positions to verify order
    const headerBox = await header.boundingBox();
    const mainBox = await main.boundingBox();
    const footerBox = await footer.boundingBox();
    
    expect(headerBox!.y).toBeLessThan(mainBox!.y);
    expect(mainBox!.y).toBeLessThan(footerBox!.y);
  });
});
