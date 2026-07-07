/**
 * Estimate mapping for the contact wizard.
 * Every price cites fsf-workspace/shared/strategy/pricing-ladder.md (canonical).
 * Do not add or change a number here without changing the ladder first.
 * Browser: window.FSF_ESTIMATE. Node (tests): module.exports.
 */
(function (root) {
  'use strict';

  // Keys must match budget_range values byte-for-byte (en dash) — and ALL coverage/length literals in tierFor below must byte-match the form's radio values (en dash in '2–3 days', em dash in 'Not sure — help me decide').
  // 'Under $X' is exclusive (their budget is strictly below X); '$A–B' is inclusive at B.
  var BRACKET_CEILINGS = {
    'Under $2,500': 2499,
    '$2,500–5,500': 5500,
    '$5,500–9,500': 9500,
    '$9,500+': Infinity,
    'Not sure yet': Infinity
  };

  function tierFor(coverage, length) {
    if (coverage === 'Not sure — help me decide') {
      return { floor: 5500, tier: 'not-sure',
        headline: 'Most events like yours run $5,500–13,500.' };
    }
    if (coverage === 'Photo only') {
      if (length === 'Half day') {
        return { floor: 1200, tier: 'photo-half',
          headline: 'Event photography for a half day runs $1,200.' };
      }
      return { floor: 1200, tier: 'photo-plus',
        headline: 'Event photography for your event starts at $1,200 — exact quote on a quick call.' };
    }
    if (coverage === 'Video only') {
      if (length === '2–3 days') {
        return { floor: 2500, tier: 'video-multi',
          headline: 'Video coverage starts at $2,500 — multi-day scopes are quoted on a quick call.' };
      }
      return { floor: 2500, tier: 'video',
        headline: 'Video coverage for your event starts at $2,500.' };
    }
    // Photo + video
    if (length === 'Half day') {
      return { floor: 2000, tier: 'story-half',
        headline: 'Photo + video for a half-day event runs $2,000.' };
    }
    if (length === '2–3 days') {
      return { floor: 9500, tier: 'full-coverage',
        headline: 'Full multi-day coverage starts at $9,500 — recent quotes have landed around $13,500.' };
    }
    return { floor: 5500, tier: 'story-standard',
      headline: 'Photo + video coverage for events like yours runs $5,500.' };
  }

  function daysUntil(dateStr, todayStr) {
    if (!dateStr || !todayStr) return null;
    var diff = (new Date(dateStr + 'T00:00:00') - new Date(todayStr + 'T00:00:00')) / 86400000;
    return isNaN(diff) ? null : Math.round(diff);
  }

  /**
   * answers: { coverage, length, budgetRange, eventDate ('' or 'YYYY-MM-DD'), today ('YYYY-MM-DD') }
   * returns: { tier, headline, rushLine|null, underBudgetLine|null }
   */
  function getEstimate(answers) {
    var t = tierFor(answers.coverage, answers.length);
    var result = { tier: t.tier, headline: t.headline, rushLine: null, underBudgetLine: null };

    // Rush mention: photo+video single-day scopes with an event inside 30 days (spec §5).
    if ((t.tier === 'story-standard' || t.tier === 'story-half') && answers.eventDate) {
      var d = daysUntil(answers.eventDate, answers.today);
      if (d !== null && d >= 0 && d <= 30) {
        result.rushLine = 'Tight deadline? Rush delivery gets you the full package in 7 business days — $7,500. We take a maximum of 2 Rush bookings a month.';
      }
    }

    // Under-budget honesty: real range always shows; offer the closest genuine fit.
    var ceiling = BRACKET_CEILINGS[answers.budgetRange];
    if (typeof ceiling === 'number' && ceiling < t.floor) {
      result.underBudgetLine = (answers.coverage === 'Video only')
        ? 'Video coverage starts at $2,500 — if that could work for you, let’s talk.'
        : 'Working with a tighter budget? The closest fit is our $1,200 event photo half-day.';
    }
    return result;
  }

  var api = { getEstimate: getEstimate, BRACKET_CEILINGS: BRACKET_CEILINGS };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
  else { root.FSF_ESTIMATE = api; }
})(typeof window !== 'undefined' ? window : globalThis);
