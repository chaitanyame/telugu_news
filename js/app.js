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
    loading: false,
    viewMode: 'list',      // 'list' or 'grid'
    sidebarView: 'month',  // 'month' or 'list'
    displayedDatesCount: 5, // For load more functionality
    theme: 'light'         // 'light' or 'dark'
  };

  // DOM elements (will be cached on init)
  const elements = {};
  
  // Touch handling for swipe gestures
  let touchStartX = 0;
  let touchEndX = 0;
  const SWIPE_THRESHOLD = 50;

  /**
   * Initialize the application
   */
  async function init() {
    cacheElements();
    initTheme();
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
    elements.themeToggle = document.getElementById('theme-toggle');
    elements.loadMoreContainer = document.getElementById('load-more-container');
    elements.loadMoreBtn = document.getElementById('load-more-btn');
    elements.loadMoreInfo = document.getElementById('load-more-info');
    // Mobile elements
    elements.mobileNav = document.getElementById('mobile-nav');
    elements.mobileHomeBtn = document.getElementById('mobile-home-btn');
    elements.mobileDatesBtn = document.getElementById('mobile-dates-btn');
    elements.mobilePrevBtn = document.getElementById('mobile-prev-btn');
    elements.mobileNextBtn = document.getElementById('mobile-next-btn');
    elements.mobileDateModal = document.getElementById('mobile-date-modal');
    elements.modalOverlay = document.getElementById('modal-overlay');
    elements.modalClose = document.getElementById('modal-close');
    elements.modalDatesList = document.getElementById('modal-dates-list');
  }

  /**
   * Initialize theme from localStorage or system preference
   */
  function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      state.theme = savedTheme;
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      state.theme = 'dark';
    }
    document.documentElement.setAttribute('data-theme', state.theme);
  }

  /**
   * Toggle theme
   */
  function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
  }

  /**
   * Attach event listeners
   */
  function attachEventListeners() {
    // Pagination buttons
    elements.prevBtn?.addEventListener('click', () => navigateDates(-1));
    elements.nextBtn?.addEventListener('click', () => navigateDates(1));
    
    // Theme toggle
    elements.themeToggle?.addEventListener('click', toggleTheme);
    
    // View mode toggle
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', () => setViewMode(btn.dataset.view));
    });
    
    // Sidebar view toggle
    document.querySelectorAll('.sidebar-view-btn').forEach(btn => {
      btn.addEventListener('click', () => setSidebarView(btn.dataset.sidebarView));
    });
    
    // Load more button
    elements.loadMoreBtn?.addEventListener('click', loadMoreDates);
    
    // Mobile navigation
    elements.mobileHomeBtn?.addEventListener('click', () => {
      if (state.filteredDates.length > 0) {
        selectDate(state.filteredDates[0]);
      }
    });
    elements.mobileDatesBtn?.addEventListener('click', openDateModal);
    elements.mobilePrevBtn?.addEventListener('click', () => navigateDates(-1));
    elements.mobileNextBtn?.addEventListener('click', () => navigateDates(1));
    
    // Modal controls
    elements.modalOverlay?.addEventListener('click', closeDateModal);
    elements.modalClose?.addEventListener('click', closeDateModal);
    
    // Swipe gestures for mobile
    document.addEventListener('touchstart', handleTouchStart, { passive: true });
    document.addEventListener('touchend', handleTouchEnd, { passive: true });
    
    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboard);
  }

  /**
   * Handle touch start for swipe detection
   */
  function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].screenX;
  }

  /**
   * Handle touch end for swipe detection
   */
  function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }

  /**
   * Handle swipe gesture
   */
  function handleSwipe() {
    const diff = touchStartX - touchEndX;
    if (Math.abs(diff) > SWIPE_THRESHOLD) {
      if (diff > 0) {
        // Swipe left - next date (older)
        navigateDates(1);
      } else {
        // Swipe right - prev date (newer)
        navigateDates(-1);
      }
    }
  }

  /**
   * Handle keyboard navigation
   */
  function handleKeyboard(e) {
    if (e.key === 'ArrowLeft') {
      navigateDates(-1);
    } else if (e.key === 'ArrowRight') {
      navigateDates(1);
    } else if (e.key === 'Escape' && elements.mobileDateModal?.classList.contains('open')) {
      closeDateModal();
    }
  }

  /**
   * Open date picker modal (mobile)
   */
  function openDateModal() {
    if (!elements.mobileDateModal) return;
    elements.mobileDateModal.classList.add('open');
    elements.mobileDateModal.setAttribute('aria-hidden', 'false');
    renderModalDates();
    document.body.style.overflow = 'hidden';
  }

  /**
   * Close date picker modal
   */
  function closeDateModal() {
    if (!elements.mobileDateModal) return;
    elements.mobileDateModal.classList.remove('open');
    elements.mobileDateModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  /**
   * Render dates in modal (grouped by month)
   */
  function renderModalDates() {
    if (!elements.modalDatesList) return;
    elements.modalDatesList.innerHTML = renderGroupedDates(state.filteredDates, true);
    attachDateClickHandlers(elements.modalDatesList);
  }

  /**
   * Set view mode (list/grid)
   */
  function setViewMode(mode) {
    state.viewMode = mode;
    
    // Update button states
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === mode);
      btn.setAttribute('aria-pressed', btn.dataset.view === mode);
    });
    
    // Update news list class
    if (elements.newsList) {
      elements.newsList.classList.toggle('grid-view', mode === 'grid');
    }
  }

  /**
   * Set sidebar view mode (month/list)
   */
  function setSidebarView(view) {
    state.sidebarView = view;
    
    // Update button states
    document.querySelectorAll('.sidebar-view-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.sidebarView === view);
    });
    
    renderDatesList();
  }

  /**
   * Load more dates (hybrid pagination)
   */
  function loadMoreDates() {
    state.displayedDatesCount += 5;
    renderNews();
    updateLoadMoreButton();
  }

  /**
   * Update load more button visibility and info
   */
  function updateLoadMoreButton() {
    if (!elements.loadMoreContainer) return;
    
    const total = state.filteredDates.length;
    const displayed = Math.min(state.displayedDatesCount, total);
    
    if (displayed >= total) {
      elements.loadMoreContainer.style.display = 'none';
    } else {
      elements.loadMoreContainer.style.display = 'block';
      if (elements.loadMoreInfo) {
        elements.loadMoreInfo.textContent = `${displayed} / ${total} తేదీలు చూపబడుతున్నాయి`;
      }
    }
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

    if (state.sidebarView === 'month') {
      elements.datesList.innerHTML = renderGroupedDates(state.filteredDates, false);
    } else {
      elements.datesList.innerHTML = renderFlatDates(state.filteredDates);
    }

    attachDateClickHandlers(elements.datesList);
    attachMonthToggleHandlers();
  }

  /**
   * Render dates grouped by month
   */
  function renderGroupedDates(dates, isModal = false) {
    const grouped = {};
    
    dates.forEach(dateKey => {
      const [year, month] = dateKey.split('-');
      const monthKey = `${year}-${month}`;
      if (!grouped[monthKey]) {
        grouped[monthKey] = [];
      }
      grouped[monthKey].push(dateKey);
    });

    return Object.entries(grouped).map(([monthKey, monthDates]) => {
      const [year, month] = monthKey.split('-');
      const monthDate = new Date(year, month - 1, 1);
      const monthName = monthDate.toLocaleDateString('te-IN', { 
        year: 'numeric', 
        month: 'long' 
      });
      
      const isExpanded = monthDates.some(d => d === state.selectedDate) || monthDates[0] === dates[0];
      
      return `
        <div class="month-group" data-month="${monthKey}">
          <div class="month-header" role="button" aria-expanded="${isExpanded}">
            <span>${monthName}</span>
            <span class="month-count">${monthDates.length}</span>
          </div>
          <div class="month-dates ${isExpanded ? '' : 'collapsed'}">
            ${monthDates.map(dateKey => renderDateItem(dateKey)).join('')}
          </div>
        </div>
      `;
    }).join('');
  }

  /**
   * Render flat list of dates
   */
  function renderFlatDates(dates) {
    return dates.map(dateKey => renderDateItem(dateKey)).join('');
  }

  /**
   * Render a single date item
   */
  function renderDateItem(dateKey) {
    const [year, month, day] = dateKey.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    const formattedDate = date.toLocaleDateString('te-IN', {
      month: 'short',
      day: 'numeric',
      weekday: 'short'
    });
    const isSelected = dateKey === state.selectedDate;
    const newsCount = getNewsCountForDate(dateKey);
    
    return `
      <button class="date-item ${isSelected ? 'selected' : ''}" 
              data-date="${dateKey}"
              aria-pressed="${isSelected}">
        <span class="date-text">${formattedDate}</span>
        <span class="news-count-badge" title="${newsCount} వార్తలు">${newsCount}</span>
      </button>
    `;
  }

  /**
   * Get news count for a specific date
   */
  function getNewsCountForDate(dateKey) {
    const dateData = state.newsByDate[dateKey];
    if (!dateData) return 0;
    
    let count = 0;
    if (dateData.slots['9pm']?.summary) count += dateData.slots['9pm'].summary.length;
    if (dateData.slots['7am']?.summary) count += dateData.slots['7am'].summary.length;
    return count;
  }

  /**
   * Attach click handlers to date items
   */
  function attachDateClickHandlers(container) {
    container.querySelectorAll('.date-item').forEach(btn => {
      btn.addEventListener('click', () => {
        selectDate(btn.dataset.date);
        closeDateModal(); // Close modal if open
      });
    });
  }

  /**
   * Attach toggle handlers to month headers
   */
  function attachMonthToggleHandlers() {
    document.querySelectorAll('.month-header').forEach(header => {
      header.addEventListener('click', () => {
        const monthDates = header.nextElementSibling;
        const isCollapsed = monthDates.classList.contains('collapsed');
        monthDates.classList.toggle('collapsed');
        header.setAttribute('aria-expanded', isCollapsed);
      });
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

    // Category order and colors mapping
    const categoryOrder = [
      'రాజకీయాలు',
      'వ్యాపారం',
      'నేరం',
      'క్రీడలు',
      'వినోదం',
      'సినిమా',
      'ఆరోగ్యం',
      'వ్యవసాయం',
      'టెక్నాలజీ',
      'అంతర్జాతీయం',
      'విద్య',
      'వాతావరణం',
      'ఇతరం'
    ];

    // Helper to extract category from news item
    function extractCategory(point) {
      const colonIndex = point.indexOf(':');
      if (colonIndex > 0 && colonIndex < 30) {
        let category = point.substring(0, colonIndex).trim();
        // Handle sub-categories like "వ్యాపారం - ఆంధ్రప్రదేశ్"
        const dashIndex = category.indexOf(' - ');
        if (dashIndex > 0) {
          category = category.substring(0, dashIndex).trim();
        }
        return category;
      }
      return 'ఇతరం';
    }

    // Helper to extract content from news item
    function extractContent(point) {
      const colonIndex = point.indexOf(':');
      if (colonIndex > 0 && colonIndex < 30) {
        return point.substring(colonIndex + 1).trim();
      }
      return point;
    }

    // Group news items by category
    function groupByCategory(newsItems) {
      const grouped = {};
      
      (newsItems || []).forEach(item => {
        const category = extractCategory(item);
        if (!grouped[category]) {
          grouped[category] = [];
        }
        grouped[category].push(extractContent(item));
      });

      // Sort categories by predefined order
      const sortedCategories = Object.keys(grouped).sort((a, b) => {
        const indexA = categoryOrder.indexOf(a);
        const indexB = categoryOrder.indexOf(b);
        // If category not in order list, put it at the end
        const orderA = indexA === -1 ? 999 : indexA;
        const orderB = indexB === -1 ? 999 : indexB;
        return orderA - orderB;
      });

      return { grouped, sortedCategories };
    }

    // Render grouped news
    function renderGroupedNews(newsItems, slotClass) {
      const { grouped, sortedCategories } = groupByCategory(newsItems);
      
      if (sortedCategories.length === 0) {
        return '<p class="no-news-items">వార్తలు లేవు</p>';
      }

      return sortedCategories.map(category => {
        const items = grouped[category];
        const categoryClass = getCategoryClass(category);
        return `
          <div class="category-group ${categoryClass}">
            <h4 class="category-header ${categoryClass}">${escapeHtml(category)}</h4>
            <ul class="category-news-list">
              ${items.map(content => `<li class="news-item">${escapeHtml(content)}</li>`).join('')}
            </ul>
          </div>
        `;
      }).join('');
    }

    // Get CSS class for category
    function getCategoryClass(category) {
      const categoryMap = {
        'రాజకీయాలు': 'cat-politics',
        'వ్యాపారం': 'cat-business',
        'నేరం': 'cat-crime',
        'క్రీడలు': 'cat-sports',
        'వినోదం': 'cat-entertainment',
        'సినిమా': 'cat-entertainment',
        'ఆరోగ్యం': 'cat-health',
        'వ్యవసాయం': 'cat-agriculture',
        'టెక్నాలజీ': 'cat-technology',
        'అంతర్జాతీయం': 'cat-international',
        'విద్య': 'cat-education',
        'వాతావరణం': 'cat-weather',
        'ఇతరం': 'cat-other'
      };
      return categoryMap[category] || 'cat-other';
    }

    // Build slot sections
    let slotsHtml = '';
    
    // Evening news (9 PM) section
    if (dateData.slots['9pm']) {
      const evening = dateData.slots['9pm'];
      slotsHtml += `
        <div class="slot-section evening-section">
          <div class="slot-header">
            <span class="slot-badge slot-9pm">🌙 సాయంత్రం వార్తలు (9 PM)</span>
          </div>
          <div class="categorized-news">
            ${renderGroupedNews(evening.summary, 'evening')}
          </div>
        </div>
      `;
    }

    // Morning news (7 AM) section
    if (dateData.slots['7am']) {
      const morning = dateData.slots['7am'];
      slotsHtml += `
        <div class="slot-section morning-section">
          <div class="slot-header">
            <span class="slot-badge slot-7am">☀️ ఉదయం వార్తలు (7 AM)</span>
          </div>
          <div class="categorized-news">
            ${renderGroupedNews(morning.summary, 'morning')}
          </div>
        </div>
      `;
    }

    // If no slots available
    if (!slotsHtml) {
      slotsHtml = '<p class="no-slots">ఈ తేదీకి వార్తలు అందుబాటులో లేవు</p>';
    }

    card.innerHTML = `
      <div class="date-header">
        <span class="date-icon">📰</span>
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
    const isPrevDisabled = currentIdx <= 0;
    const isNextDisabled = currentIdx >= totalDates - 1;
    
    if (elements.prevBtn) {
      elements.prevBtn.disabled = isPrevDisabled;
    }
    if (elements.nextBtn) {
      elements.nextBtn.disabled = isNextDisabled;
    }
    
    // Update mobile navigation buttons
    if (elements.mobilePrevBtn) {
      elements.mobilePrevBtn.disabled = isPrevDisabled;
    }
    if (elements.mobileNextBtn) {
      elements.mobileNextBtn.disabled = isNextDisabled;
    }
    
    // Update load more button
    updateLoadMoreButton();
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
    navigateDates,
    toggleTheme,
    setViewMode,
    setSidebarView,
    loadMoreDates
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
