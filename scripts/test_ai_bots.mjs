// Tests for netlify/edge-functions/lib/ai-bots.js — run: node scripts/test_ai_bots.mjs
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// The lib is ESM but lives under a package.json without "type": "module", so Node would
// read the .js as CommonJS. Load it as source and import it as a module instead.
const src = readFileSync(new URL('../netlify/edge-functions/lib/ai-bots.js', import.meta.url), 'utf8');
const { AI_BOTS, matchBot } = await import('data:text/javascript,' + encodeURIComponent(src));

// — Roster shape —
const CONTROL_TOKENS = ['Google-Extended', 'Applebot-Extended'];
const fetching = AI_BOTS.filter(b => !CONTROL_TOKENS.includes(b.bot));
assert.equal(fetching.length, 13, '13 fetching crawlers');
assert.equal(AI_BOTS.length, 15, '13 crawlers + 2 non-fetching control tokens');

// — Ordering: an entry whose match string contains an earlier entry's match can never be
//   reached, because matchBot returns the first hit. Guards every prefix pair, not just
//   the Applebot one that prompted this test.
AI_BOTS.forEach((earlier, i) => {
  AI_BOTS.slice(i + 1).forEach(later => {
    assert.ok(
      !later.match.toLowerCase().includes(earlier.match.toLowerCase()),
      `"${later.bot}" is unreachable — "${earlier.bot}" matches first; move it above`
    );
  });
});

// — The Applebot trap. This UA does not occur in the wild (Applebot-Extended is a
//   robots.txt token and never issues requests); the test exists so a reordering of the
//   array cannot silently start filing Applebot-Extended hits as plain Applebot.
const APPLEBOT_EXTENDED_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 (Applebot-Extended/1.0)';
assert.equal(matchBot(APPLEBOT_EXTENDED_UA), 'Applebot-Extended', 'Applebot-Extended must not match as Applebot');
assert.notEqual(matchBot(APPLEBOT_EXTENDED_UA), 'Applebot');

// — Real user agents, each to its own bot —
const UAS = {
  'GPTBot':             'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.2; +https://openai.com/gptbot',
  'OAI-SearchBot':      'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot',
  'ChatGPT-User':       'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot',
  'PerplexityBot':      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot',
  'Perplexity-User':    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user',
  'ClaudeBot':          'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ClaudeBot/1.0; +claudebot@anthropic.com',
  'Claude-User':        'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; Claude-User/1.0; +Claude-User@anthropic.com',
  'Applebot':           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 (Applebot/0.1; +http://www.apple.com/go/applebot)',
  'Bingbot':            'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
  'CCBot':              'CCBot/2.0 (https://commoncrawl.org/faq/)',
  'Meta-ExternalAgent': 'meta-externalagent/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/crawler)',
  'Amazonbot':          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 (Amazonbot/0.1; +https://developer.amazon.com/support/amazonbot)',
  'DuckAssistBot':      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 (compatible; DuckAssistBot/1.0; +https://duckduckgo.com/duckassistbot/)',
};
assert.deepEqual(Object.keys(UAS).sort(), fetching.map(b => b.bot).sort(), 'every fetching crawler has a UA test');
for (const [bot, ua] of Object.entries(UAS)) {
  assert.equal(matchBot(ua), bot, `${bot} UA`);
}

// — Real browsers are not bots. Every Safari UA carries "AppleWebKit", so a sloppy
//   "Apple" match would log every Mac visitor.
assert.equal(matchBot('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'), null, 'Safari on Mac');
assert.equal(matchBot('Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'), null, 'Safari on iPhone');
assert.equal(matchBot('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'), null, 'Googlebot deliberately not tracked');
assert.equal(matchBot(''), null, 'empty UA');
assert.equal(matchBot(null), null, 'missing UA');
assert.equal(matchBot(undefined), null, 'undefined UA');

// — Case insensitivity —
assert.equal(matchBot('mozilla/5.0 (compatible; ccbot/2.0)'), 'CCBot', 'lowercased UA still matches');
assert.equal(matchBot('SOMETHING AMAZONBOT/0.1'), 'Amazonbot', 'uppercased UA still matches');

console.log(`PASS — ${fetching.length} fetching crawlers + ${AI_BOTS.length - fetching.length} control tokens, ordering safe`);
