/* ==========================================================================
   work-feed.js — "Recent Shoots" dated feed for recurring /work/ pillars
   (Architecture doc §3b). Loaded only on pillar pages that include the feed.

   Two behaviors:
   1) Load more — cards beyond LIMIT collapse (display:none, but stay in the DOM
      so they remain indexable); a "Load more" button reveals the rest.
   2) Lightbox — thumbnails open a shared modal for photo OR video. Full-res is
      never loaded inline; it loads only when a thumb is opened.

   Markup hooks:
     #shoot-feed            wraps the .shoot-card articles (newest first)
     #shoot-load-more       the reveal button (starts hidden)
     [data-lightbox-video]  element carrying a video src -> opens video
     [data-lightbox-img]    element carrying a full-res image src -> opens image
     #work-modal            the shared modal container (see template markup)
   ========================================================================== */
(function () {
  var LIMIT = 12; // collapse cards after this many (§3b: ~10–12)

  // ---- 1. Load more --------------------------------------------------------
  var feed = document.getElementById('shoot-feed');
  var moreBtn = document.getElementById('shoot-load-more');
  if (feed && moreBtn) {
    var cards = Array.prototype.slice.call(feed.querySelectorAll('.shoot-card'));
    if (cards.length > LIMIT) {
      cards.slice(LIMIT).forEach(function (c) { c.classList.add('is-collapsed'); });
      moreBtn.hidden = false;
      moreBtn.addEventListener('click', function () {
        cards.forEach(function (c) { c.classList.remove('is-collapsed'); });
        moreBtn.hidden = true;
      });
    }
  }

  // ---- 2. Lightbox (photo + video) ----------------------------------------
  var modal = document.getElementById('work-modal');
  if (!modal) return;
  var video = document.getElementById('work-modal-video');
  var image = document.getElementById('work-modal-image');

  function openModal() {
    modal.dataset.open = 'true';
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }
  function openVideo(src) {
    if (!src || !video) return;
    if (image) { image.hidden = true; image.removeAttribute('src'); }
    video.hidden = false;
    video.src = src;
    openModal();
    video.play().catch(function () {});
  }
  function openImage(src, alt) {
    if (!src || !image) return;
    if (video) { video.pause(); video.removeAttribute('src'); video.hidden = true; }
    image.hidden = false;
    image.src = src;
    image.alt = alt || '';
    openModal();
  }
  function closeModal() {
    if (video && !video.hidden) { video.pause(); video.removeAttribute('src'); video.load(); }
    if (image) { image.removeAttribute('src'); }
    delete modal.dataset.open;
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  document.addEventListener('click', function (e) {
    var v = e.target.closest('[data-lightbox-video]');
    if (v) { e.preventDefault(); openVideo(v.getAttribute('data-lightbox-video')); return; }
    var im = e.target.closest('[data-lightbox-img]');
    if (im) {
      e.preventDefault();
      var thumb = im.querySelector('img');
      openImage(im.getAttribute('data-lightbox-img'), thumb ? thumb.alt : '');
    }
  });
  modal.addEventListener('click', function (e) {
    if (e.target.matches('[data-close-modal]')) closeModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal.dataset.open === 'true') closeModal();
  });
})();
