import { matchBot } from "./lib/ai-bots.js";

export default async (request, context) => {
  const ua = request.headers.get("user-agent") || "";
  const bot = matchBot(ua);

  if (!bot) return;                       // not an AI bot → pass straight through (one substring check)

  const response = await context.next();  // real response, returned untouched
  const hit = {
    bot,
    page: new URL(request.url).pathname,  // path as-received; the reader adds the host
    ts: new Date().toISOString(),
    status: response.status,
    ua,
  };
  // Hand the write off to a Node function (the Blobs SDK works natively in the
  // Node runtime; edge bundling does not). Fire-and-forget after the response is sent.
  const secret = Netlify.env.get("AI_CRAWLER_LOG_SECRET") || "";
  const origin = new URL(request.url).origin;
  context.waitUntil(
    fetch(`${origin}/.netlify/functions/ai-crawler-write`, {
      method: "POST",
      headers: { "content-type": "application/json", "x-log-secret": secret },
      body: JSON.stringify(hit),
    }).catch(() => {})  // fail silent — never affects the visitor
  );
  return response;
};

export const config = {
  path: "/*",
  excludedPath: ["/.netlify/*", "/assets/*", "/*.css", "/*.js", "/*.png", "/*.jpg",
                 "/*.jpeg", "/*.svg", "/*.ico", "/*.webp", "/*.woff2"],
};
