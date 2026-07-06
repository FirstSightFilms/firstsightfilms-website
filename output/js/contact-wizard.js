/**
 * Contact wizard — one-question-at-a-time enhancement over the plain Netlify form.
 * Spec: fsf-workspace/website/references/2026-07-06-contact-form-rework-design.md
 * Requires estimate-logic.js (window.FSF_ESTIMATE) loaded first.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'fsf-contact-wizard';
  var WEDDING = 'Wedding / private party';

  document.addEventListener('DOMContentLoaded', init);

  function track(name, data) {
    if (window.umami && typeof window.umami.track === 'function') {
      try { window.umami.track(name, data); } catch (e) { /* analytics must never break the form */ }
    }
  }

  function localToday() {
    var d = new Date();
    return d.getFullYear() + '-' +
      String(d.getMonth() + 1).padStart(2, '0') + '-' +
      String(d.getDate()).padStart(2, '0');
  }

  function init() {
    var form = document.querySelector('form[name="contact"]');
    var logic = window.FSF_ESTIMATE;
    if (!form || !logic || !window.fetch || !window.sessionStorage) return; // stay a plain form
    var steps = Array.prototype.slice.call(form.querySelectorAll('.wizard-step'));
    if (steps.length < 2) return;

    var wrapper = form.closest('.contact-form-wrapper');
    var current = 0;
    var submitAttempts = 0;

    // --- injected UI ---
    var progress = document.createElement('div');
    progress.className = 'wizard-progress';
    progress.innerHTML =
      '<span class="wizard-progress-text" aria-live="polite"></span>' +
      '<div class="wizard-progress-track"><div class="wizard-progress-fill"></div></div>';
    form.insertBefore(progress, steps[0]);

    var nav = document.createElement('div');
    nav.className = 'wizard-nav';
    nav.innerHTML =
      '<button type="button" class="wizard-back" hidden>&larr; Back</button>' +
      '<button type="button" class="btn btn-primary wizard-next">Next &rarr;</button>';
    form.appendChild(nav);

    var stepError = document.createElement('p');
    stepError.className = 'wizard-error';
    stepError.setAttribute('aria-live', 'polite');
    form.insertBefore(stepError, nav);

    var submitError = document.createElement('div');
    submitError.className = 'wizard-submit-error';
    submitError.innerHTML =
      '<p>Something went wrong sending your answers. ' +
      '<button type="button" class="btn btn-primary wizard-retry">Try again</button></p>';
    form.appendChild(submitError);

    var backBtn = nav.querySelector('.wizard-back');
    var nextBtn = nav.querySelector('.wizard-next');
    var progressText = progress.querySelector('.wizard-progress-text');
    var progressFill = progress.querySelector('.wizard-progress-fill');
    var submitBtn = form.querySelector('button[type="submit"]');

    // --- date field constraints ---
    var dateInput = form.querySelector('#event_date');
    var noDate = form.querySelector('#no_date_yet');
    if (dateInput) dateInput.min = localToday();
    if (noDate && dateInput) {
      noDate.addEventListener('change', function () {
        dateInput.disabled = noDate.checked;
        if (noDate.checked) dateInput.value = '';
      });
      dateInput.addEventListener('input', function () {
        if (dateInput.value) noDate.checked = false;
      });
    }

    // --- referral detail show/hide (replaces the old inline script) ---
    var refSel = form.querySelector('#referral_source');
    var refWrap = form.querySelector('#referral_detail_wrap');
    function syncReferralDetail() {
      if (!refSel || !refWrap) return;
      var v = refSel.value;
      refWrap.style.display =
        (v === 'Referral (a person or company)' || v === 'Other') ? 'block' : 'none';
    }
    if (refSel) refSel.addEventListener('change', syncReferralDetail);

    // --- persistence ---
    function saveState() {
      var values = {};
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.name === 'bot-field' || el.name === 'form-name') return;
        if (el.type === 'radio' || el.type === 'checkbox') {
          if (el.checked) values[el.name] = el.value;
        } else {
          values[el.name] = el.value;
        }
      });
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ step: current, values: values }));
      } catch (e) { /* private mode etc. — persistence is best-effort */ }
    }

    function restoreState() {
      var raw = null;
      try { raw = sessionStorage.getItem(STORAGE_KEY); } catch (e) { return 0; }
      if (!raw) return 0;
      var state;
      try { state = JSON.parse(raw); } catch (e) { return 0; }
      if (!state || typeof state.step !== 'number' || !state.values) return 0;
      Object.keys(state.values).forEach(function (name) {
        var v = state.values[name];
        var els = form.querySelectorAll('[name="' + name + '"]');
        Array.prototype.forEach.call(els, function (el) {
          if (el.type === 'radio' || el.type === 'checkbox') el.checked = (el.value === v);
          else el.value = v;
        });
      });
      if (noDate && dateInput) dateInput.disabled = noDate.checked;
      syncReferralDetail();
      return Math.min(Math.max(state.step, 0), steps.length - 1);
    }

    function clearState() {
      try { sessionStorage.removeItem(STORAGE_KEY); } catch (e) { /* ignore */ }
    }

    // --- step engine ---
    function stepValid(i) {
      var step = steps[i];
      if (step.dataset.step === 'when-where') {
        var hasWhen = (dateInput && dateInput.value) || (noDate && noDate.checked);
        var loc = form.querySelector('#event_location');
        if (!hasWhen) return 'Pick a date — or tap “No date yet.”';
        if (!loc.value.trim()) return 'Tell us the city or venue.';
        if (dateInput && dateInput.value && !dateInput.checkValidity()) return 'That date looks off — it should be today or later.';
        return '';
      }
      var fields = step.querySelectorAll('input, select, textarea');
      for (var f = 0; f < fields.length; f++) {
        if (!fields[f].disabled && !fields[f].checkValidity()) {
          return (fields[f].type === 'radio') ? 'Pick one to continue.' : 'Please fill this in to continue.';
        }
      }
      return '';
    }

    function showStep(i, opts) {
      opts = opts || {};
      current = i;
      steps.forEach(function (s, idx) { s.classList.toggle('is-current', idx === i); });
      form.classList.toggle('on-last-step', i === steps.length - 1);
      nextBtn.hidden = (i === steps.length - 1);
      backBtn.hidden = (i === 0);
      progressText.textContent = 'Step ' + (i + 1) + ' of ' + steps.length;
      progressFill.style.width = (((i + 1) / steps.length) * 100) + '%';
      stepError.classList.remove('is-visible');
      if (!opts.fromHistory) {
        try { history.pushState({ wizardStep: i }, ''); } catch (e) { /* ignore */ }
      }
      if (!opts.noFocus) steps[i].querySelector('legend').focus();
      saveState();
    }

    function advance() {
      var err = stepValid(current);
      if (err) {
        stepError.textContent = err;
        stepError.classList.add('is-visible');
        return;
      }
      // Wedding branch: exits instead of advancing (spec §4)
      var et = form.querySelector('input[name="event_type"]:checked');
      if (current === 0 && et && et.value === WEDDING) {
        showWeddingExit();
        return;
      }
      track('wizard-step-' + (current + 1));
      showStep(current + 1);
    }

    backBtn.addEventListener('click', function () { if (current > 0) showStep(current - 1); });
    nextBtn.addEventListener('click', advance);

    // Auto-advance on chip (radio) selection for radio-only steps
    steps.forEach(function (step) {
      var radios = step.querySelectorAll('input[type="radio"]');
      Array.prototype.forEach.call(radios, function (r) {
        r.addEventListener('change', function () {
          saveState();
          setTimeout(function () {
            if (steps[current] === step) advance();
          }, 200);
        });
      });
    });
    form.addEventListener('input', saveState);

    window.addEventListener('popstate', function (e) {
      if (e.state && typeof e.state.wizardStep === 'number') {
        showStep(e.state.wizardStep, { fromHistory: true, noFocus: true });
      }
    });

    // Enter key advances instead of submitting mid-wizard
    form.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && current < steps.length - 1) {
        e.preventDefault();
        advance();
      }
    });

    // --- wedding exit (spec §4: generic wording; named referrals drop into the marked block) ---
    function showWeddingExit() {
      track('wizard-exit-wedding');
      var exit = document.createElement('div');
      exit.className = 'wizard-exit';
      exit.innerHTML =
        '<h3>We&rsquo;re probably not your crew &mdash; and that&rsquo;s okay.</h3>' +
        '<p>First Sight Films covers festivals, conferences, and organizational events, so we&rsquo;re not the right fit for weddings or private parties.</p>' +
        // REFERRAL BLOCK — swap this one paragraph when Diego names 1–2 local wedding filmmakers.
        '<p>Northeast Florida has wonderful wedding filmmakers and photographers &mdash; WeddingWire and The Knot are great places to find them.</p>' +
        '<p>Planning a corporate or organizational gathering instead? <button type="button" class="btn btn-primary wizard-exit-back">Go back and tell us about it</button></p>';
      form.hidden = true;
      wrapper.appendChild(exit);
      exit.querySelector('.wizard-exit-back').addEventListener('click', function () {
        var checked = form.querySelector('input[name="event_type"]:checked');
        if (checked) checked.checked = false;
        exit.remove();
        form.hidden = false;
        showStep(0);
      });
    }

    // --- submit & estimate screen ---
    function collectAnswers() {
      var get = function (name) {
        var el = form.querySelector('input[name="' + name + '"]:checked');
        return el ? el.value : '';
      };
      return {
        coverage: get('coverage_type'),
        length: get('event_length'),
        budgetRange: get('budget_range'),
        eventDate: (dateInput && !dateInput.disabled) ? dateInput.value : '',
        today: localToday()
      };
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var err = stepValid(current);
      if (err) {
        stepError.textContent = err;
        stepError.classList.add('is-visible');
        return;
      }
      var estimate = logic.getEstimate(collectAnswers());
      form.querySelector('#estimate_shown').value = estimate.headline;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending…';

      var body = new URLSearchParams(new FormData(form)).toString();
      fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body
      }).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        clearState();
        track('contact-form-submit');
        track('estimate-shown', { tier: estimate.tier });
        renderEstimate(estimate);
      }).catch(function () {
        submitAttempts += 1;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Get my estimate';
        if (submitAttempts >= 2) {
          // Last resort: native POST (Netlify's generic success page). No lead lost.
          form.submit();
          return;
        }
        submitError.classList.add('is-visible');
      });
    });

    submitError.querySelector('.wizard-retry').addEventListener('click', function () {
      submitError.classList.remove('is-visible');
      form.requestSubmit();
    });

    // --- estimate screen (spec §5) ---
    function renderEstimate(estimate) {
      var screen = document.createElement('div');
      screen.className = 'estimate-screen';
      var html =
        '<h3 tabindex="-1">Here&rsquo;s your estimate</h3>' +
        '<p class="estimate-headline">' + estimate.headline + '</p>' +
        '<p class="estimate-note">That&rsquo;s an estimate, not a quote &mdash; the exact number depends on days on site, deliverables, and timing. You&rsquo;ll get a firm number on a quick call, and we&rsquo;ll follow up by email within a business day.</p>';
      if (estimate.rushLine) html += '<div class="estimate-extra">' + estimate.rushLine + '</div>';
      if (estimate.underBudgetLine) html += '<div class="estimate-extra">' + estimate.underBudgetLine + '</div>';
      html +=
        '<p><strong>Every package:</strong> photos and a short social recap within 72 hours of your event.</p>' +
        '<p><strong>Want the exact number sooner? Grab a time below &mdash; 15 minutes, same-day quote.</strong></p>';
      screen.innerHTML = html;

      // Move the existing booking card into the result screen (single calendar embed on the page).
      var bookingCard = document.querySelector('.booking-card');
      var anchor = document.getElementById('book-a-call');
      form.hidden = true;
      wrapper.appendChild(screen);
      if (bookingCard) screen.appendChild(bookingCard);
      if (anchor) anchor.hidden = true;
      screen.querySelector('h3').focus();
      screen.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // --- activate ---
    form.classList.add('wizard-active');
    syncReferralDetail();
    var startAt = restoreState();
    try { history.replaceState({ wizardStep: startAt }, ''); } catch (e) { /* ignore */ }
    showStep(startAt, { fromHistory: true, noFocus: true });
  }
})();
