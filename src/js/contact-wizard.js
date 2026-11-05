/**
 * Contact wizard — one-question-at-a-time enhancement over the plain Netlify form.
 * Spec: fsf-workspace/website/references/2026-07-06-contact-form-rework-design.md
 * 3-step rework: website/working/handoffs/handoff-webdev-contact-form-3-step-2026-11-05.txt
 * Requires estimate-logic.js (window.FSF_ESTIMATE) loaded first.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'fsf-contact-wizard-v2'; // v1 = the 7-step form; its saved state must not restore here
  var WEDDING = 'Wedding / private party';
  var REELS = 'Reels for social media';
  var SOMETHING_ELSE = 'Something else';

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
    var stepByName = {};
    steps.forEach(function (s) { stepByName[s.dataset.step] = s; });
    if (!stepByName.need || !stepByName['event-details'] || !stepByName['project-details'] || !stepByName.contact) return;

    var wrapper = form.closest('.contact-form-wrapper');
    var current = 0; // index into path()
    var submitAttempts = 0;
    var completed = false;

    // Branch-only questions are required only while their branch is live; the plain
    // no-JS form leaves them optional so a non-event visitor can still send it.
    Array.prototype.forEach.call(form.querySelectorAll('[data-required]'), function (el) {
      el.required = true;
    });

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
    var projectDate = form.querySelector('#project_date');
    if (dateInput) dateInput.min = localToday();
    if (projectDate) projectDate.min = localToday();
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

    // --- branching on service ---
    function service() {
      var el = form.querySelector('input[name="service"]:checked');
      return el ? el.value : '';
    }
    function isEventPath() { return service() === logic.EVENT_SERVICE; }

    function path() {
      return [stepByName.need,
        isEventPath() ? stepByName['event-details'] : stepByName['project-details'],
        stepByName.contact];
    }

    function setEnabled(container, on) {
      Array.prototype.forEach.call(container.querySelectorAll('input, select, textarea'), function (el) {
        el.disabled = !on;
      });
    }

    // Hidden-branch inputs are disabled so they skip validation and stay out of the submission.
    var coverageWrap = form.querySelector('#q-project-coverage-wrap');
    var frequencyWrap = form.querySelector('#q-frequency-wrap');
    function syncBranch() {
      var svc = service();
      var ev = isEventPath();
      setEnabled(stepByName['event-details'], ev);
      setEnabled(stepByName['project-details'], !ev);
      if (ev && noDate && dateInput) dateInput.disabled = noDate.checked;
      var showCoverage = !ev && (svc === REELS || svc === SOMETHING_ELSE);
      var showFrequency = !ev && svc === REELS;
      coverageWrap.hidden = !showCoverage;
      setEnabled(coverageWrap, showCoverage);
      frequencyWrap.hidden = !showFrequency;
      setEnabled(frequencyWrap, showFrequency);
      submitLabel = (ev || svc === 'Product photos') ? 'Get my estimate' : 'Send';
      if (!submitBtn.disabled) submitBtn.textContent = submitLabel;
    }
    var submitLabel = 'Get my estimate';
    Array.prototype.forEach.call(form.querySelectorAll('input[name="service"]'), function (r) {
      r.addEventListener('change', syncBranch);
    });

    // --- persistence ---
    function saveState() {
      if (completed) return; // never resurrect state cleared on success
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
      syncBranch();
      syncReferralDetail();
      if (!service()) return 0;
      return Math.min(Math.max(state.step, 0), 2);
    }

    function clearState() {
      try { sessionStorage.removeItem(STORAGE_KEY); } catch (e) { /* ignore */ }
    }

    // --- step engine ---
    function fieldError(el) {
      if (el.type === 'radio') {
        var q = el.closest('.wizard-question');
        var label = q && q.querySelector('.wizard-question-label');
        return label ? 'Pick an answer for “' + label.textContent + '”' : 'Pick one to continue.';
      }
      if (el.type === 'date') return 'That date looks off — it should be today or later.';
      if (el.type === 'time') return 'That time looks unfinished — complete it or clear it.';
      return 'Please fill this in to continue.';
    }

    function stepValid(i) {
      var fields = path()[i].querySelectorAll('input, select, textarea');
      for (var f = 0; f < fields.length; f++) {
        if (!fields[f].disabled && !fields[f].checkValidity()) return fieldError(fields[f]);
      }
      return '';
    }

    function showStep(i, opts) {
      opts = opts || {};
      var p = path();
      current = i;
      steps.forEach(function (s) { s.classList.toggle('is-current', s === p[i]); });
      form.classList.toggle('on-last-step', i === p.length - 1);
      nextBtn.hidden = (i === p.length - 1);
      backBtn.hidden = (i === 0);
      progressText.textContent = 'Step ' + (i + 1) + ' of ' + p.length;
      progressFill.style.width = (((i + 1) / p.length) * 100) + '%';
      stepError.classList.remove('is-visible');
      if (!opts.fromHistory) {
        try { history.pushState({ wizardStep: i }, ''); } catch (e) { /* ignore */ }
      }
      if (!opts.noFocus) p[i].querySelector('legend').focus();
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
      if (path()[current] === stepByName['event-details'] && et && et.value === WEDDING) {
        showWeddingExit();
        return;
      }
      track('wizard-step-' + (current + 1), current === 0 ? { service: service() } : undefined);
      showStep(current + 1);
    }

    backBtn.addEventListener('click', function () {
      if (current > 0) {
        if (history.state && typeof history.state.wizardStep === 'number') {
          history.back(); // popstate drives showStep — same path as browser Back
        } else {
          showStep(current - 1);
        }
      }
    });
    nextBtn.addEventListener('click', advance);

    // Auto-advance on chip click, only on step 1 (a single question). Label taps and
    // Space both fire click (a deliberate confirm); arrow-key browsing fires change
    // but NOT click, so it never advances mid-selection.
    Array.prototype.forEach.call(stepByName.need.querySelectorAll('input[type="radio"]'), function (r) {
      r.addEventListener('click', function () {
        saveState();
        setTimeout(function () {
          if (path()[current] === stepByName.need) advance();
        }, 200);
      });
    });
    form.addEventListener('input', saveState);
    form.addEventListener('change', saveState); // radios/selects where 'input' doesn't fire
    form.addEventListener('change', function () { stepError.classList.remove('is-visible'); });

    window.addEventListener('popstate', function (e) {
      if (completed) return;
      if (e.state && typeof e.state.wizardStep === 'number') {
        showStep(e.state.wizardStep, { fromHistory: true, noFocus: true });
      }
    });

    // Enter key advances instead of submitting mid-wizard
    form.addEventListener('keydown', function (e) {
      if (e.target.tagName === 'BUTTON') return; // Enter on Back must not advance
      if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && current < path().length - 1) {
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
        '<p>First Sight Films covers business and organizational events, product photos and marketing video, so we&rsquo;re not the right fit for weddings or private parties.</p>' +
        // REFERRAL BLOCK — swap this one paragraph when Diego names 1–2 local wedding filmmakers.
        '<p>Northeast Florida has wonderful wedding filmmakers and photographers &mdash; WeddingWire and The Knot are great places to find them.</p>' +
        '<p>Planning a corporate or organizational gathering instead? <button type="button" class="btn btn-primary wizard-exit-back">Go back and tell us about your project</button></p>';
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

    // --- submit & result screen ---
    function collectAnswers() {
      var get = function (name) {
        var el = form.querySelector('input[name="' + name + '"]:checked');
        return el ? el.value : '';
      };
      var budget = form.querySelector('#budget_range');
      return {
        coverage: get('coverage_type'),
        length: get('event_length'),
        budgetRange: budget ? budget.value : '',
        eventDate: (dateInput && !dateInput.disabled) ? dateInput.value : '',
        today: localToday()
      };
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      // novalidate is on, so validate every step ourselves (not just the last)
      syncBranch();
      for (var i = 0; i < path().length; i++) {
        var err = stepValid(i);
        if (err) {
          showStep(i);
          stepError.textContent = err;
          stepError.classList.add('is-visible');
          return;
        }
      }
      track('wizard-step-' + path().length);
      var result = logic.getResult(service(), collectAnswers());
      form.querySelector('#estimate_shown').value = result.headline;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending…';

      var body = new URLSearchParams(new FormData(form)).toString();
      fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body
      }).then(function (res) {
        if (!res.ok) {
          var httpErr = new Error('HTTP ' + res.status);
          httpErr.status = res.status;
          throw httpErr;
        }
        clearState();
        completed = true;
        track('contact-form-submit');
        if (typeof window.gtag === 'function') { // gtag is skipped for bots (head.html)
          try { window.gtag('event', 'generate_lead', { form_name: 'contact', estimate_tier: result.tier }); } catch (e) { /* analytics must never break the form */ }
        }
        track('estimate-shown', { tier: result.tier });
        renderResult(result);
      }).catch(function (err) {
        submitAttempts += 1;
        track('contact-form-error', { status: (err && err.status) ? String(err.status) : 'network' });
        submitBtn.disabled = false;
        submitBtn.textContent = submitLabel;
        if (submitAttempts >= 2) {
          // Last resort: native POST (Netlify's generic success page). No lead lost.
          // Umami sends with keepalive, so this event survives the navigation.
          track('contact-form-fallback');
          form.submit();
          return;
        }
        submitError.classList.add('is-visible');
      });
    });

    submitError.querySelector('.wizard-retry').addEventListener('click', function () {
      submitError.classList.remove('is-visible');
      if (form.requestSubmit) form.requestSubmit(); else form.submit();
    });

    // --- result screen (spec §5; per-service variants per the 3-step handoff §5) ---
    function renderResult(result) {
      var screen = document.createElement('div');
      screen.className = 'estimate-screen';
      var html;
      if (result.isEvent) {
        html =
          '<h3 tabindex="-1">Here&rsquo;s your estimate</h3>' +
          '<p class="estimate-headline">' + result.headline + '</p>' +
          '<p class="estimate-note">That&rsquo;s an estimate, not a quote &mdash; the exact number depends on days on site, deliverables, and timing. You&rsquo;ll get a firm number on a quick call, and we&rsquo;ll follow up by email within a business day.</p>';
        if (result.rushLine) html += '<div class="estimate-extra">' + result.rushLine + '</div>';
        if (result.underBudgetLine) html += '<div class="estimate-extra">' + result.underBudgetLine + '</div>';
        html +=
          '<p><strong>Every package:</strong> photos and a short social recap within 72 hours of your event.</p>' +
          '<p><strong>Want the exact number sooner? Grab a time below &mdash; 15 minutes, same-day quote.</strong></p>';
      } else if (result.priced) {
        html =
          '<h3 tabindex="-1">Here&rsquo;s your estimate</h3>' +
          '<p class="estimate-headline">' + result.headline + '</p>' +
          '<p class="estimate-note">That&rsquo;s a starting price, not a quote. You&rsquo;ll get a firm number on a quick call, and we&rsquo;ll follow up by email within a business day.</p>' +
          '<p><strong>Want the exact number sooner? Grab a time below &mdash; 15 minutes, same-day quote.</strong></p>';
      } else {
        html =
          '<h3 tabindex="-1">Message sent</h3>' +
          '<p class="estimate-headline">' + result.headline + '</p>' +
          '<p class="estimate-note">We&rsquo;ll follow up by email within a business day with options.</p>' +
          '<p><strong>Rather talk it through? Grab a time below &mdash; 15 minutes.</strong></p>';
      }
      screen.innerHTML = html;

      // Move the existing booking card into the result screen (single calendar embed on the page).
      var bookingCard = document.querySelector('.booking-card');
      var anchor = document.getElementById('book-a-call');
      form.hidden = true;
      wrapper.appendChild(screen);
      if (bookingCard) screen.appendChild(bookingCard);
      if (anchor) anchor.hidden = true;
      screen.querySelector('h3').focus({ preventScroll: true });
      var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      screen.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    }

    // --- activate ---
    form.noValidate = true; // stepValid() validates per step; native check would block on hidden steps
    form.classList.add('wizard-active');
    syncReferralDetail();
    syncBranch();
    var startAt = restoreState();
    try { history.replaceState({ wizardStep: startAt }, ''); } catch (e) { /* ignore */ }
    showStep(startAt, { fromHistory: true, noFocus: true });
  }
})();
