/**
 * Review Carousel
 * Handles the testimonials carousel navigation
 */

(function() {
  'use strict';

  function initReviewCarousel() {
    const carousel = document.querySelector('.review-carousel-wrapper');
    if (!carousel) return;

    const track = carousel.querySelector('.review-cards-track');
    const cards = track.querySelectorAll('.review-card');
    const prevBtns = carousel.closest('.section-testimonials').querySelectorAll('.review-nav.prev');
    const nextBtns = carousel.closest('.section-testimonials').querySelectorAll('.review-nav.next');
    const currentPageEls = carousel.closest('.section-testimonials').querySelectorAll('.current-page');
    const totalPagesEls = carousel.closest('.section-testimonials').querySelectorAll('.total-pages');

    if (cards.length === 0) return;

    let currentIndex = 0;
    let cardsPerView = 1;
    let totalPages = cards.length;
    let cachedCardWidth = 0;
    let cachedGap = 24;

    function getCardsPerView() {
      if (window.matchMedia('(max-width: 768px)').matches) return 1;
      if (window.matchMedia('(max-width: 1024px)').matches) return 2;
      return 3;
    }

    function cacheCardDimensions() {
      // Cache dimensions once to avoid forced reflows
      requestAnimationFrame(function() {
        const card = cards[0];
        cachedCardWidth = card.offsetWidth;
        const style = getComputedStyle(card);
        cachedGap = parseFloat(style.marginRight) || 24;
      });
    }

    function updatePagination() {
      const currentPage = Math.floor(currentIndex / cardsPerView) + 1;
      currentPageEls.forEach(function(el) { el.textContent = currentPage; });
      totalPagesEls.forEach(function(el) { el.textContent = totalPages; });
    }

    function updateButtons() {
      const atStart = currentIndex === 0;
      const atEnd = currentIndex >= cards.length - cardsPerView;

      prevBtns.forEach(function(btn) { btn.disabled = atStart; });
      nextBtns.forEach(function(btn) { btn.disabled = atEnd; });
    }

    function slideToIndex(index) {
      const maxIndex = cards.length - cardsPerView;
      currentIndex = Math.max(0, Math.min(index, maxIndex));

      const viewport = carousel.querySelector('.review-cards-viewport');
      const isMobile = window.matchMedia('(max-width: 768px)').matches;

      if (isMobile && viewport) {
        // On mobile, use native scroll for proper scroll-snap
        track.style.transform = 'none';
        const scrollPos = currentIndex * viewport.offsetWidth;
        viewport.scrollTo({ left: scrollPos, behavior: 'smooth' });
      } else {
        // On desktop, use transform
        const offset = currentIndex * (cachedCardWidth + cachedGap);
        track.style.transform = 'translateX(-' + offset + 'px)';
      }

      updatePagination();
      updateButtons();
    }

    function goToPrev() {
      slideToIndex(currentIndex - cardsPerView);
    }

    function goToNext() {
      slideToIndex(currentIndex + cardsPerView);
    }

    // Event listeners
    prevBtns.forEach(function(btn) { btn.addEventListener('click', goToPrev); });
    nextBtns.forEach(function(btn) { btn.addEventListener('click', goToNext); });

    // Track manual scroll on mobile to update pagination
    const viewport = carousel.querySelector('.review-cards-viewport');
    let scrollTimer;
    viewport.addEventListener('scroll', function() {
      if (!window.matchMedia('(max-width: 768px)').matches) return;
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(function() {
        const scrollPos = viewport.scrollLeft;
        const cardWidth = viewport.offsetWidth;
        currentIndex = Math.round(scrollPos / cardWidth);
        updatePagination();
        updateButtons();
      }, 100);
    });

    // Handle resize
    let resizeTimer;
    window.addEventListener('resize', function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function() {
        const newCardsPerView = getCardsPerView();
        if (newCardsPerView !== cardsPerView) {
          cardsPerView = newCardsPerView;
          totalPages = Math.ceil(cards.length / cardsPerView);
          cacheCardDimensions();
          slideToIndex(0);
        }
      }, 250);
    });

    // Initialize
    cardsPerView = getCardsPerView();
    totalPages = Math.ceil(cards.length / cardsPerView);
    cacheCardDimensions();

    // Delay initial slide to allow dimensions to be cached
    requestAnimationFrame(function() {
      slideToIndex(0);
    });

    // Handle "Read more" expand buttons
    const expandBtns = carousel.querySelectorAll('.review-expand');
    expandBtns.forEach(function(btn) {
      btn.addEventListener('click', function() {
        const wrapper = btn.closest('.review-quote-wrapper');
        const card = btn.closest('.review-card');
        if (wrapper) {
          wrapper.classList.remove('truncated');
          wrapper.classList.add('expanded');
        }
        if (card) {
          card.classList.add('expanded');
        }
      });
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReviewCarousel);
  } else {
    initReviewCarousel();
  }
})();
