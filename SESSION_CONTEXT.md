# Session Context - Squarespace Cleanup for firstsightfilms.com

## Project Location
- Local: `/Users/diegosmbp/Downloads/diegos first script/downloaded_site`
- GitHub: https://github.com/FirstSightFilms/firstsightfilms-website
- Live: https://www.firstsightfilms.com
- Dev Server: http://localhost:3001 (serves from `output/` folder)

---

## Latest Session (March 9, 2026) - Header Redesign & SEO URLs

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

### Making Changes
1. Edit files in `/output/` folder (this is the live dev site)
2. Test on http://localhost:3001
3. When ready, commit and push to GitHub
4. Netlify auto-deploys from `output/` folder

### Starting Dev Server
```bash
cd "/Users/diegosmbp/Downloads/diegos first script/downloaded_site/output"
npx serve -p 3001
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

- **Dev server runs from `output/`** - all changes should be made there
- **Netlify serves from `output/`** - configured via netlify.toml
- **Video background still uses YouTube** - consider switching to self-hosted MP4
- **Modular build system (`src/`, `scripts/`)** exists but not actively used - changes made directly to `output/`
