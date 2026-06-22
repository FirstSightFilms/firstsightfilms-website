import { getStore } from "@netlify/blobs";
import { matchBot } from "./ai-bots.js";

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
  const key = `${Date.now()}-${crypto.randomUUID()}`;   // unique per hit, no append race
  context.waitUntil(                                    // background, after response is sent
    getStore("ai-crawler-hits").set(key, JSON.stringify(hit)).catch(() => {})  // fail silent
  );
  return response;
};

export const config = {
  path: "/*",
  excludedPath: ["/assets/*", "/*.css", "/*.js", "/*.png", "/*.jpg",
                 "/*.jpeg", "/*.svg", "/*.ico", "/*.webp", "/*.woff2"],
};
