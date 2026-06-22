import { getStore } from "@netlify/blobs";

// Writes one AI-bot hit to the site-wide ai-crawler-hits Blobs store.
// Called only by the ai-crawler-log edge function (fire-and-forget).
// Node runtime supports @netlify/blobs natively — no edge bundling involved.
export default async (req) => {
  // Shared-secret gate: a wide-open endpoint would let anyone inject fake hits.
  const expected = process.env.AI_CRAWLER_LOG_SECRET || "";
  const got = req.headers.get("x-log-secret") || "";
  if (!expected || got !== expected) {
    return new Response("unauthorized", { status: 401 });
  }

  let hit;
  try {
    hit = await req.json();
  } catch {
    return new Response("bad request", { status: 400 });
  }

  const key = `${Date.now()}-${crypto.randomUUID()}`;  // unique per hit; reader dedupes on it
  try {
    // Site-wide store (NOT getDeployStore) — the external reader pulls the site-wide store.
    await getStore("ai-crawler-hits").set(key, JSON.stringify(hit));
  } catch {
    return new Response("write failed", { status: 500 });
  }

  return new Response("ok", { status: 202 });
};
