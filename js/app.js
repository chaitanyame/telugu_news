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
    currentPage: 1,
    itemsPerPage: 1,       // 1 date per page (single date with both slots)
    filters: {
      slots: ['9pm', '7am'],
      dateFrom: null,
      dateTo: null
    },
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
    renderStats();
    renderNews();
    updatePaginationControls();
  }

  /**
   * Cache DOM elements for performance
   */
  function cacheElements() {
    elements.newsList = document.getElementById('news-list');
    elements.prevBtn = document.getElementById('prev-btn');
    elements.nextBtn = document.getElementById('next-btn');
    elements.pageInfo = document.getElementById('page-info');
    elements.filterBtn = document.querySelector('.apply-filters-btn');
    elements.dateFrom = document.getElementById('date-from');
    elements.dateTo = document.getElementById('date-to');
    elements.slotCheckboxes = document.querySelectorAll('input[name="slot"]');
    elements.totalNews = document.getElementById('total-news');
    elements.total9pm = document.getElementById('total-9pm');
    elements.total7am = document.getElementById('total-7am');
  }

  /**
   * Attach event listeners
   */
  function attachEventListeners() {
    // Pagination buttons
    elements.prevBtn?.addEventListener('click', () => changePage(-1));
    elements.nextBtn?.addEventListener('click', () => changePage(1));

    // Filter button
    elements.filterBtn?.addEventListener('click', applyFilters);

    // Slot checkboxes
    elements.slotCheckboxes?.forEach(checkbox => {
      checkbox.addEventListener('change', applyFilters);
    });
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

      // Apply initial filters
      applyFilters();
      
    } catch (error) {
      console.error('Error loading data:', error);
      showError('డేటా లోడ్ చేయడంలో లోపం ఏర్పడింది');
    } finally {
      hideLoading();
    }
  }

  /**
   * Apply filters to news list
   */
  function applyFilters() {
    // Get selected slots
    const selectedSlots = Array.from(elements.slotCheckboxes || [])
      .filter(cb => cb.checked)
      .map(cb => cb.value);

    // Get date range
    const dateFrom = elements.dateFrom?.value;
    const dateTo = elements.dateTo?.value;

    // Filter dates based on criteria
    state.filteredDates = Object.keys(state.newsByDate).filter(dateKey => {
      const dateData = state.newsByDate[dateKey];
      
      // Check if date has at least one matching slot
      const hasMatchingSlot = selectedSlots.length === 0 || 
        selectedSlots.some(slot => dateData.slots[slot]);
      
      if (!hasMatchingSlot) return false;

      // Filter by date range
      if (dateFrom && dateKey < dateFrom) return false;
      if (dateTo && dateKey > dateTo) return false;

      return true;
    }).sort((a, b) => b.localeCompare(a)); // Sort newest first

    // Reset to first page
    state.currentPage = 1;

    // Update UI
    renderStats();
    renderNews();
    updatePaginationControls();
  }

  /**
   * Render statistics
   */
  function renderStats() {
    // Count total slots across all filtered dates
    let total9pm = 0;
    let total7am = 0;
    
    state.filteredDates.forEach(dateKey => {
      const dateData = state.newsByDate[dateKey];
      if (dateData.slots['9pm']) total9pm++;
      if (dateData.slots['7am']) total7am++;
    });

    const total = total9pm + total7am;

    if (elements.totalNews) elements.totalNews.textContent = total;
    if (elements.total9pm) elements.total9pm.textContent = total9pm;
    if (elements.total7am) elements.total7am.textContent = total7am;
  }

  /**
   * Render news list - one date per page with both slots
   */
  function renderNews() {
    if (!elements.newsList) return;

    // Calculate pagination (by date, not by individual news items)
    const startIdx = (state.currentPage - 1) * state.itemsPerPage;
    const endIdx = startIdx + state.itemsPerPage;
    const datesToShow = state.filteredDates.slice(startIdx, endIdx);

    // Clear existing content
    elements.newsList.innerHTML = '';

    if (datesToShow.length === 0) {
      elements.newsList.innerHTML = `
        <div class="no-news" role="status">
          <p>ఎటువంటి వార్తలు అందుబాటులో లేవు</p>
        </div>
      `;
      return;
    }

    // Render each date's news (combined card for all slots)
    datesToShow.forEach(dateKey => {
      const dateData = state.newsByDate[dateKey];
      const dateCard = createDateCard(dateData);
      elements.newsList.appendChild(dateCard);
    });
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
   * Change page (pagination by date)
   */
  function changePage(direction) {
    const totalPages = Math.ceil(state.filteredDates.length / state.itemsPerPage);
    const newPage = state.currentPage + direction;

    if (newPage < 1 || newPage > totalPages) return;

    state.currentPage = newPage;
    renderNews();
    updatePaginationControls();

    // Scroll to top of news list
    elements.newsList?.scrollIntoView({ behavior: 'smooth' });
  }

  /**
   * Update pagination controls
   */
  function updatePaginationControls() {
    const totalPages = Math.ceil(state.filteredDates.length / state.itemsPerPage);

    // Update page info
    if (elements.pageInfo) {
      elements.pageInfo.textContent = `పేజీ ${state.currentPage} / ${totalPages || 1}`;
    }

    // Update button states
    if (elements.prevBtn) {
      elements.prevBtn.disabled = state.currentPage <= 1;
    }
    if (elements.nextBtn) {
      elements.nextBtn.disabled = state.currentPage >= totalPages;
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
    applyFilters,
    changePage
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
