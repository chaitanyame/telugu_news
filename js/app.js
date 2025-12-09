/**
 * Telugu News Aggregator - Main Application
 * Handles news loading, filtering, and display
 */

const App = (() => {
  // State management
  let state = {
    allNews: [],
    filteredNews: [],
    currentPage: 1,
    itemsPerPage: 10,
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

      // Sort by date (newest first)
      state.allNews.sort((a, b) => {
        const dateA = new Date(a.published_at || a.date);
        const dateB = new Date(b.published_at || b.date);
        return dateB - dateA;
      });

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

    // Filter news
    state.filteredNews = state.allNews.filter(news => {
      // Filter by slot
      if (selectedSlots.length > 0 && !selectedSlots.includes(news.slot)) {
        return false;
      }

      // Filter by date range
      if (dateFrom || dateTo) {
        const newsDate = news.date;
        if (dateFrom && newsDate < dateFrom) return false;
        if (dateTo && newsDate > dateTo) return false;
      }

      return true;
    });

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
    const total9pm = state.filteredNews.filter(n => n.slot === '9pm').length;
    const total7am = state.filteredNews.filter(n => n.slot === '7am').length;
    const total = state.filteredNews.length;

    if (elements.totalNews) elements.totalNews.textContent = total;
    if (elements.total9pm) elements.total9pm.textContent = total9pm;
    if (elements.total7am) elements.total7am.textContent = total7am;
  }

  /**
   * Render news list
   */
  function renderNews() {
    if (!elements.newsList) return;

    // Calculate pagination
    const startIdx = (state.currentPage - 1) * state.itemsPerPage;
    const endIdx = startIdx + state.itemsPerPage;
    const newsToShow = state.filteredNews.slice(startIdx, endIdx);

    // Clear existing content
    elements.newsList.innerHTML = '';

    if (newsToShow.length === 0) {
      elements.newsList.innerHTML = `
        <div class="no-news" role="status">
          <p>ఎటువంటి వార్తలు అందుబాటులో లేవు</p>
        </div>
      `;
      return;
    }

    // Render each news item
    newsToShow.forEach(news => {
      const newsCard = createNewsCard(news);
      elements.newsList.appendChild(newsCard);
    });
  }

  /**
   * Create a news card element
   */
  function createNewsCard(news) {
    const card = document.createElement('article');
    card.className = 'news-card';
    card.setAttribute('role', 'article');

    const slotBadge = news.slot === '9pm' ? 
      '<span class="slot-badge slot-9pm">9 PM</span>' :
      '<span class="slot-badge slot-7am">7 AM</span>';

    const date = new Date(news.date);
    const formattedDate = date.toLocaleDateString('te-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });

    card.innerHTML = `
      <div class="news-header">
        ${slotBadge}
        <time datetime="${news.date}" class="news-date">${formattedDate}</time>
      </div>
      <h3 class="news-title">${escapeHtml(news.title)}</h3>
      <ul class="news-summary">
        ${(news.summary || []).map(point => `<li>${escapeHtml(point)}</li>`).join('')}
      </ul>
      <div class="news-footer">
        <a href="https://www.youtube.com/watch?v=${news.video_id}" 
           target="_blank" 
           rel="noopener noreferrer"
           class="youtube-btn"
           aria-label="YouTube లో వీడియో చూడండి">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 16.5l6-4.5-6-4.5v9zM23 12s0-3.85-.46-5.58c-.25-.95-.98-1.69-1.94-1.94C18.88 4 12 4 12 4s-6.88 0-8.6.48c-.96.25-1.69.99-1.94 1.94C1 8.15 1 12 1 12s0 3.85.46 5.58c.25.95.98 1.69 1.94 1.94C5.12 20 12 20 12 20s6.88 0 8.6-.48c.96-.25 1.69-.99 1.94-1.94C23 15.85 23 12 23 12z"/>
          </svg>
          YouTube లో చూడండి
        </a>
      </div>
    `;

    return card;
  }

  /**
   * Change page (pagination)
   */
  function changePage(direction) {
    const totalPages = Math.ceil(state.filteredNews.length / state.itemsPerPage);
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
    const totalPages = Math.ceil(state.filteredNews.length / state.itemsPerPage);

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
