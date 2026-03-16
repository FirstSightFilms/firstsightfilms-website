# Site Module + Python Systems

Reference document for the FSF modular website architecture.

---

## Overview

This system uses:
- **HTML Modules**: Reusable components stored as separate files in `src/modules/`
- **Python Build Script**: Combines modules + pages into complete HTML
- **Placeholder Syntax**: `{{module-name}}` in pages, replaced during build
- **Local + GitHub Workflow**: Edit locally, build, push to GitHub, Netlify deploys

---

## Current Project Structure

```
downloaded_site/
│
├── src/                           # SOURCE FILES (edit these)
│   ├── modules/                   # Reusable components
│   │   ├── head.html              # <head> with meta, fonts, CSS links
│   │   ├── header.html            # Logo + navigation + mobile menu
│   │   ├── footer.html            # Footer with CTA, contact, social
│   │   ├── schema.html            # LocalBusiness JSON-LD schema
│   │   ├── portfolio-grid.html    # Video project grid (8 projects)
│   │   └── why-st-augustine.html  # "Why St. Augustine?" section
│   │
│   ├── pages/                     # Page templates with {{placeholders}}
│   │   ├── index.html             # Homepage
│   │   ├── aboutus/index.html
│   │   ├── contact/index.html
│   │   ├── portfolio/index.html
│   │   ├── st-augustine-photography/index.html
│   │   ├── corporate-video-st-augustine/index.html
│   │   └── st-augustine-video-production/
│   │       ├── index.html         # Video landing page
│   │       ├── fortmose/index.html
│   │       ├── staugustineamp/index.html
│   │       └── ... (13 project pages)
│   │
│   ├── css/
│   │   ├── base.css
│   │   ├── header.css
│   │   ├── components.css         # Buttons, cards, gallery, portfolio grid
│   │   ├── site_3e6e8161.css      # Legacy Squarespace CSS
│   │   └── static_b4ee7412.css    # Legacy Squarespace CSS
│   │
│   ├── faqs/                      # FAQ content by page
│   │   ├── homepage.html
│   │   ├── homepage-schema.json
│   │   └── corporate-video-st-augustine.html
│   │
│   └── reviews/
│       └── reviews.json           # Google reviews data
│
├── scripts/
│   └── build.py                   # Main build script
│
├── output/                        # GENERATED SITE (auto-built)
│   └── ...                        # Served by Netlify
│
├── images/                        # Website images
│   ├── bento/
│   ├── hero/
│   ├── about/
│   ├── logos/
│   └── portfolio/
│
└── netlify.toml                   # Serves from /output
```

---

## Current Modules

### `src/modules/head.html`
Contains `<head>` content: charset, viewport, fonts (Roboto, Poppins), CSS links.

### `src/modules/header.html`
```html
<header class="site-header">
  <div class="header-inner">
    <a href="/" class="header-logo">
      <img src="/images/logos/first-sight-films-logo-st-augustine-fl.png"
           alt="First Sight Films - St. Augustine Video & Photo Production">
    </a>
    <div class="header-tagline">
      <span class="tagline-top">Video Production & Photography</span>
      <span class="tagline-bottom">St. Augustine | Jacksonville</span>
    </div>
    <nav class="header-nav">
      <a href="/st-augustine-video-production/">Video</a>
      <a href="/st-augustine-photography/">Photo</a>
      <a href="/aboutus/">About</a>
      <a href="/contact/" class="nav-cta">Let's Talk</a>
    </nav>
    <button class="mobile-menu-toggle">...</button>
  </div>
</header>
```

### `src/modules/footer.html`
Footer with CTA banner, contact info, social links, service areas.

### `src/modules/portfolio-grid.html`
8-project grid linking to video project pages with location pills.

### `src/modules/why-st-augustine.html`
Local history section about Diego and Trista's connection to St. Augustine.

---

## Page Template Example

### `src/pages/index.html` (Homepage)
```html
<!DOCTYPE html>
<html lang="en">
<head>
{{head}}
</head>
<body class="page-home">

{{header}}

<main>
  <!-- Hero Section -->
  <section class="hero hero-split">
    ...
  </section>

  <!-- Services Bento Grid -->
  <section class="bento-portfolio">
    ...
  </section>

  <!-- About Teaser -->
  <section class="section-about-teaser">
    ...
  </section>

{{why-st-augustine}}

{{portfolio-grid}}

{{reviews}}

  <!-- FAQ Section -->
  <section class="section-faq">
    {{faq:homepage}}
  </section>

</main>

{{faq-schema:homepage}}
{{schema}}
{{footer}}

</body>
</html>
```

---

## Placeholder Syntax

| Placeholder | Description |
|-------------|-------------|
| `{{header}}` | Inserts header.html module |
| `{{footer}}` | Inserts footer.html module |
| `{{head}}` | Inserts head.html module |
| `{{schema}}` | Inserts schema.html module |
| `{{portfolio-grid}}` | Inserts portfolio grid section |
| `{{why-st-augustine}}` | Inserts Why St. Augustine section |
| `{{reviews}}` | Inserts reviews from reviews.json |
| `{{faq:page-name}}` | Inserts FAQ content for specific page |
| `{{faq-schema:page-name}}` | Inserts FAQ schema JSON-LD |

**Note:** Hyphens are supported in module names.

---

## Build Process

### Command
```bash
cd "/Users/diegosmbp/Downloads/diegos first script/downloaded_site"
python3 scripts/build.py
```

### What It Does
1. Loads all modules from `src/modules/`
2. For each page in `src/pages/`:
   - Reads the HTML template
   - Replaces `{{placeholder}}` with module content
   - Handles special placeholders (faq, reviews, schema)
   - Writes complete HTML to `output/`
3. Copies CSS from `src/css/` to `output/css/`
4. Copies images to `output/images/`

### Output
```
src/pages/index.html + modules → output/index.html
src/pages/aboutus/index.html + modules → output/aboutus/index.html
...
```

---

## Development Workflow

### Making Changes
1. Edit source files in `src/pages/` or `src/modules/`
2. Run: `python3 scripts/build.py`
3. Test locally: `python3 -m http.server 8000 --directory output`
4. View at: http://localhost:8000

### Deploying
```bash
git add -A
git commit -m "Description of changes"
git push origin main
```
Netlify auto-deploys from `output/` folder.

---

## Related Tools

### FSF Image Optimizer
Location: `/Users/diegosmbp/Desktop/FSF Image Optimizer/`

**Features:**
- Watch folder automation
- Converts to WebP (large/medium/thumb sizes)
- SEO-friendly naming prompts
- Claude API integration for alt text generation

**Usage:**
```bash
python3 "/Users/diegosmbp/Desktop/FSF Image Optimizer/start-optimizer.py"
```

---

## Future Enhancements (Not Yet Built)

- [ ] `generate_sitemap.py` - Auto-generate XML sitemap
- [ ] `generate_schema.py` - Auto-generate schema for new pages
- [ ] Location/service page generator for scaling
- [ ] Automated internal linking
- [ ] Image sitemap generation

---

## Reference

- Architecture inspired by: robfutrell.com
- Tools: Python 3, HTML modules, Netlify
- Last updated: March 15, 2026
