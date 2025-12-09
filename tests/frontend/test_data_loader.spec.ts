import { test, expect } from '@playwright/test';

test.describe('Data Loader', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the page before each test
    await page.goto('/');
  });

  test('should have fetchIndex function available', async ({ page }) => {
    const hasFetchIndex = await page.evaluate(() => {
      return typeof window.DataLoader !== 'undefined' && 
             typeof window.DataLoader.fetchIndex === 'function';
    });
    expect(hasFetchIndex).toBeTruthy();
  });

  test('should have fetchNewsForDate function available', async ({ page }) => {
    const hasFetchNewsForDate = await page.evaluate(() => {
      return typeof window.DataLoader !== 'undefined' && 
             typeof window.DataLoader.fetchNewsForDate === 'function';
    });
    expect(hasFetchNewsForDate).toBeTruthy();
  });

  test('should fetch index.json successfully', async ({ page }) => {
    // Create a mock index.json file
    await page.route('**/data/index.json*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          dates: ['2025-12-09', '2025-12-08'],
          last_updated: '2025-12-09T12:00:00Z'
        })
      });
    });

    const result = await page.evaluate(async () => {
      return await window.DataLoader.fetchIndex();
    });

    expect(result).toBeTruthy();
    expect(result.dates).toEqual(['2025-12-09', '2025-12-08']);
    expect(result.last_updated).toBe('2025-12-09T12:00:00Z');
  });

  test('should handle index.json fetch errors gracefully', async ({ page }) => {
    // Mock a failed request
    await page.route('**/data/index.json*', async (route) => {
      await route.abort('failed');
    });

    const result = await page.evaluate(async () => {
      return await window.DataLoader.fetchIndex();
    });

    // Should return fallback data
    expect(result).toBeTruthy();
    expect(result.dates).toEqual([]);
    expect(result.error).toBeTruthy();
  });

  test('should fetch news for a specific date', async ({ page }) => {
    // Mock the news file for a specific date
    await page.route('**/data/2025-12-09.json*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          date: '2025-12-09',
          news: [
            {
              slot: '9pm',
              video_id: 'test123',
              title: 'Test News',
              summary: ['Point 1', 'Point 2']
            }
          ]
        })
      });
    });

    const result = await page.evaluate(async () => {
      return await window.DataLoader.fetchNewsForDate('2025-12-09');
    });

    expect(result).toBeTruthy();
    expect(result.date).toBe('2025-12-09');
    expect(result.news).toHaveLength(1);
    expect(result.news[0].slot).toBe('9pm');
  });

  test('should handle news fetch errors gracefully', async ({ page }) => {
    await page.route('**/data/2025-12-09.json*', async (route) => {
      await route.abort('failed');
    });

    const result = await page.evaluate(async () => {
      return await window.DataLoader.fetchNewsForDate('2025-12-09');
    });

    // Should return fallback data
    expect(result).toBeTruthy();
    expect(result.date).toBe('2025-12-09');
    expect(result.news).toEqual([]);
    expect(result.error).toBeTruthy();
  });

  test('should add cache busting timestamp to requests', async ({ page }) => {
    let requestUrl = '';
    
    await page.route('**/data/index.json*', async (route) => {
      requestUrl = route.request().url();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ dates: [], last_updated: '' })
      });
    });

    await page.evaluate(async () => {
      await window.DataLoader.fetchIndex();
    });

    // Check if URL contains timestamp parameter
    expect(requestUrl).toContain('?t=');
  });

  test('should handle 404 errors for missing news files', async ({ page }) => {
    await page.route('**/data/2025-01-01.json*', async (route) => {
      await route.fulfill({ status: 404 });
    });

    const result = await page.evaluate(async () => {
      return await window.DataLoader.fetchNewsForDate('2025-01-01');
    });

    expect(result).toBeTruthy();
    expect(result.date).toBe('2025-01-01');
    expect(result.news).toEqual([]);
    expect(result.error).toBeTruthy();
  });

  test('should handle malformed JSON gracefully', async ({ page }) => {
    await page.route('**/data/index.json*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: 'invalid json {'
      });
    });

    const result = await page.evaluate(async () => {
      return await window.DataLoader.fetchIndex();
    });

    expect(result).toBeTruthy();
    expect(result.dates).toEqual([]);
    expect(result.error).toBeTruthy();
  });
});
