# Site Module + Python Systems

Reference document for implementing a modular website architecture like robfutrell.com.

---

## Overview

This system uses:
- **HTML Modules**: Reusable components (header, footer, nav, etc.) stored as separate files
- **Python Scripts**: Automation for building pages, optimizing images, generating SEO elements
- **Local + GitHub Workflow**: Edit locally, push to GitHub, Netlify deploys

---

## Project Structure

```
firstsightfilms-website/
│
├── src/                           # SOURCE FILES (you edit these)
│   ├── modules/                   # Reusable components
│   │   ├── head.html              # <head> with meta, fonts, CSS
│   │   ├── header.html            # Logo + navigation
│   │   ├── footer.html            # Footer content
│   │   ├── navigation.html        # Nav menu (included in header)
│   │   ├── video-player.html      # Video embed component
│   │   ├── testimonials.html      # Testimonials section
│   │   ├── schema-business.html   # LocalBusiness schema
│   │   ├── schema-video.html      # VideoObject schema template
│   │   └── contact-form.html      # Contact form component
│   │
│   ├── pages/                     # Page-specific content
│   │   ├── index.html             # Homepage content only
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── portfolio.html
│   │   ├── photo.html
│   │   └── video/                 # Video project pages
│   │       ├── fortmose.html
│   │       ├── iceplant.html
│   │       └── ...
│   │
│   ├── css/
│   │   └── styles.css             # Your styles (cleaned up)
│   │
│   └── images/                    # Source images
│       ├── logo/
│       ├── portfolio/
│       └── projects/
│
├── scripts/                       # Python automation
│   ├── build.py                   # Combines modules + pages → output
│   ├── optimize_images.py         # Resize, convert to WebP
│   ├── generate_schema.py         # Create/update schema markup
│   └── generate_sitemap.py        # Build XML sitemap
│
├── output/                        # COMPILED SITE (auto-generated)
│   ├── index.html                 # Final HTML files
│   ├── about/index.html
│   ├── video/fortmose/index.html
│   ├── css/
│   ├── images/                    # Optimized images
│   └── sitemap.xml
│
├── netlify.toml                   # Tells Netlify to serve from /output
└── README.md
```

---

## How the Modules Work

### Example: `src/modules/header.html`
```html
<header class="site-header">
  <a href="/" class="logo">
    <img src="/images/logo/fsf-logo.png" alt="First Sight Films" width="180" height="60">
  </a>
  {{navigation}}
</header>
```

### Example: `src/modules/navigation.html`
```html
<nav class="main-nav">
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/video/">Video</a></li>
    <li><a href="/photo/">Photo</a></li>
    <li><a href="/portfolio/">Portfolio</a></li>
    <li><a href="/about/">About</a></li>
    <li><a href="/contact/">Contact</a></li>
  </ul>
</nav>
```

### Example: `src/modules/footer.html`
```html
<footer class="site-footer">
  <div class="footer-content">
    <div class="footer-brand">
      <img src="/images/logo/fsf-logo.png" alt="First Sight Films">
      <p>Professional video production for St. Augustine businesses.</p>
    </div>
    <div class="footer-contact">
      <p>St. Augustine, FL 32080</p>
      <p><a href="tel:+19542947868">(954) 294-7868</a></p>
      <p><a href="mailto:info@firstsightfilms.com">info@firstsightfilms.com</a></p>
    </div>
    <div class="footer-social">
      <a href="https://www.instagram.com/firstsightfilms/">Instagram</a>
    </div>
  </div>
  <p class="copyright">© 2026 First Sight Films. All rights reserved.</p>
</footer>
```

### Example: `src/pages/index.html` (Homepage)
```html
{{head}}
<body>
{{header}}

<main>
  <section class="hero">
    {{video-player:hero-reel}}
    <h1>Premier Video Production for St. Augustine Businesses</h1>
    <a href="/contact/" class="btn">Start Your Video Project</a>
  </section>

  <section class="about-preview">
    <h2>More Than Just Videographers</h2>
    <p>We're business content strategists, with a few cameras.</p>
  </section>

  {{testimonials}}
</main>

{{schema-business}}
{{footer}}
</body>
</html>
```

---

## How the Build Script Works

When you run `python scripts/build.py`:

1. **Reads** each page from `src/pages/`
2. **Finds** placeholders like `{{header}}`, `{{footer}}`
3. **Replaces** them with content from `src/modules/`
4. **Outputs** complete HTML files to `output/`

```
src/pages/index.html + src/modules/* → output/index.html
src/pages/about.html + src/modules/* → output/about/index.html
```

**Result:** You edit modules once, run build, all pages update.

---

## Automation Scripts

### 1. Image Optimization (`optimize_images.py`)
```
Input:  src/images/projects/fortmose/ceremony.jpg (4MB, 4000x3000)
Output: output/images/projects/fortmose/ceremony.webp (150KB, 1920x1440)
        output/images/projects/fortmose/ceremony-thumb.webp (20KB, 400x300)
```

**What it does:**
- Converts JPG/PNG to WebP (smaller file size)
- Creates multiple sizes (thumbnail, medium, large)
- Preserves folder structure
- Generates width/height attributes for HTML

### 2. Schema Generation (`generate_schema.py`)
```
Input:  Config file with business info + list of services
Output: Updated schema-business.html module with current data
        Individual schema for each video project page
```

**What it does:**
- Maintains consistent LocalBusiness schema
- Generates VideoObject schema for each video project
- Updates review count, ratings from a config file
- Ensures NAP (Name, Address, Phone) consistency

### 3. Sitemap Generation (`generate_sitemap.py`)
```
Input:  All files in output/ folder
Output: output/sitemap.xml with all pages, lastmod dates, priorities
```

**What it does:**
- Scans output folder for all HTML files
- Sets priority based on page type (homepage=1.0, projects=0.7)
- Updates lastmod dates automatically
- Validates URL structure

---

## Your Workflow

### Making a Site-Wide Change (e.g., update phone number)

**Current process:**
1. Open each of 19 HTML files
2. Find and replace phone number
3. Hope you didn't miss any
4. Commit and push

**New process:**
1. Edit `src/modules/footer.html` (one file)
2. Run `python scripts/build.py`
3. Commit and push

### Adding a New Video Project Page

**Current process:**
1. Duplicate an existing page
2. Manually update content, videos, schema
3. Update navigation on all pages
4. Update sitemap manually

**New process:**
1. Create `src/pages/video/newproject.html` with just the unique content
2. Run `python scripts/build.py`
3. Sitemap updates automatically
4. Commit and push

---

## Local + GitHub Workflow

```
Your Mac                          GitHub                    Netlify
─────────────────────────────────────────────────────────────────────
src/ (you edit)          →   pushed to repo      →
scripts/ (automation)    →   pushed to repo      →
output/ (generated)      →   pushed to repo      →   serves output/
```

**Recommended: Build locally, push output**
- You run Python scripts on your Mac
- Push the `output/` folder to GitHub
- Netlify serves it

---

## SEO Benefits of This Approach

### 1. Consistency Across All Pages
When Google crawls the site, every page has:
- Proper schema markup (LocalBusiness, Service, FAQPage)
- Consistent navigation structure
- Same footer with contact info, NAP (Name, Address, Phone)

**Why it matters:** Google trusts sites with consistent, well-structured data.

### 2. Scalable Location/Service Pages
Python scripts can generate location-specific pages programmatically:
```python
locations = ['st-augustine', 'jacksonville', 'palm-coast']
services = ['corporate-video', 'event-coverage', 'brand-story']

for location in locations:
    for service in services:
        generate_page(location, service)
```

### 3. Instant Site-Wide Updates
Change the phone number in `modules/footer.html` → rebuild → every page updates.

**Why it matters:** NAP consistency is critical for local SEO.

### 4. Automated Image SEO
Python can:
- Generate descriptive alt text from folder names/EXIF data
- Create proper file names (`st-augustine-corporate-video.webp` vs `IMG_4532.jpg`)
- Build structured image sitemaps
- Ensure all images have width/height attributes

### 5. Schema Markup at Scale
Every service page gets proper structured data automatically.

### 6. Internal Linking Structure
Python can automatically:
- Link related project pages
- Add "related services" sections
- Build breadcrumb navigation
- Ensure no orphan pages

---

## Implementation Steps (When Ready)

1. **Create module files** by extracting common elements from current HTML
2. **Write Python scripts** for building, image optimization, schema generation
3. **Set up folder structure** in local directory
4. **Create README** with commands to run
5. **Test locally** before pushing to GitHub
6. **Update Netlify config** to serve from output folder

---

## Reference

- Inspired by: robfutrell.com (213 pages managed with similar system)
- Tools: Python, HTML modules, Netlify
- Source: Conversation with Claude Code, February 2026
