# Session Context - firstsightfilms.com

## Project Location
- Local: `/Users/diegosmbp/Downloads/diegos first script/downloaded_site`
- GitHub: https://github.com/FirstSightFilms/firstsightfilms-website
- Live: https://www.firstsightfilms.com
- Dev Server: `python3 -m http.server 8000 --directory output`

---

## Latest Session (March 15, 2026) - Homepage Redesign & Content Updates

### Changes Made
- Added portfolio-grid module (8 video projects)
- Added "Why St. Augustine?" section with local history
- Rebuilt photography page clean (removed Squarespace bloat)
- Updated all buttons to gold (#f4c057)
- Matched background colors across About, Portfolio, FAQ sections
- Updated portfolio images with SEO/GEO alt text (Fort Mose Jazz & Blues Festival)
- Fixed build script regex to support hyphenated module names
- Updated About section text, FAQ heading

### Current URL Structure
| Page | URL |
|------|-----|
| Video Production | `/st-augustine-video-production/` |
| Photography | `/st-augustine-photography/` |
| Corporate Video | `/corporate-video-st-augustine/` |
| About | `/aboutus/` |
| Contact | `/contact/` |

---

## Session History (March 9, 2026) - Header Redesign & SEO URLs

### Deployed to Netlify (Commit 0f2bfa1)

#### 1. Header Navigation Redesign
- **Removed Portfolio dropdown** - Video and Photo are now separate top-level nav items
- **Removed Home link** from navigation
- **Simplified JavaScript** - removed ~40 lines of dropdown/accordion code, kept only mobile menu toggle
- **Nav structure now:** Video | Photo | About | Let's Talk

#### 2. SEO-Optimized URLs
Changed all URLs to include location keywords:

| Old URL | New URL |
|---------|---------|
| `/video/` | `/st-augustine-jacksonville-video-production/` |
| `/photo/` | `/saint-augustine-jacksonville-photographer/` |

- Renamed all folders to match
- Updated all internal links across all HTML files
- Created `_redirects` file for 301 redirects from old URLs

#### 3. Header Content Updates
- **Tagline:** Changed to two lines:
  - Line 1: "Video Production & Photography"
  - Line 2: "St. Augustine | Jacksonville"
- **Tagline font size:** Increased to 1.05rem
- **Logo filename:** Renamed to `First-Sight-Films-Logo-Video-Production-Photography-St-Augustine-Jacksonville-FL.png`

#### 4. Homepage Content Updates
- **H1:** Changed to "St. Augustine & Jacksonville | Video Production & Photography"
- **H2 "Stop scrambling...":** Increased font size to 200%

#### 5. Netlify Configuration
- Created `netlify.toml` to serve from `output/` folder
- All changes made in `output/` folder for dev testing before deploy

### Files Changed
- `output/` - All HTML files updated with new header, URLs, and content
- `output/css/header.css` - Tagline font size
- `output/_redirects` - 301 redirects for old URLs
- `output/images/` - Logo renamed
- `netlify.toml` - Points Netlify to output/ folder

---

## Development Workflow

### Making Changes (Current - Modular System)
1. Edit source files in `src/pages/` or `src/modules/`
2. Run build: `python3 scripts/build.py`
3. Test on dev server
4. Commit and push to GitHub
5. Netlify auto-deploys from `output/` folder

### Starting Dev Server
```bash
cd "/Users/diegosmbp/Downloads/diegos first script/downloaded_site"
python3 -m http.server 8000 --directory output
```
Then open: http://localhost:8000

### Building the Site
```bash
cd "/Users/diegosmbp/Downloads/diegos first script/downloaded_site"
python3 scripts/build.py
```

### Deploying to Live
```bash
cd "/Users/diegosmbp/Downloads/diegos first script/downloaded_site"
git add -A
git commit -m "Description of changes"
git push origin main
```

---

## Current Site Structure

```
output/
├── index.html                              # Homepage
├── aboutus/index.html
├── contact/index.html
├── portfolio/index.html
├── st-augustine-jacksonville-video-production/
│   ├── index.html                          # Video landing page
│   ├── fortmose/
│   ├── singoutloud2024/
│   ├── staugustineamp/
│   └── ... (13 video project pages)
├── saint-augustine-jacksonville-photographer/
│   └── index.html                          # Photo page
├── css/
│   ├── header.css
│   ├── site_3e6e8161.css
│   └── static_b4ee7412.css
├── images/
└── _redirects
```

---

## Key Styling Values

| Element | Value |
|---------|-------|
| Logo height | 90px desktop, 63px mobile |
| Tagline font | 1.05rem, weight 550, letter-spacing 0.1em, color #666 |
| Menu items | 1rem, weight 550, uppercase, color #666 |
| CTA button (Let's Talk) | Background #000 desktop, #f4c057 mobile |
| H2 "Stop scrambling" | font-size: 200% |

---

## Redirects (_redirects file)

```
/video/*                      → /st-augustine-jacksonville-video-production/:splat
/st-augustine-video-production/* → /st-augustine-jacksonville-video-production/:splat
/photo/*                      → /saint-augustine-jacksonville-photographer/:splat
/st-augustine-photography/*   → /saint-augustine-jacksonville-photographer/:splat
/saint-augustine-photographer/* → /saint-augustine-jacksonville-photographer/:splat
```

---

## Previous Sessions

### March 2026 - Modular Build System
- Created `src/modules/` and `src/pages/` structure
- Built Python build scripts
- Initial header cleanup

### Initial Cleanup
- Removed ~36KB Squarespace bloat from all pages
- Fixed homepage video with HLS.js
- Removed unused cart page

---

## Notes for Next Session

- **Edit `src/`, not `output/`** - output is auto-generated by build.py
- **Run `python3 scripts/build.py`** after making changes
- **Netlify serves from `output/`** - configured via netlify.toml
- **Modules support hyphens** - e.g., `{{portfolio-grid}}`, `{{why-st-augustine}}`

### Pending Tasks
- Create dedicated pages for `/brand-story-video/` and `/social-media-video/`
- Localize remaining Squarespace CDN images on project pages
- Set up ANTHROPIC_API_KEY for FSF Image Optimizer alt text generation
