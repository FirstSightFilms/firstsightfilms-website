// Tests for src/js/estimate-logic.js — run: node scripts/test_estimate_logic.mjs
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { getEstimate, getResult, EVENT_SERVICE } = require('../src/js/estimate-logic.js');

const COVERAGE = ['Photo only', 'Video only', 'Photo + video', 'Not sure — help me decide'];
const est = (coverage) => getEstimate({ coverage });

// — Event estimate from coverage alone (3-step handoff §5, 2026-11-05) —
assert.equal(est('Photo only').headline, 'Event photography for your event starts at $1,200 — exact quote on a quick call.');
assert.equal(est('Video only').headline, 'Video coverage for your event starts at $2,500.');
assert.equal(est('Photo + video').headline, 'Photo + video for events starts at $2,000 — exact quote on a quick call.');
assert.equal(est('Not sure — help me decide').headline, 'Most events like yours run $5,500–13,500.');

// — Retired numbers must never appear in any output string —
for (const c of COVERAGE) {
  const r = est(c);
  assert.ok(r.tier && r.headline, 'every coverage returns tier + headline');
  for (const bad of ['$1,800', '$9,000', '$3,500', '$1,000', 'up to $10,000', '$1,500'])
    assert.ok(!r.headline.includes(bad), `retired number ${bad} in: ${r.headline}`);
}

// — Result screen by service —
assert.equal(EVENT_SERVICE, 'Event photo and video');
for (const c of COVERAGE) {
  const ev = getResult(EVENT_SERVICE, { coverage: c });
  assert.equal(ev.headline, est(c).headline, 'event path matches getEstimate');
  assert.equal(ev.tier, est(c).tier);
  assert.equal(ev.isEvent, true);
}

// No-price paths: no dollar figure anywhere.
for (const s of ['Marketing content', 'Photos for your business', 'Something else']) {
  const r = getResult(s, { coverage: 'Photo + video' });
  assert.equal(r.isEvent, false, s);
  assert.equal(r.headline, 'Custom package rates.', s);
  assert.ok(!r.headline.includes('$'), `no price for ${s}`);
  assert.ok(r.tier, `tier for ${s}`);
}
const tiers = ['Marketing content', 'Photos for your business', 'Something else'].map((s) => getResult(s, {}).tier);
assert.equal(new Set(tiers).size, 3, 'each non-event path has its own tier');

console.log('All estimate-logic tests passed (4 coverage estimates + 3 no-price paths).');
