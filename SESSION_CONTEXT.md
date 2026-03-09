# Session Context - Squarespace Cleanup for firstsightfilms.com

## Project Location
- Local: `/Users/diegosmbp/Downloads/diegos first script/downloaded_site`
- GitHub: https://github.com/FirstSightFilms/firstsightfilms-website
- Live: https://www.firstsightfilms.com

---

## Latest Session (March 2026) - Modular Build System & Header Redesign

### What Was Built

#### 1. Modular Build System
Created a Python-based build system inspired by robfutrell.com:

**Directory Structure:**
```
downloaded_site/
├── src/
│   ├── modules/
│   │   └── header.html      # Reusable header component
│   ├── pages/
│   │   ├── index.html       # Homepage template
│   │   ├── aboutus/
│   │   ├── contact/
│   │   ├── photo/
│   │   ├── portfolio/
│   │   └── video/           # Includes all video subpages
│   └── css/
│       └── header.css       # Header styles
├── scripts/
│   ├── build.py             # Main build script
│   └── migrate_pages.py     # Migration script for existing pages
└── output/                   # Generated site (serve this folder)
```

**How It Works:**
1. Pages in `src/pages/` use `{{header}}` placeholder
2. `build.py` replaces placeholders with module content
3. Output goes to `output/` folder
4. Run: `python3 scripts/build.py`

#### 2. New Clean Header
Replaced Squarespace header (~21,000 chars per page) with clean modular header (~2,000 chars):

**Features:**
- Centered logo with SEO-optimized filename: `first-sight-films-logo-st-augustine-fl.png`
- Tagline: "ST. AUGUSTINE VIDEO & PHOTO PRODUCTION"
- Hamburger menu on all screen sizes (no horizontal nav)
- Dropdown menu with: Portfolio (Video, Photo), About, Let's Talk (CTA)
- Yellow CTA button (#f4c057) matching logo color

**Header Files:**
- `src/modules/header.html` - HTML structure
- `src/css/header.css` - All header styling (also copied to `css/header.css`)

#### 3. Homepage Above-the-Fold Copy
Updated based on StoryBrand framework and ICP research:

- **H1:** "St. Augustine Video & Photo Production"
- **Subhead:** "Stop scrambling for content. We've got it."
- **CTA:** "Let's Talk"

#### 4. Body Class Cleanup (Homepage Only)
Reduced homepage `<body class="...">` from 5,857 characters (~120 classes) to:
```html
<body class="page-home">
```

### Commands to Run

```bash
# Navigate to project
cd "/Users/diegosmbp/Downloads/diegos first script/downloaded_site"

# Build all pages
python3 scripts/build.py

# Start dev server on output folder
cd output && npx serve -p 3001

# View site
open http://localhost:3001
```

### Key Styling Values (Header)

| Element | Value |
|---------|-------|
| Logo height | 90px desktop, 63px mobile |
| Tagline font | 1rem, weight 550, letter-spacing 0.1em, color #666 |
| Menu items | 1rem, weight 550, letter-spacing 0.1em, color #666 |
| CTA button | Background #f4c057, white text, bold |

### What's Left To Do

1. **Clean up body class** on remaining pages (only homepage done)
2. **Clean up `<head>` section** - still has Squarespace bloat
3. **Review homepage content** below the fold
4. **Commit changes to git** when ready
5. **Deploy to Netlify** (output folder should be deployed)

---

## Previous Session - Initial Cleanup

### 1. Removed Squarespace Bloat (Commit 6a02a42)
- Removed ~36KB `SQUARESPACE_CONTEXT` JSON blob from all 19 HTML files
- Removed Squarespace performance scripts and sqspcdn button components
- Updated social meta images to use local paths
- Updated schema.org images to local paths
- Replaced Squarespace favicon with local logo
- Deleted unused `/cart/` page

### 2. Fixed Homepage Video (Commits f3f5731, 9edd70c)
- Original Squarespace native video player broke after removing scripts
- Added HLS.js library to handle the HLS stream
- Video location in code: `index.html` around line 2096

## Key Video Details
- Video ID: `3587b48b-6519-4d1a-8d6e-6c83c6ccb8d3`
- HLS Playlist: `https://video.squarespace-cdn.com/content/v1/67181a4e7af7e4192dd7b946/3587b48b-6519-4d1a-8d6e-6c83c6ccb8d3/playlist.m3u8`

## Git Commits (Previous)
```
9edd70c Fix video playback using HLS.js for Squarespace HLS stream
f3f5731 Fix homepage video: replace Squarespace native player with HTML5 video
6a02a42 Remove Squarespace bloat for major performance improvement
```

---

## Notes for Next Session

- Always run `python3 scripts/build.py` after making changes to `src/`
- Dev server should point to `output/` folder, not root
- Header changes: edit `src/modules/header.html` and `src/css/header.css`, then rebuild
- To migrate a new page: add to `src/pages/` with `{{header}}` placeholder
