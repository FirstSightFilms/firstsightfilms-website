// Tests for src/js/estimate-logic.js — run: node scripts/test_estimate_logic.mjs
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { getEstimate } = require('../src/js/estimate-logic.js');

const T = '2026-07-06'; // fixed "today" for rush-window tests

function est(coverage, length, budgetRange, eventDate) {
  return getEstimate({ coverage, length, budgetRange, eventDate, today: T });
}

// — Spec §5 estimate table —
assert.match(est('Photo only', 'Half day', 'Not sure yet', '').headline, /\$1,200/);
assert.match(est('Photo only', 'Full day', 'Not sure yet', '').headline, /starts at \$1,200/);
assert.match(est('Photo only', '2–3 days', 'Not sure yet', '').headline, /starts at \$1,200/);
assert.match(est('Video only', 'Half day', 'Not sure yet', '').headline, /starts at \$2,500/);
assert.match(est('Video only', '2–3 days', 'Not sure yet', '').headline, /multi-day/);
assert.match(est('Photo + video', 'Half day', 'Not sure yet', '').headline, /\$2,750/);
assert.match(est('Photo + video', 'Full day', 'Not sure yet', '').headline, /\$5,500/);
assert.match(est('Photo + video', '2–3 days', 'Not sure yet', '').headline, /\$9,500/);
assert.match(est('Photo + video', '2–3 days', 'Not sure yet', '').headline, /\$13,500/);
assert.match(est('Not sure — help me decide', 'Full day', 'Not sure yet', '').headline, /\$5,500–13,500/);

// — Rush: photo+video single-day, event within 30 days —
assert.ok(est('Photo + video', 'Full day', '$5,500–9,500', '2026-07-20').rushLine, 'rush inside 30d');
assert.match(est('Photo + video', 'Full day', '$5,500–9,500', '2026-07-20').rushLine, /\$7,500/);
assert.equal(est('Photo + video', 'Full day', '$5,500–9,500', '2026-09-30').rushLine, null, 'no rush at 86d');
assert.equal(est('Photo + video', '2–3 days', '$9,500+', '2026-07-20').rushLine, null, 'no rush for multi-day');
assert.equal(est('Video only', 'Full day', 'Not sure yet', '2026-07-20').rushLine, null, 'no rush for video-only');
assert.equal(est('Photo + video', 'Full day', '$5,500–9,500', '').rushLine, null, 'no rush without a date');
assert.ok(est('Photo + video', 'Full day', '$5,500–9,500', '2026-07-06').rushLine, 'rush at day 0 (event today)');
assert.ok(est('Photo + video', 'Full day', '$5,500–9,500', '2026-08-05').rushLine, 'rush at exactly day 30');
assert.equal(est('Photo + video', 'Full day', '$5,500–9,500', '2026-08-06').rushLine, null, 'no rush at day 31');
assert.equal(est('Photo + video', 'Full day', '$5,500–9,500', '2026-07-01').rushLine, null, 'no rush for past dates');

// — Under-budget honesty —
assert.match(est('Photo + video', 'Full day', 'Under $2,500', '').underBudgetLine, /\$1,200 event photo half-day/);
assert.match(est('Not sure — help me decide', 'Full day', 'Under $2,500', '').underBudgetLine, /\$1,200/);
assert.match(est('Video only', 'Full day', 'Under $2,500', '').underBudgetLine, /starts at \$2,500/);
assert.doesNotMatch(est('Video only', 'Full day', 'Under $2,500', '').underBudgetLine, /\$1,200/, 'video-only never offered the photo product');
assert.equal(est('Photo + video', 'Full day', '$2,500–5,500', '').underBudgetLine, null, 'bracket ceiling == floor is NOT under-budget');
assert.equal(est('Photo + video', '2–3 days', '$5,500–9,500', '').underBudgetLine, null, 'ceiling 9500 == floor 9500 OK');
assert.match(est('Photo + video', '2–3 days', '$2,500–5,500', '').underBudgetLine, /\$1,200/);
assert.equal(est('Photo only', 'Half day', 'Under $2,500', '').underBudgetLine, null, 'photo half-day fits every bracket');
assert.equal(est('Photo + video', 'Full day', 'Not sure yet', '').underBudgetLine, null, '"Not sure yet" is never under-budget');

// — Retired numbers must never appear in any output string —
const combos = [];
for (const c of ['Photo + video', 'Video only', 'Photo only', 'Not sure — help me decide'])
  for (const l of ['Half day', 'Full day', '2–3 days'])
    for (const b of ['Under $2,500', '$2,500–5,500', '$5,500–9,500', '$9,500+', 'Not sure yet'])
      for (const d of ['', '2026-07-20'])
        combos.push(est(c, l, b, d));
for (const r of combos) {
  const text = [r.headline, r.rushLine, r.underBudgetLine].filter(Boolean).join(' ');
  for (const bad of ['$1,800', '$9,000', '$3,500', '$1,000', 'up to $10,000'])
    assert.ok(!text.includes(bad), `retired number ${bad} in: ${text}`);
  assert.ok(r.tier && r.headline, 'every combo returns tier + headline');
}

console.log(`All estimate-logic tests passed (${combos.length} combos swept).`);
