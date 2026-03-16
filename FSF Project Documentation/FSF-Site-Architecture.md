# FSF Site Architecture & SEO Strategy

**Goal:** Rank #1 for "video production st augustine" within 12 weeks
**Secondary Goal:** Expand into Jacksonville market
**Current Position:** #16 (page 2)
**Date:** 2026-03-16

---

## Executive Summary

First Sight Films' website uses a **hub and spoke model** where service landing pages (hubs) capture search traffic, and event/project pages (spokes) build topical authority and serve as social proof for conversion.

Unlike wedding photographers who create venue pages to capture "[venue] wedding photographer" searches, FSF's event pages serve a different purpose: they signal local expertise to Google and provide credibility to prospects who land on the site via broader searches like "video production st augustine."

**Key Markets:**
- St. Augustine (primary)
- Jacksonville (secondary, to build)

---

## The Hub & Spoke Model

### How It Works

```
                                    HOMEPAGE
                           firstsightfilms.com/
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
   VIDEO SERVICES              PHOTO SERVICES              CORPORATE VIDEO
        │                             │                             │
   ┌────┴────┐                   ┌────┴────┐                        │
   │         │                   │         │                        │
   ▼         ▼                   ▼         ▼                        ▼
ST. AUG   JAX                ST. AUG   JAX                   /corporate-video-
VIDEO     VIDEO              PHOTO     PHOTO                  st-augustine/
   │         │                   │         │
   │         │                   │         │
/st-augustine-  /jacksonville-  /st-augustine-  /jacksonville-
video-production/ video-production/ photography/  photography/
   │         │                   │         │
   │         │                   │         │
   └────┬────┘                   └────┬────┘
        │                             │
        ▼                             ▼
   EVENT SPOKE PAGES            EVENT SPOKE PAGES
   (support video hubs)         (support photo hubs)
```

### Page Purposes

| Page Type | Primary Purpose | Secondary Purpose |
|-----------|-----------------|-------------------|
| **Hub pages** | Capture search traffic | Convert visitors |
| **Spoke pages** (events/projects) | Build hub's authority + local signals | Social proof for conversion |

---

## Rob Futrell's Service Structure (Reference)

Rob creates **location variants** and **service variants** to capture multiple keywords:

```
                            robfutrell.com
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
    ▼                             ▼                             ▼
PHOTOGRAPHY                  VIDEOGRAPHY                   COMMERCIAL
SERVICES                     SERVICES                      SERVICES
    │                             │                             │
    │                             │                             │
    ├── Wedding                   └── Wedding                   ├── Headshots
    │   ├── St. Augustine             Videography               ├── Branding
    │   ├── Jacksonville                                        └── Corporate Events
    │   └── Courthouse
    │
    ├── Elopement
    │   ├── St. Augustine
    │   └── Amelia Island
    │
    ├── Engagement
    ├── Proposal
    ├── Family
    ├── Maternity
    └── Newborn
```

**Key Insight:** Rob creates geo-variants of the same service to capture different local searches.

---

## Current FSF Site Structure

### Core Pages
```
/                                    Homepage
/aboutus/                            About Us
/contact/                            Contact
/portfolio/                          Portfolio
```

### Service Hub Pages (Current)
```
/st-augustine-video-production/              PRIMARY HUB - Target: "video production st augustine"
/st-augustine-jacksonville-video-production/ Secondary (consolidate?)
/corporate-video-st-augustine/               Corporate video hub
/st-augustine-photography/                   Photography hub
/saint-augustine-jacksonville-photographer/  Photography secondary (consolidate?)
```

### Event/Project Spoke Pages (Current - 13 legacy projects)
```
/st-augustine-video-production/
├── fortmose/
├── staugustineamp/
├── iceplant/
├── seamarkranch/
├── singoutloud2024/
├── singoutloud2018/
├── sjcchamberofcommerce/
├── avilesstreetfestival/
├── friendsofacadia/
├── epiccure/
├── fishtankstudios/
├── rockymountainconservancy/
└── livewildlyfloridastateparkfoundation/
```

---

## Target FSF Site Structure

### Full Site Map

```
firstsightfilms.com/
│
├── CORE PAGES
│   ├── /aboutus/
│   ├── /contact/
│   └── /portfolio/
│
├── VIDEO HUBS
│   │
│   ├── /st-augustine-video-production/          ◄── PRIMARY TARGET
│   │   ├── /fort-mose-jazz-blues-festival/
│   │   ├── /sing-out-loud-festival/
│   │   ├── /st-augustine-amphitheatre/
│   │   ├── /aviles-street-festival/
│   │   ├── /flagler-college/
│   │   ├── /ice-plant-bar/
│   │   ├── /st-johns-cultural-council/
│   │   ├── /seamark-ranch/
│   │   └── /florida-state-parks/
│   │
│   ├── /jacksonville-video-production/          ◄── TO BUILD
│   │   └── (Jacksonville-specific events/clients)
│   │
│   └── /corporate-video-st-augustine/           ◄── EXISTS
│       └── (corporate client case studies)
│
├── PHOTO HUBS
│   │
│   ├── /st-augustine-photography/               ◄── EXISTS (needs build-out)
│   │   └── (event/project spoke pages)
│   │
│   ├── /jacksonville-photography/               ◄── TO BUILD
│   │   └── (event/project spoke pages)
│   │
│   └── /st-augustine-event-photography/         ◄── TO BUILD (optional)
│
└── RESOURCES (future)
    ├── /st-augustine-event-venues/              (venue guides like Rob)
    └── /video-production-pricing/
```

---

## Service Hub Strategy

### Video Production Hubs

| Page | Target Keyword | Status | Priority |
|------|----------------|--------|----------|
| `/st-augustine-video-production/` | "video production st augustine" | EXISTS | P0 |
| `/jacksonville-video-production/` | "video production jacksonville" | TO BUILD | P1 |
| `/corporate-video-st-augustine/` | "corporate video st augustine" | EXISTS | P1 |

### Photography Hubs

| Page | Target Keyword | Status | Priority |
|------|----------------|--------|----------|
| `/st-augustine-photography/` | "photographer st augustine" | EXISTS | P1 |
| `/jacksonville-photography/` | "photographer jacksonville" | TO BUILD | P2 |
| `/st-augustine-event-photography/` | "event photographer st augustine" | TO BUILD | P2 |

---

## Event Spoke Pages Strategy

### How Spoke Pages Connect to Multiple Hubs

A single event page can support multiple hubs through internal linking:

```
                    fort-mose-jazz-blues-festival/
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
    Links to:            Links to:            Links to:
/st-augustine-        /st-augustine-      /jacksonville-
video-production/     photography/        video-production/
                                          (if JAX audience)
```

**Example internal links on event pages:**
- "View more of our [St. Augustine video production](/st-augustine-video-production/) work"
- "See our [event photography](/st-augustine-photography/) from this festival"
- "We also serve [Jacksonville](/jacksonville-video-production/) for event coverage"

### Priority Event Pages to Build

**High Priority (Local St. Augustine):**
| Page | Event/Venue | Status |
|------|-------------|--------|
| `/st-augustine-video-production/fort-mose-jazz-blues-festival/` | Fort Mose Jazz & Blues | IN PROGRESS |
| `/st-augustine-video-production/sing-out-loud-festival/` | Sing Out Loud Festival | TO BUILD |
| `/st-augustine-video-production/st-augustine-amphitheatre/` | The Amp | TO BUILD |
| `/st-augustine-video-production/aviles-street-festival/` | Aviles Street Festival | TO BUILD |

**Medium Priority (Local Clients/Venues):**
| Page | Event/Venue | Status |
|------|-------------|--------|
| `/st-augustine-video-production/flagler-college/` | Flagler College | TO BUILD |
| `/st-augustine-video-production/ice-plant-bar/` | Ice Plant Bar | TO BUILD |
| `/st-augustine-video-production/st-johns-cultural-council/` | SJCC | TO BUILD |
| `/st-augustine-video-production/seamark-ranch/` | Seamark Ranch | TO BUILD |

**Lower Priority (Non-Local - National Credibility):**
| Page | Event/Venue | Status |
|------|-------------|--------|
| `/st-augustine-video-production/florida-state-parks/` | FL State Parks | TO BUILD |
| `/st-augustine-video-production/friends-of-acadia/` | Friends of Acadia | TO BUILD |
| `/st-augustine-video-production/rocky-mountain-conservancy/` | Rocky Mountain | TO BUILD |

---

## How Authority Flows

```
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   SPOKE PAGES (event/project pages)                 │
    │                                                     │
    │   fort-mose ──────┐                                 │
    │   sing-out-loud ──┼──► Link equity flows to HUB    │
    │   amphitheatre ───┤                                 │
    │   aviles-fest ────┘                                 │
    │                                                     │
    └─────────────────────┬───────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   HUB PAGE                                          │
    │   /st-augustine-video-production/                   │
    │                                                     │
    │   - Captures search traffic                         │
    │   - Ranks for "video production st augustine"       │
    │   - Benefits from spoke page authority              │
    │                                                     │
    └─────────────────────────────────────────────────────┘
```

---

## How Event Pages Support SEO

### 1. Topical Authority
Multiple pages about video production in St. Augustine tells Google: "This site is deeply about video production in St. Augustine."

### 2. Local Entity Association
Mentioning recognized local entities associates FSF with these entities in Google's index:
- Fort Mose Historic State Park
- St. Augustine Amphitheatre
- Flagler College
- St. Johns County
- Sing Out Loud Festival

### 3. Internal Link Equity
Each event page links back to the hub page, passing authority.

### 4. Content Depth
More quality content across the site = more domain authority for all pages.

### 5. Long-Tail Traffic (Bonus)
Some searches may land on event pages:
- "festival videographer florida"
- "event video production northeast florida"

---

## How Event Pages Support Conversion

### The Visitor Journey

```
1. Prospect searches "video production st augustine"
                    │
                    ▼
2. Lands on /st-augustine-video-production/ (hub page)
                    │
                    ▼
3. Sees: "We've covered Fort Mose, Sing Out Loud, the Amp..."
                    │
                    ▼
4. Clicks through to event page, sees the work
                    │
                    ▼
5. Thinks: "These people are legit. They've done major local events."
                    │
                    ▼
6. Reaches out via contact form
```

### Target Audience for Event Pages

**Who:** Overwhelmed event organizers who:
- Don't want to micromanage a videographer
- Don't want to answer questions on event day
- Want someone who "just handles it"

**Key Messages:**
- "We come prepared" — no questions on event day
- "We stay out of your way" — work independently
- "We deliver fast" — 48hr social clips, 2 week recap
- "We know this venue/event" — credibility through experience

---

## Comparison: Rob Futrell vs FSF

| Metric | Rob Futrell | FSF Current | FSF Target |
|--------|-------------|-------------|------------|
| Service hub pages | ~14 | 5 | 8-10 |
| Venue/event spoke pages | 95 | 13 (legacy) | 15-20 |
| Portfolio galleries | 140 | 0 | 10-20 |
| Resource/guide pages | 35 | 0 | 5-10 |
| **Total pages** | **~370** | **~35** | **~60-80** |

### Key Difference

**Rob's venue pages** = Fishing nets (each catches its own traffic)
- Couples search "[venue] wedding photographer"
- 95 venue pages = 95 keyword targets

**FSF's event pages** = Weights on the main net (strengthen the hub)
- Event organizers search "video production st augustine"
- Event pages build authority for the hub, which catches traffic

---

## Event Page Template

### Required Sections

1. **Hero**
   - Event name
   - "Official Video Partner" badge (if applicable)
   - Tagline addressing organizer pain point
   - Proof points (years covered, location)
   - CTA

2. **What You Get**
   - "We come prepared"
   - "We stay out of your way"
   - "We deliver fast"

3. **Gallery**
   - 2-4 images minimum
   - Geo-rich alt text

4. **About the Event/Venue**
   - Historical/contextual information
   - Local entity mentions (SEO value)
   - FSF's relationship with the event

5. **How It Works**
   - Simple 3-step process
   - Emphasize low-effort for client

6. **FAQ**
   - What do we get?
   - How much does it cost?
   - How far in advance to book?
   - What if we've never worked with a videographer?
   - Do you also shoot photos?

7. **CTA**
   - Clear call to action
   - Link to contact

### Required SEO Elements

- **Title tag:** "[Event Name] Video Production | First Sight Films St. Augustine"
- **Meta description:** Mention event, location, FSF's experience
- **H1:** Event name
- **Schema:** FAQPage, Event, Service, BreadcrumbList
- **Internal links:** To hub page and related event pages
- **Image alt text:** Include location and event names

---

## URL Structure

### Naming Convention
- Use full, descriptive slugs: `fort-mose-jazz-blues-festival` not `fortmose`
- Include location when relevant: `st-augustine-amphitheatre`
- Hyphenate words: `sing-out-loud-festival`

### Hierarchy
All event pages nest under the relevant hub:
```
/st-augustine-video-production/fort-mose-jazz-blues-festival/
/st-augustine-video-production/sing-out-loud-festival/
/jacksonville-video-production/[jacksonville-event]/
```

---

## Duplicate Content Issue

**Problem:** Current sitemap shows identical project pages under both:
- `/st-augustine-video-production/[project]/`
- `/st-augustine-jacksonville-video-production/[project]/`

**Solution:**
- Keep pages only under `/st-augustine-video-production/`
- Remove or redirect `/st-augustine-jacksonville-video-production/` entirely
- Create separate `/jacksonville-video-production/` hub with its own unique content

---

## Action Items

### Immediate (This Week)
- [ ] Finalize Fort Mose page with correct structure
- [ ] Update URL from `/fortmose/` to `/fort-mose-jazz-blues-festival/`
- [ ] Add BreadcrumbList schema to Fort Mose page
- [ ] Ensure hub page links to Fort Mose page

### Short-Term (Next 2-4 Weeks)
- [ ] Create Sing Out Loud Festival page
- [ ] Create St. Augustine Amphitheatre page
- [ ] Create `/jacksonville-video-production/` hub page
- [ ] Update sitemap with new URLs
- [ ] Remove duplicate pages under `/st-augustine-jacksonville-video-production/`

### Medium-Term (4-8 Weeks)
- [ ] Create remaining priority event pages
- [ ] Build out `/jacksonville-photography/` hub
- [ ] Add more images to all event pages
- [ ] Strengthen internal linking between pages
- [ ] Monitor Search Console for indexing and ranking changes

### Long-Term (8-12 Weeks)
- [ ] Create resource/guide pages (venue guides, pricing page)
- [ ] Add portfolio gallery pages
- [ ] Expand Jacksonville event coverage pages
- [ ] Evaluate need for additional service hubs

---

## Success Metrics

| Metric | Current | 4-Week Target | 12-Week Target |
|--------|---------|---------------|----------------|
| Ranking: "video production st augustine" | #16 | Top 10 | #1-3 |
| Ranking: "video production jacksonville" | N/A | Top 20 | Top 10 |
| Indexed pages | ~35 | 45 | 60+ |
| Organic traffic (monthly) | TBD | +25% | +100% |
| Contact form submissions | TBD | +20% | +50% |

---

## Reference: How Leads Find FSF

**Example:** Email from Irish Consulate General

> "We are looking to hire a videographer for our Saint-Patrick's day event in ST-Augustine on Sunday, March 8th 2026. This will take place at Flagler College."

**Their search was likely:** "videographer st augustine" or "event videographer st augustine"
**NOT:** "Flagler College videographer"

**Conclusion:** Hub pages capture traffic; event pages provide credibility and build hub authority.

---

*Last updated: 2026-03-16*
