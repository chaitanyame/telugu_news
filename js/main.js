/**
 * Telugu News Aggregator - Main JavaScript
 * Handles UI interactions and data loading
 */

// Initialize page on load
document.addEventListener('DOMContentLoaded', () => {
  // Set current year in footer
  const currentYear = new Date().getFullYear();
  const yearElement = document.getElementById('current-year');
  if (yearElement) {
    yearElement.textContent = currentYear;
  }
  
  // Set last updated timestamp (placeholder for now)
  const lastUpdatedElement = document.getElementById('last-updated');
  if (lastUpdatedElement) {
    lastUpdatedElement.textContent = new Date().toLocaleDateString('te-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    lastUpdatedElement.setAttribute('datetime', new Date().toISOString());
  }
});
