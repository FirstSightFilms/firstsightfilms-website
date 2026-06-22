// The ONE place to add/remove a tracked AI bot. match = case-insensitive UA substring.
export const AI_BOTS = [
  { bot: "GPTBot",            match: "GPTBot" },
  { bot: "OAI-SearchBot",     match: "OAI-SearchBot" },
  { bot: "ChatGPT-User",      match: "ChatGPT-User" },
  { bot: "PerplexityBot",     match: "PerplexityBot" },
  { bot: "Perplexity-User",   match: "Perplexity-User" },
  { bot: "ClaudeBot",         match: "ClaudeBot" },
  { bot: "Claude-User",       match: "Claude-User" },
  { bot: "Google-Extended",   match: "Google-Extended" },
  { bot: "Applebot-Extended", match: "Applebot-Extended" },
];

export function matchBot(ua) {
  if (!ua) return null;
  const u = ua.toLowerCase();
  const hit = AI_BOTS.find(b => u.includes(b.match.toLowerCase()));
  return hit ? hit.bot : null;
}
