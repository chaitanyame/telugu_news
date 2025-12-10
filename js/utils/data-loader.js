/**
 * Data Loader Utility
 * Handles fetching news data from JSON files with error handling and caching
 */

const DataLoader = (() => {
  // Get base path - use relative path to work on both local and GitHub Pages
  const BASE_PATH = './data';

  /**
   * Fetch the index file containing all available dates
   * @returns {Promise<{dates: string[], last_updated: string, error?: string}>}
   */
  async function fetchIndex() {
    try {
      // Add cache busting timestamp
      const timestamp = Date.now();
      const response = await fetch(`${BASE_PATH}/index.json?t=${timestamp}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Handle new format: array of {date, slots} objects
      if (Array.isArray(data)) {
        return {
          dates: data.map(item => item.date),
          last_updated: new Date().toISOString()
        };
      }
      
      // Handle old format: {dates: [], last_updated: ""}
      return data;
    } catch (error) {
      console.error('Error fetching index:', error);
      return {
        dates: [],
        last_updated: '',
        error: error.message || 'Failed to fetch index'
      };
    }
  }

  /**
   * Fetch news data for a specific date
   * @param {string} date - Date in YYYY-MM-DD format
   * @returns {Promise<{date: string, news: Array, error?: string}>}
   */
  async function fetchNewsForDate(date) {
    try {
      // Convert date to archive path format: YYYY-MM-DD -> archive/YYYY-MM/YYYY-MM-DD.json
      const [year, month] = date.split('-');
      const archivePath = `${BASE_PATH}/archive/${year}-${month}/${date}.json`;
      
      // Add cache busting timestamp
      const timestamp = Date.now();
      const response = await fetch(`${archivePath}?t=${timestamp}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          return {
            date: date,
            news: [],
            error: 'No news available for this date'
          };
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Convert new format to old format for compatibility
      // New: {date, slots: {9pm: {...}, 7am: {...}}}
      // Old: {date, news: [{slot: "9pm", ...}, {slot: "7am", ...}]}
      if (data.slots) {
        const newsArray = [];
        if (data.slots['9pm']) {
          newsArray.push({
            slot: '9pm',
            ...data.slots['9pm']
          });
        }
        if (data.slots['7am']) {
          newsArray.push({
            slot: '7am',
            ...data.slots['7am']
          });
        }
        return {
          date: data.date,
          news: newsArray
        };
      }
      
      return data;
    } catch (error) {
      console.error(`Error fetching news for ${date}:`, error);
      return {
        date: date,
        news: [],
        error: error.message || 'Failed to fetch news'
      };
    }
  }

  /**
   * Fetch news for multiple dates
   * @param {string[]} dates - Array of dates in YYYY-MM-DD format
   * @returns {Promise<Array>}
   */
  async function fetchNewsForDates(dates) {
    const promises = dates.map(date => fetchNewsForDate(date));
    return await Promise.all(promises);
  }

  /**
   * Get the latest news (most recent date)
   * @returns {Promise<{date: string, news: Array, error?: string}>}
   */
  async function fetchLatestNews() {
    try {
      const index = await fetchIndex();
      if (index.error || index.dates.length === 0) {
        return {
          date: '',
          news: [],
          error: 'No news available'
        };
      }
      
      // Get the first date (most recent)
      const latestDate = index.dates[0];
      return await fetchNewsForDate(latestDate);
    } catch (error) {
      console.error('Error fetching latest news:', error);
      return {
        date: '',
        news: [],
        error: error.message || 'Failed to fetch latest news'
      };
    }
  }

  // Public API
  return {
    fetchIndex,
    fetchNewsForDate,
    fetchNewsForDates,
    fetchLatestNews
  };
})();

// Make it available globally for the app
window.DataLoader = DataLoader;
