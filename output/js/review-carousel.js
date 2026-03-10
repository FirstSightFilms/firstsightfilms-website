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
    let cardsPerView = getCardsPerView();
    let totalPages = Math.ceil(cards.length / cardsPerView);

    function getCardsPerView() {
      const width = window.innerWidth;
      if (width <= 768) return 1;
      if (width <= 1024) return 2;
      return 3;
    }

    function updatePagination() {
      const currentPage = Math.floor(currentIndex / cardsPerView) + 1;
      currentPageEls.forEach(el => el.textContent = currentPage);
      totalPagesEls.forEach(el => el.textContent = totalPages);
    }

    function updateButtons() {
      const atStart = currentIndex === 0;
      const atEnd = currentIndex >= cards.length - cardsPerView;

      prevBtns.forEach(btn => btn.disabled = atStart);
      nextBtns.forEach(btn => btn.disabled = atEnd);
    }

    function slideToIndex(index) {
      const maxIndex = cards.length - cardsPerView;
      currentIndex = Math.max(0, Math.min(index, maxIndex));

      const card = cards[0];
      const cardStyle = getComputedStyle(card);
      const cardWidth = card.offsetWidth;
      const gap = parseFloat(cardStyle.marginRight) || 24; // 1.5rem default

      const offset = currentIndex * (cardWidth + gap);
      track.style.transform = `translateX(-${offset}px)`;

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
    prevBtns.forEach(btn => btn.addEventListener('click', goToPrev));
    nextBtns.forEach(btn => btn.addEventListener('click', goToNext));

    // Handle resize
    let resizeTimer;
    window.addEventListener('resize', function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function() {
        const newCardsPerView = getCardsPerView();
        if (newCardsPerView !== cardsPerView) {
          cardsPerView = newCardsPerView;
          totalPages = Math.ceil(cards.length / cardsPerView);
          slideToIndex(0);
        }
      }, 250);
    });

    // Initialize
    slideToIndex(0);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReviewCarousel);
  } else {
    initReviewCarousel();
  }
})();
