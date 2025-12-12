/**
 * Telugu News Aggregator - Main Application
 * Handles news loading, filtering, and display
 * Single date per page with combined 9 PM and 7 AM slots
 */

const App = (() => {
  // State management
  let state = {
    allNews: [],           // All news items
    newsByDate: {},        // News grouped by date: { 'YYYY-MM-DD': { date, slots: { '9pm': news, '7am': news } } }
    filteredDates: [],     // Filtered date keys to display
    selectedDate: null,    // Currently selected date
    availableDates: [],
    loading: false
  };

  // DOM elements (will be cached on init)
  const elements = {};

  /**
   * Initialize the application
   */
  async function init() {
    cacheElements();
    attachEventListeners();
    await loadInitialData();
  }

  /**
   * Cache DOM elements for performance
   */
  function cacheElements() {
    elements.newsList = document.getElementById('news-list');
    elements.prevBtn = document.getElementById('prev-btn');
    elements.nextBtn = document.getElementById('next-btn');
    elements.pageInfo = document.getElementById('page-info');
    elements.datesList = document.getElementById('dates-list');
  }

  /**
   * Attach event listeners
   */
  function attachEventListeners() {
    // Pagination buttons
    elements.prevBtn?.addEventListener('click', () => navigateDates(-1));
    elements.nextBtn?.addEventListener('click', () => navigateDates(1));
  }

  /**
   * Load initial data from server
   */
  async function loadInitialData() {
    showLoading();
    
    try {
      // Fetch index to get available dates
      const index = await window.DataLoader.fetchIndex();
      
      if (index.error) {
        showError('డేటా లోడ్ చేయడంలో లోపం ఏర్పడింది');
        return;
      }

      state.availableDates = index.dates || [];

      // Fetch news for all available dates
      const newsPromises = state.availableDates.map(date => 
        window.DataLoader.fetchNewsForDate(date)
      );
      
      const allNewsData = await Promise.all(newsPromises);
      
      // Flatten all news into single array
      state.allNews = allNewsData.flatMap(dateData => 
        (dateData.news || []).map(newsItem => ({
          ...newsItem,
          date: dateData.date
        }))
      );

      // Group news by date with slots
      state.newsByDate = {};
      state.allNews.forEach(news => {
        const dateKey = news.date;
        if (!state.newsByDate[dateKey]) {
          state.newsByDate[dateKey] = {
            date: dateKey,
            slots: {}
          };
        }
        // Store news in appropriate slot (avoid duplicates by video_id)
        if (!state.newsByDate[dateKey].slots[news.slot] || 
            state.newsByDate[dateKey].slots[news.slot].video_id === news.video_id) {
          state.newsByDate[dateKey].slots[news.slot] = news;
        }
      });

      // Get sorted date keys (newest first)
      state.filteredDates = Object.keys(state.newsByDate).sort((a, b) => b.localeCompare(a));

      // Select the most recent date by default
      if (state.filteredDates.length > 0) {
        state.selectedDate = state.filteredDates[0];
      }

      // Render the dates list and news
      renderDatesList();
      renderNews();
      updatePaginationControls();
      
    } catch (error) {
      console.error('Error loading data:', error);
      showError('డేటా లోడ్ చేయడంలో లోపం ఏర్పడింది');
    } finally {
      hideLoading();
    }
  }

  /**
   * Render the dates list in sidebar
   */
  function renderDatesList() {
    if (!elements.datesList) return;

    if (state.filteredDates.length === 0) {
      elements.datesList.innerHTML = '<p class="no-dates">తేదీలు అందుబాటులో లేవు</p>';
      return;
    }

    elements.datesList.innerHTML = state.filteredDates.map(dateKey => {
      const [year, month, day] = dateKey.split('-').map(Number);
      const formattedDate = `${day}-${month}-${year}`;
      const isSelected = dateKey === state.selectedDate;
      return `
        <button class="date-item ${isSelected ? 'selected' : ''}" 
                data-date="${dateKey}"
                aria-pressed="${isSelected}">
          ${formattedDate}
        </button>
      `;
    }).join('');

    // Attach click handlers
    elements.datesList.querySelectorAll('.date-item').forEach(btn => {
      btn.addEventListener('click', () => selectDate(btn.dataset.date));
    });
  }

  /**
   * Select a specific date
   */
  function selectDate(dateKey) {
    state.selectedDate = dateKey;
    renderDatesList();
    renderNews();
    updatePaginationControls();
    
    // Scroll to news content on mobile
    elements.newsList?.scrollIntoView({ behavior: 'smooth' });
  }

  /**
   * Navigate between dates (prev/next)
   */
  function navigateDates(direction) {
    const currentIdx = state.filteredDates.indexOf(state.selectedDate);
    const newIdx = currentIdx + direction;
    
    if (newIdx >= 0 && newIdx < state.filteredDates.length) {
      selectDate(state.filteredDates[newIdx]);
    }
  }

  /**
   * Apply filters to news list
   */
  function applyFilters() {
    renderDatesList();
    renderNews();
    updatePaginationControls();
  }

  /**
   * Render news list - show selected date's news
   */
  function renderNews() {
    if (!elements.newsList) return;

    // Clear existing content
    elements.newsList.innerHTML = '';

    if (!state.selectedDate || !state.newsByDate[state.selectedDate]) {
      elements.newsList.innerHTML = `
        <div class="no-news" role="status">
          <p>ఎటువంటి వార్తలు అందుబాటులో లేవు</p>
        </div>
      `;
      return;
    }

    // Render selected date's news
    const dateData = state.newsByDate[state.selectedDate];
    const dateCard = createDateCard(dateData);
    elements.newsList.appendChild(dateCard);
  }

  /**
   * Create a date card element with both 9 PM and 7 AM slots
   */
  function createDateCard(dateData) {
    const card = document.createElement('article');
    card.className = 'news-card date-card';
    card.setAttribute('role', 'article');

    // Parse date correctly to avoid timezone issues
    // dateData.date is in 'YYYY-MM-DD' format
    const [year, month, day] = dateData.date.split('-').map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed
    const formattedDate = date.toLocaleDateString('te-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });

    // Build slot sections
    let slotsHtml = '';
    
    // Helper to format news item with category styling
    function formatNewsItem(point) {
      const escaped = escapeHtml(point);
      // Check if starts with a category prefix (e.g., "రాజకీయాలు:")
      const colonIndex = escaped.indexOf(':');
      if (colonIndex > 0 && colonIndex < 20) {
        const category = escaped.substring(0, colonIndex);
        const content = escaped.substring(colonIndex + 1).trim();
        return `<span class="news-category">${category}</span><span class="news-content">${content}</span>`;
      }
      return `<span class="news-content">${escaped}</span>`;
    }
    
    // Evening news (9 PM) section
    if (dateData.slots['9pm']) {
      const evening = dateData.slots['9pm'];
      slotsHtml += `
        <div class="slot-section evening-section">
          <div class="slot-header">
            <span class="slot-badge slot-9pm">సాయంత్రం వార్తలు (9 PM)</span>
          </div>
          <ul class="news-summary">
            ${(evening.summary || []).map(point => `<li>${formatNewsItem(point)}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    // Morning news (7 AM) section
    if (dateData.slots['7am']) {
      const morning = dateData.slots['7am'];
      slotsHtml += `
        <div class="slot-section morning-section">
          <div class="slot-header">
            <span class="slot-badge slot-7am">ఉదయం వార్తలు (7 AM)</span>
          </div>
          <ul class="news-summary">
            ${(morning.summary || []).map(point => `<li>${formatNewsItem(point)}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    // If no slots available
    if (!slotsHtml) {
      slotsHtml = '<p class="no-slots">ఈ తేదీకి వార్తలు అందుబాటులో లేవు</p>';
    }

    card.innerHTML = `
      <div class="date-header">
        <time datetime="${dateData.date}" class="news-date">${formattedDate}</time>
      </div>
      <div class="slots-container">
        ${slotsHtml}
      </div>
    `;

    return card;
  }

  /**
   * Update pagination controls (now for prev/next date navigation)
   */
  function updatePaginationControls() {
    const currentIdx = state.filteredDates.indexOf(state.selectedDate);
    const totalDates = state.filteredDates.length;

    // Update page info
    if (elements.pageInfo) {
      elements.pageInfo.textContent = totalDates > 0 
        ? `${currentIdx + 1} / ${totalDates} తేదీలు`
        : '0 తేదీలు';
    }

    // Update button states (prev = newer date, next = older date)
    if (elements.prevBtn) {
      elements.prevBtn.disabled = currentIdx <= 0;
    }
    if (elements.nextBtn) {
      elements.nextBtn.disabled = currentIdx >= totalDates - 1;
    }
  }

  /**
   * Show loading state
   */
  function showLoading() {
    state.loading = true;
    if (elements.newsList) {
      elements.newsList.innerHTML = `
        <div class="loading" role="status" aria-live="polite">
          <p>వార్తలు లోడ్ అవుతున్నాయి...</p>
        </div>
      `;
    }
  }

  /**
   * Hide loading state
   */
  function hideLoading() {
    state.loading = false;
  }

  /**
   * Show error message
   */
  function showError(message) {
    if (elements.newsList) {
      elements.newsList.innerHTML = `
        <div class="error" role="alert">
          <p>${escapeHtml(message)}</p>
        </div>
      `;
    }
  }

  /**
   * Escape HTML to prevent XSS
   */
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Public API
  return {
    init,
    selectDate,
    navigateDates
  };
})();

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => App.init());
} else {
  App.init();
}

// Make app available globally for debugging
window.App = App;
