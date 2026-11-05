/**
 * Estimate mapping for the contact wizard.
 * Every price cites fsf-workspace/shared/strategy/pricing-ladder.md (canonical).
 * Do not add or change a number here without changing the ladder first.
 * Browser: window.FSF_ESTIMATE. Node (tests): module.exports.
 */
(function (root) {
  'use strict';

  // Coverage literals must byte-match the form's coverage_type radio values (em dash in 'Not sure — help me decide').
  function tierFor(coverage) {
    if (coverage === 'Photo only') {
      // pricing-ladder.md:18 — event photo half-day, $1,200
      return { tier: 'photo',
        headline: 'Event photography for your event starts at $1,200 — exact quote on a quick call.' };
    }
    if (coverage === 'Video only') {
      // pricing-ladder.md:19 — video day, from $2,500
      return { tier: 'video',
        headline: 'Video coverage for your event starts at $2,500.' };
    }
    if (coverage === 'Photo + video') {
      // pricing-ladder.md:20 — Event Story half-day, $2,000
      return { tier: 'photo-video',
        headline: 'Photo + video for events starts at $2,000 — exact quote on a quick call.' };
    }
    return { tier: 'not-sure',
      headline: 'Most events like yours run $5,500–13,500.' };
  }

  /**
   * answers: { coverage }
   * returns: { tier, headline }
   */
  function getEstimate(answers) {
    var t = tierFor(answers.coverage);
    return { tier: t.tier, headline: t.headline };
  }

  // Keys must byte-match the form's `service` radio values.
  var EVENT_SERVICE = 'Event photo and video';
  var NO_PRICE_TIERS = {
    'Marketing content': 'marketing-content',
    'Photos for your business': 'business-photos',
    'Something else': 'other'
  };

  /**
   * Result screen by service.
   * returns: { tier, headline, isEvent }
   */
  function getResult(service, answers) {
    if (service === EVENT_SERVICE) {
      var e = getEstimate(answers);
      e.isEvent = true;
      return e;
    }
    return { tier: NO_PRICE_TIERS[service] || 'other', headline: 'Custom package rates.', isEvent: false };
  }

  var api = { getEstimate: getEstimate, getResult: getResult, EVENT_SERVICE: EVENT_SERVICE };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
  else { root.FSF_ESTIMATE = api; }
})(typeof window !== 'undefined' ? window : globalThis);
