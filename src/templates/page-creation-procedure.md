# Page Creation Procedure

Interactive step-by-step process for creating new pages.

## Trigger Phrases

User says:
- "Create a new page for [name]"
- "Build a page for [project]"
- "New page: [topic]"

---

## STEP 1: Page Setup

**Ask:**
1. URL path (e.g., `/st-augustine-video-production/client-name/`)
2. Page title (e.g., "Client Name Video Production | First Sight Films")
3. Meta description (1-2 sentences for SEO)
4. Body class (e.g., `page-project`, `page-service`)

**Defaults:**
- Body class: `page-project`

---

## STEP 2: Hero Section

**Ask:**
1. Hero label (small text above H1)
2. H1 headline
3. Tagline (1-2 sentences below H1)
4. Stats to display? (e.g., "3+ Years", "20+ Events", "50+ Videos")

**Defaults:**
- Hero label: "St. Augustine Video Production"
- Stats: none

---

## STEP 3: About Section

**Ask:**
1. Section heading (e.g., "About [Client Name]")
2. About content (2-4 paragraphs describing the client/project)
3. Include "View more work" link? (yes/no)

**Defaults:**
- Include link: yes, pointing to `/st-augustine-video-production/`

---

## STEP 4: Portfolio Grid

**Ask:**
1. Include portfolio grid? (yes/no/custom)
2. If custom: which projects to feature?
3. Custom heading/subtitle?

**Defaults:**
- Use standard `{{portfolio-grid}}` module

**Skip behavior:**
- If skipped, remove `{{portfolio-grid}}` from page

---

## STEP 5: Photo Gallery

**Ask:**
1. Include photo gallery? (yes/no)
2. Image folder path (e.g., `/images/portfolio/client-name/`)
3. Gallery heading?

**Defaults:**
- Use standard `{{photo-gallery}}` module

**Skip behavior:**
- If skipped, remove `{{photo-gallery}}` from page

---

## STEP 6: Reviews

**Ask:**
1. Include reviews section? (yes/no)

**Defaults:**
- Use standard `{{reviews}}` module (loads from testimonials.json)

**Skip behavior:**
- If skipped, remove `{{reviews}}` from page

---

## STEP 7: FAQ

**Ask:**
1. Include FAQ section? (yes/no)
2. FAQ name (creates/uses `src/faqs/[name].json`)
3. FAQ heading (e.g., "Frequently Asked Questions")
4. FAQ questions (if creating new)

**Defaults:**
- FAQ heading: "Frequently Asked Questions"

**Skip behavior:**
- If skipped, remove FAQ section and schema from page

---

## Controls

During the process, user can say:
- **"skip"** - Omit section or use defaults
- **"back"** - Return to previous step
- **"show progress"** - Display current answers
- **"finish"** - Generate page with current content (remaining steps skipped)

---

## Output

After all steps complete (or user says "finish"):

1. Create page file at specified URL path
2. Create FAQ JSON if new FAQ was defined
3. Run build script
4. Show summary of created files

---

## Example Session

```
User: Create a new page for Beachside Brewery

Claude: Starting page creation for Beachside Brewery.

STEP 1: Page Setup

1. URL path?
2. Page title?
3. Meta description?
4. Body class? (default: page-project)

User:
1. /st-augustine-video-production/beachside-brewery/
2. Beachside Brewery Video Production | St. Augustine Videographer
3. Brand video and event coverage for Beachside Brewery in St. Augustine, FL.
4. skip

Claude: Got it.
- URL: /st-augustine-video-production/beachside-brewery/
- Title: Beachside Brewery Video Production | St. Augustine Videographer
- Meta: Brand video and event coverage for Beachside Brewery in St. Augustine, FL.
- Body class: page-project (default)

STEP 2: Hero Section
...
```
