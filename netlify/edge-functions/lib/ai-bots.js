// The ONE place to add/remove a tracked AI bot. match = case-insensitive UA substring.
//
// ORDERING MATTERS: matchBot returns the FIRST substring hit, so whenever one match string
// is contained in another, the longer one must come first. "Applebot-Extended" is listed
// above "Applebot" for exactly that reason — flipped, every Applebot-Extended UA would be
// recorded as plain Applebot. Any future prefix pair carries the same trap.
export const AI_BOTS = [
  // Control tokens, not crawlers. These are robots.txt opt-out tokens that govern whether
  // content the real crawlers already fetched may be used for AI. Neither issues requests,
  // so both will read "never" in the logs forever — that is correct, not a capture gap.
  //   Google: "Google-Extended doesn't have a separate HTTP request user agent string."
  //   Apple:  "Applebot-Extended does not crawl webpages."
  // Kept here so the "never" row documents itself and nobody re-adds them as real targets.
  { bot: "Google-Extended",    match: "Google-Extended" },
  { bot: "Applebot-Extended",  match: "Applebot-Extended" },  // must stay above "Applebot"

  // Fetching crawlers.
  { bot: "GPTBot",             match: "GPTBot" },
  { bot: "OAI-SearchBot",      match: "OAI-SearchBot" },
  { bot: "ChatGPT-User",       match: "ChatGPT-User" },
  { bot: "PerplexityBot",      match: "PerplexityBot" },
  { bot: "Perplexity-User",    match: "Perplexity-User" },
  { bot: "ClaudeBot",          match: "ClaudeBot" },
  { bot: "Claude-User",        match: "Claude-User" },
  { bot: "Applebot",           match: "Applebot" },           // Siri / Spotlight / Apple Intelligence
  { bot: "Bingbot",            match: "bingbot" },            // feeds Microsoft Copilot
  { bot: "CCBot",              match: "CCBot" },              // Common Crawl; robots.txt already allows it
  { bot: "Meta-ExternalAgent", match: "meta-externalagent" }, // Meta AI
  { bot: "Amazonbot",          match: "Amazonbot" },          // Alexa / Rufus
  { bot: "DuckAssistBot",      match: "DuckAssistBot" },      // DuckDuckGo AI answers
];

export function matchBot(ua) {
  if (!ua) return null;
  const u = ua.toLowerCase();
  const hit = AI_BOTS.find(b => u.includes(b.match.toLowerCase()));
  return hit ? hit.bot : null;
}
