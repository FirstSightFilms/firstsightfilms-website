#!/usr/bin/env python3
"""
FSF Site Builder
Combines modules + pages into complete HTML files.

Usage:
    python scripts/build.py --watch     # Watch mode (recommended) - auto-rebuilds changed files
    python scripts/build.py --page X    # Build only specific page
    python scripts/build.py --all       # Full rebuild of entire site

Directory structure:
    src/modules/    - Reusable components (header.html, footer.html, etc.)
    src/pages/      - Page templates with {{module}} placeholders
    output/         - Generated HTML files (served by Netlify)
"""

import os
import re
import csv
import json
import shutil
import argparse
import time
from pathlib import Path
from datetime import datetime

# Try to import watchdog for watch mode
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Paths
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
MODULES_DIR = SRC_DIR / "modules"
PAGES_DIR = SRC_DIR / "pages"
FAQS_DIR = SRC_DIR / "faqs"
REVIEWS_DIR = SRC_DIR / "reviews"
CONFIG_DIR = SRC_DIR / "config"
OUTPUT_DIR = BASE_DIR / "output"

# Protected pages - these will NEVER be overwritten by the build script
# Edit these directly in output/ - they bypass the build system
PROTECTED_PAGES = [
    # Homepage now builds from src/pages/index.html via the shared modules
    # (footer module). Re-add "index.html" here to bypass the build again.
]

# Global page config (populated by load_page_config)
PAGE_CONFIG = {}

# Assets to copy from src to output
ASSETS_TO_COPY = ["images", "js", "video"]

# CSS directory in src
SRC_CSS_DIR = SRC_DIR / "css"

# Fonts directory in src
SRC_FONTS_DIR = SRC_DIR / "fonts"

# Global image manifest (populated by load_image_manifests)
IMAGE_MANIFEST = {}

# Blog paths
BLOG_DIR = SRC_DIR / "blog"
BLOG_ARTICLES_DIR = BLOG_DIR / "articles"
BLOG_CONTENT_DIR = BLOG_DIR / "content"
BLOG_CONFIG_DIR = BLOG_DIR / "config"

# Global blog data (populated by load_blog_data)
BLOG_ARTICLES = []
BLOG_CATEGORIES = {}
BLOG_AUTHORS = {}


def load_image_manifests():
    """Load all _manifest.csv files from output/images/*/ into a lookup dict."""
    global IMAGE_MANIFEST
    IMAGE_MANIFEST = {}

    images_dir = OUTPUT_DIR / "images"
    if not images_dir.exists():
        return IMAGE_MANIFEST

    # Find all _manifest.csv files
    for manifest_file in images_dir.glob("**/_manifest.csv"):
        try:
            with open(manifest_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    filename = row.get('filename', '')
                    if filename:
                        # Key by filename (e.g., "image-name-large.webp")
                        IMAGE_MANIFEST[filename] = {
                            'alt': row.get('alt', ''),
                            'width': row.get('width', ''),
                            'height': row.get('height', ''),
                            'original': row.get('original', ''),
                            'size': row.get('size', '')
                        }
        except Exception as e:
            print(f"  Warning: Error reading {manifest_file}: {e}")

    return IMAGE_MANIFEST


def inject_image_attributes(html_content):
    """Find <img> tags and inject alt/width/height from manifest if missing."""
    if not IMAGE_MANIFEST:
        return html_content

    def replace_img(match):
        img_tag = match.group(0)

        # Extract src attribute
        src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
        if not src_match:
            return img_tag

        src = src_match.group(1)

        # Get filename from src path (e.g., "/images/folder/name.webp" -> "name.webp")
        filename = Path(src).name

        # Look up in manifest
        if filename not in IMAGE_MANIFEST:
            return img_tag

        manifest_data = IMAGE_MANIFEST[filename]

        # Check what's already present
        has_alt = re.search(r'\balt=["\']', img_tag) is not None
        has_width = re.search(r'\bwidth=["\']', img_tag) is not None
        has_height = re.search(r'\bheight=["\']', img_tag) is not None
        has_loading = re.search(r'\bloading=["\']', img_tag) is not None

        # Build attributes to add
        attrs_to_add = []

        if not has_alt and manifest_data['alt']:
            # Escape quotes in alt text
            alt_text = manifest_data['alt'].replace('"', '&quot;')
            attrs_to_add.append(f'alt="{alt_text}"')

        if not has_width and manifest_data['width']:
            attrs_to_add.append(f'width="{manifest_data["width"]}"')

        if not has_height and manifest_data['height']:
            attrs_to_add.append(f'height="{manifest_data["height"]}"')

        if not has_loading:
            attrs_to_add.append('loading="lazy"')

        if not attrs_to_add:
            return img_tag

        # Insert attributes before the closing > or />
        attrs_str = ' ' + ' '.join(attrs_to_add)

        if img_tag.rstrip().endswith('/>'):
            # Self-closing tag
            return re.sub(r'\s*/>', f'{attrs_str} />', img_tag)
        else:
            # Regular tag
            return re.sub(r'>', f'{attrs_str}>', img_tag, count=1)

    # Match <img ...> tags (handles multiline)
    img_pattern = r'<img\s[^>]*>'
    return re.sub(img_pattern, replace_img, html_content, flags=re.IGNORECASE | re.DOTALL)


def load_page_config():
    """Load page configuration from pages.json."""
    global PAGE_CONFIG
    config_file = CONFIG_DIR / "pages.json"

    if not config_file.exists():
        print(f"  Warning: Page config not found: {config_file}")
        return {}

    try:
        PAGE_CONFIG = json.loads(config_file.read_text(encoding="utf-8"))
        print(f"  Loaded config for {len(PAGE_CONFIG)} pages")
        return PAGE_CONFIG
    except json.JSONDecodeError as e:
        print(f"  Error parsing pages.json: {e}")
        return {}


def load_hero(page_name, modules):
    """Generate hero HTML from template and page config."""
    if page_name not in PAGE_CONFIG:
        print(f"  Warning: No config found for page: {page_name}")
        return ""

    # Load hero template
    hero_template_file = MODULES_DIR / "hero.html"
    if not hero_template_file.exists():
        print(f"  Warning: Hero template not found")
        return ""

    hero_html = hero_template_file.read_text(encoding="utf-8")
    config = PAGE_CONFIG[page_name]

    # Replace basic placeholders
    hero_html = hero_html.replace("{{hero-h1}}", config.get("h1", ""))
    hero_html = hero_html.replace("{{hero-tagline}}", config.get("tagline", ""))
    hero_html = hero_html.replace("{{hero-description}}", config.get("description", ""))

    # Handle optional description2
    desc2 = config.get("description2", "")
    if desc2:
        hero_html = hero_html.replace("{{hero-description2}}", f'<p class="hero-desc">{desc2}</p>')
    else:
        hero_html = hero_html.replace("{{hero-description2}}", "")

    # Handle CTA button
    cta_text = config.get("cta_text", "")
    cta_url = config.get("cta_url", "")
    if cta_text and cta_url:
        cta_html = f'<a href="{cta_url}" class="btn btn-primary hero-cta">{cta_text}</a>'
        hero_html = hero_html.replace("{{hero-cta}}", cta_html)
    else:
        hero_html = hero_html.replace("{{hero-cta}}", "")

    # Handle media (video or image)
    hero_video = config.get("hero_video", "")
    hero_image = config.get("hero_image", "")
    hero_alt = config.get("hero_alt", "First Sight Films")

    if hero_video:
        # Video with image fallback
        media_html = f'''<video id="heroVideo" autoplay muted loop playsinline poster="{hero_image}">
        <source src="{hero_video}" type="video/mp4">
        <img src="{hero_image}" alt="{hero_alt}">
      </video>
      <button class="video-sound-toggle" id="soundToggle" aria-label="Toggle sound">
        <span class="sound-off">&#128263;</span>
        <span class="sound-on">&#128266;</span>
      </button>'''
        media_mobile_html = f'''<video autoplay muted loop playsinline poster="{hero_image}">
        <source src="{hero_video}" type="video/mp4">
        <img src="{hero_image}" alt="{hero_alt}">
      </video>'''
    else:
        # Image only
        media_html = f'<img src="{hero_image}" alt="{hero_alt}">'
        media_mobile_html = f'<img src="{hero_image}" alt="{hero_alt}">'

    hero_html = hero_html.replace("{{hero-media}}", media_html)
    hero_html = hero_html.replace("{{hero-media-mobile}}", media_mobile_html)

    print(f"  Generated hero: {page_name}")
    return hero_html


def load_hero_service(page_name, modules):
    """Generate service hero HTML from template and page config."""
    if page_name not in PAGE_CONFIG:
        print(f"  Warning: No config found for page: {page_name}")
        return ""

    # Load hero-service template
    hero_template_file = MODULES_DIR / "hero-service.html"
    if not hero_template_file.exists():
        print(f"  Warning: Hero-service template not found")
        return ""

    hero_html = hero_template_file.read_text(encoding="utf-8")
    config = PAGE_CONFIG[page_name]

    # Replace placeholders
    hero_html = hero_html.replace("{{hero-label}}", config.get("label", "St. Augustine & Jacksonville"))
    hero_html = hero_html.replace("{{hero-h1}}", config.get("h1", ""))
    hero_html = hero_html.replace("{{hero-tagline}}", config.get("tagline", ""))
    hero_html = hero_html.replace("{{hero-description}}", config.get("description", ""))

    # Handle CTA button
    cta_text = config.get("cta_text", "")
    cta_url = config.get("cta_url", "")
    if cta_text and cta_url:
        cta_html = f'<a href="{cta_url}" class="btn btn-accent">{cta_text}</a>'
        hero_html = hero_html.replace("{{hero-cta}}", cta_html)
    else:
        hero_html = hero_html.replace("{{hero-cta}}", "")

    print(f"  Generated hero-service: {page_name}")
    return hero_html


def load_modules():
    """Load all module files into a dictionary."""
    modules = {}
    if not MODULES_DIR.exists():
        print(f"Warning: Modules directory not found: {MODULES_DIR}")
        return modules

    for module_file in MODULES_DIR.glob("*.html"):
        module_name = module_file.stem  # filename without .html
        modules[module_name] = module_file.read_text(encoding="utf-8")
        print(f"  Loaded module: {module_name}")

    return modules


def load_faq_data(faq_name):
    """Load FAQ JSON data."""
    faq_file = FAQS_DIR / f"{faq_name}.json"

    if not faq_file.exists():
        print(f"  Warning: FAQ file not found: {faq_file}")
        return None

    try:
        return json.loads(faq_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  Error parsing FAQ JSON {faq_name}: {e}")
        return None


def _faq_slug(text):
    """Make a URL-safe anchor id from a category name."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _render_faq_items(items):
    """Render a list of FAQ question dicts as accordion <details> HTML."""
    parts = ['    <div class="faq-list">']
    for item in items:
        question = item.get("question", "")
        answer = item.get("answer", "")
        parts.append(f'''        <details class="faq-item">
          <summary class="faq-question">{question}</summary>
          <div class="faq-answer">
            {answer}
          </div>
        </details>''')
    parts.append('      </div>')
    return '\n'.join(parts)


def load_faq(faq_name):
    """Load FAQ JSON and generate HTML.

    If any question carries a "category" field, render grouped sections with a
    scannable jump-nav. Otherwise render a single flat list (backward compatible).
    """
    faq_data = load_faq_data(faq_name)
    if not faq_data:
        return ""

    questions = faq_data.get("questions", [])

    # No categories -> original flat list behavior
    if not any(q.get("category") for q in questions):
        return _render_faq_items(questions)

    # Group by category, preserving first-seen order
    groups = []
    index = {}
    for q in questions:
        cat = q.get("category", "More Questions")
        if cat not in index:
            index[cat] = len(groups)
            groups.append((cat, []))
        groups[index[cat]][1].append(q)

    def esc(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    parts = ['<div class="faq-grouped">']
    parts.append('      <nav class="faq-jump" aria-label="Jump to FAQ category">')
    for cat, _items in groups:
        parts.append(f'        <a href="#faq-g-{_faq_slug(cat)}">{esc(cat)}</a>')
    parts.append('      </nav>')
    for cat, items in groups:
        parts.append(f'      <div class="faq-group" id="faq-g-{_faq_slug(cat)}">')
        parts.append(f'        <h3 class="faq-group-title">{esc(cat)}</h3>')
        parts.append(_render_faq_items(items))
        parts.append('      </div>')
    parts.append('    </div>')
    return '\n'.join(parts)


def load_faq_schema(faq_name):
    """Load FAQ JSON-LD schema for <head>."""
    faq_data = load_faq_data(faq_name)
    if not faq_data or "schema" not in faq_data:
        return ""

    schema_json = json.dumps(faq_data["schema"], indent=2)
    return f'<script type="application/ld+json">\n{schema_json}\n</script>'


def load_reviews():
    """Load reviews JSON and generate testimonials carousel HTML."""
    reviews_file = REVIEWS_DIR / "testimonials.json"

    if not reviews_file.exists():
        print(f"  Warning: Reviews file not found: {reviews_file}")
        return ""

    try:
        data = json.loads(reviews_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  Error parsing reviews JSON: {e}")
        return ""

    title = data.get("title", "What Our Clients Say")
    subtitle = data.get("subtitle", "")
    reviews = data.get("reviews", [])

    if not reviews:
        return ""

    # Build review cards HTML
    cards_html = []
    for i, review in enumerate(reviews):
        author = review.get("author", "Anonymous")
        initial = author[0].upper() if author else "A"
        photo = review.get("photo")
        date = review.get("date", "")
        text = review.get("text", "")
        url = review.get("url", "")
        rating = review.get("rating", 5)

        stars = "★" * rating

        # Avatar HTML
        if photo:
            avatar_class = "reviewer-avatar has-photo"
            avatar_html = f'''<img src="{photo}" alt="{author}" class="reviewer-photo" width="48" height="48" loading="lazy">
                <span class="reviewer-initial" data-letter="{initial}">{initial}</span>'''
        else:
            avatar_class = "reviewer-avatar"
            avatar_html = f'<span class="reviewer-initial" data-letter="{initial}">{initial}</span>'

        # Link HTML
        link_html = f'<a href="{url}" target="_blank" rel="noopener" class="review-link">Read on Google</a>' if url else ""

        # Truncate long quotes for display
        max_chars = 280
        is_long = len(text) > max_chars
        truncated_class = " truncated" if is_long else ""
        expand_btn_html = '<button class="review-expand" aria-label="Read more">Read more</button>' if is_long else ""

        card = f'''
          <div class="review-card" data-index="{i}">
            <div class="review-author-header">
              <div class="{avatar_class}">
                {avatar_html}
              </div>
              <div class="reviewer-info">
                <span class="review-author">{author}</span>
                <span class="review-stars">{stars}</span>
              </div>
            </div>
            <div class="review-quote-wrapper{truncated_class}">
              <blockquote class="review-quote">"{text}"</blockquote>
              {expand_btn_html}
            </div>
            <div class="review-footer">
              <span class="review-date">{date}</span>
              {link_html}
            </div>
          </div>'''
        cards_html.append(card)

    total_reviews = len(reviews)
    total_pages_desktop = (total_reviews + 2) // 3  # 3 cards per page on desktop

    html = f'''<!-- Testimonials Section -->
<section class="section-testimonials" id="reviews">
  <div class="testimonials-container">
    <div class="testimonials-header">
      <h2>{title}</h2>
      <p>{subtitle}</p>
    </div>

    <div class="review-carousel-wrapper">
      <button class="review-nav review-nav-side prev" aria-label="Previous reviews">&#8249;</button>

      <div class="review-cards-viewport">
        <div class="review-cards-track">
{''.join(cards_html)}
        </div>
      </div>

      <button class="review-nav review-nav-side next" aria-label="Next reviews">&#8250;</button>
    </div>

    <div class="review-mobile-nav">
      <button class="review-nav prev" aria-label="Previous reviews">&#8249;</button>
      <div class="review-pagination">
        <span class="current-page">1</span> / <span class="total-pages">{total_reviews}</span>
      </div>
      <button class="review-nav next" aria-label="Next reviews">&#8250;</button>
    </div>

    <div class="review-pagination review-pagination-desktop">
      <span class="current-page">1</span> / <span class="total-pages">{total_pages_desktop}</span>
    </div>

    <div class="review-cta">
      <a href="{data.get('google_url', 'https://www.google.com/maps/place/First+Sight+Films/')}" target="_blank" rel="noopener" class="review-cta-link">See more of our reviews</a>
    </div>

  </div>
</section>
<script src="/js/review-carousel.js" defer></script>'''

    return html


ASSET_VERSION = None


def get_asset_version():
    """Content hash of all CSS/JS files — used to cache-bust asset links. Computed once."""
    global ASSET_VERSION
    if ASSET_VERSION is None:
        import hashlib
        h = hashlib.md5()
        for d in [SRC_CSS_DIR, SRC_DIR / "js"]:
            if d.exists():
                for f in sorted(d.rglob("*")):
                    if f.is_file() and f.suffix in (".css", ".js"):
                        h.update(f.read_bytes())
        ASSET_VERSION = h.hexdigest()[:8]
    return ASSET_VERSION


def apply_cache_busting(html_content):
    """Append ?v=<hash> to local /css/*.css and /js/*.js links so browsers refetch on change."""
    version = get_asset_version()
    if not version:
        return html_content

    def add_version(match):
        attr, path = match.group(1), match.group(2)
        sep = "&" if "?" in path else "?"
        return f'{attr}="{path}{sep}v={version}"'

    return re.sub(r'(href|src)="(/(?:css|js)/[^"]+\.(?:css|js))"', add_version, html_content)


def process_page(page_content, modules):
    """Replace {{module_name}}, {{hero:page}}, {{faq:page-name}}, {{faq-schema:page-name}}, and {{reviews}} placeholders."""

    def replace_module(match):
        module_name = match.group(1).strip()
        # Special handling for reviews
        if module_name == "reviews":
            reviews_html = load_reviews()
            if reviews_html:
                print(f"  Loaded reviews from JSON")
                return reviews_html
            else:
                return match.group(0)
        if module_name in modules:
            return modules[module_name]
        else:
            print(f"  Warning: Module not found: {module_name}")
            return match.group(0)  # Keep original if not found

    def replace_faq(match):
        faq_name = match.group(1).strip()
        faq_html = load_faq(faq_name)
        if faq_html:
            print(f"  Loaded FAQ: {faq_name}")
            return faq_html
        else:
            return match.group(0)  # Keep original if not found

    def replace_faq_schema(match):
        faq_name = match.group(1).strip()
        schema_html = load_faq_schema(faq_name)
        if schema_html:
            print(f"  Loaded FAQ schema: {faq_name}")
            return schema_html
        else:
            return ""  # Return empty if no schema

    def replace_hero(match):
        page_name = match.group(1).strip()
        hero_html = load_hero(page_name, modules)
        if hero_html:
            return hero_html
        else:
            return match.group(0)  # Keep original if not found

    def replace_hero_service(match):
        page_name = match.group(1).strip()
        hero_html = load_hero_service(page_name, modules)
        if hero_html:
            return hero_html
        else:
            return match.group(0)  # Keep original if not found

    # Match {{hero:page-name}} pattern first
    hero_pattern = r"\{\{hero:([a-zA-Z0-9_-]+)\}\}"
    page_content = re.sub(hero_pattern, replace_hero, page_content)

    # Match {{hero-service:page-name}} pattern
    hero_service_pattern = r"\{\{hero-service:([a-zA-Z0-9_-]+)\}\}"
    page_content = re.sub(hero_service_pattern, replace_hero_service, page_content)

    # Match {{faq-schema:page-name}} pattern
    faq_schema_pattern = r"\{\{faq-schema:([a-zA-Z0-9_-]+)\}\}"
    page_content = re.sub(faq_schema_pattern, replace_faq_schema, page_content)

    # Match {{faq:page-name}} pattern
    faq_pattern = r"\{\{faq:([a-zA-Z0-9_-]+)\}\}"
    page_content = re.sub(faq_pattern, replace_faq, page_content)

    # Match {{module_name}} pattern (supports hyphens in module names)
    pattern = r"\{\{([a-zA-Z0-9_-]+)\}\}"
    page_content = re.sub(pattern, replace_module, page_content)

    # Auto-inject image attributes (alt, width, height, loading) from manifests
    page_content = inject_image_attributes(page_content)

    # Cache-bust local CSS/JS links so browsers refetch them when they change
    page_content = apply_cache_busting(page_content)

    return page_content


def inject_canonical(html_content, url_path):
    """Inject canonical tag into the page head."""
    site_url = "https://www.firstsightfilms.com"
    canonical_url = site_url + url_path
    canonical_tag = f'<link rel="canonical" href="{canonical_url}">'

    # Insert before </head>
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', f'{canonical_tag}\n</head>')

    return html_content


def fix_og_url(html_content, url_path):
    """Replace generic og:url with the correct page URL."""
    site_url = "https://www.firstsightfilms.com"
    correct_url = site_url + url_path

    # Replace the hardcoded homepage og:url with the correct page URL
    html_content = re.sub(
        r'<meta property="og:url" content="https://www\.firstsightfilms\.com/?">',
        f'<meta property="og:url" content="{correct_url}">',
        html_content
    )

    return html_content


def fix_blog_og_tags(html_content):
    """Remove duplicate OG tags from blog articles.

    The head module includes default OG tags, but blog articles have their own
    article-specific OG tags. This function removes the default ones so crawlers
    find the article-specific tags first.
    """
    # Remove default og:title (keep article-specific one)
    html_content = re.sub(
        r'<meta property="og:title" content="St\. Augustine Video Production \| First Sight Films">\n?',
        '',
        html_content
    )

    # Remove default og:description (keep article-specific one)
    html_content = re.sub(
        r'<meta property="og:description" content="Professional video production and photography for St\. Augustine and Northeast Florida businesses\.">\n?',
        '',
        html_content
    )

    # Remove default og:image (keep article-specific one)
    html_content = re.sub(
        r'<meta property="og:image" content="https://www\.firstsightfilms\.com/images/fsf-social-share\.png">\n?',
        '',
        html_content
    )

    # Remove default og:type website (article template has og:type article)
    html_content = re.sub(
        r'<meta property="og:type" content="website">\n?',
        '',
        html_content
    )

    # Remove default twitter tags (they'll use OG as fallback)
    html_content = re.sub(
        r'<meta name="twitter:title" content="St\. Augustine Video Production \| First Sight Films">\n?',
        '',
        html_content
    )
    html_content = re.sub(
        r'<meta name="twitter:description" content="Professional video production and photography for St\. Augustine and Northeast Florida businesses\.">\n?',
        '',
        html_content
    )
    html_content = re.sub(
        r'<meta name="twitter:image" content="https://www\.firstsightfilms\.com/images/fsf-social-share\.png">\n?',
        '',
        html_content
    )

    return html_content


def build_pages(modules, page_filter=None, skip_protected=True):
    """Process page templates and output complete HTML.

    Args:
        modules: Dict of loaded module HTML
        page_filter: Optional string to filter which pages to build (e.g., "st-augustine-photography")
        skip_protected: If True, skip pages in PROTECTED_PAGES list
    """
    if not PAGES_DIR.exists():
        print(f"Warning: Pages directory not found: {PAGES_DIR}")
        return

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    for page_file in PAGES_DIR.glob("**/*.html"):
        # Get relative path for nested pages (e.g., video/fortmose.html)
        relative_path = page_file.relative_to(PAGES_DIR)

        # Skip template files (prefixed with _)
        if page_file.name.startswith("_"):
            print(f"  Skipped template: {relative_path}")
            continue

        # Skip protected pages (like homepage)
        if skip_protected and relative_path.name in PROTECTED_PAGES:
            if relative_path.parent == Path("."):
                print(f"  Protected (skipped): {relative_path}")
                continue

        # Filter to specific page if requested
        if page_filter:
            # Match against folder name or file stem
            page_identifier = relative_path.parent.as_posix() if relative_path.name == "index.html" else relative_path.stem
            if page_filter not in str(relative_path) and page_filter != page_identifier:
                continue  # Skip silently - not the page we're looking for

        # Read page template
        page_content = page_file.read_text(encoding="utf-8")

        # Process modules
        processed_content = process_page(page_content, modules)

        # Determine output path and URL path
        if relative_path.name == "index.html":
            # Root or subfolder index stays as-is
            output_path = OUTPUT_DIR / relative_path
            if relative_path.parent == Path("."):
                url_path = "/"
            else:
                url_path = "/" + relative_path.parent.as_posix() + "/"
        else:
            # Other pages become folder/index.html for clean URLs
            # e.g., about.html -> about/index.html
            folder_name = relative_path.stem
            parent = relative_path.parent
            output_path = OUTPUT_DIR / parent / folder_name / "index.html"
            url_path = "/" + (parent / folder_name).as_posix() + "/"

        # Inject canonical tag
        processed_content = inject_canonical(processed_content, url_path)

        # Fix og:url to match page URL
        processed_content = fix_og_url(processed_content, url_path)

        # Create parent directories
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write output
        output_path.write_text(processed_content, encoding="utf-8")
        print(f"  Built: {relative_path} -> {output_path.relative_to(OUTPUT_DIR)}")


def copy_assets():
    """Copy static assets (images, js) to output directory.

    For images: merges source into output (preserves optimized images with manifests).
    For other assets: replaces entirely.
    """
    for asset_name in ASSETS_TO_COPY:
        src_path = SRC_DIR / asset_name
        dest_path = OUTPUT_DIR / asset_name

        if src_path.exists():
            if asset_name == "images":
                # Merge images - don't delete existing (preserves optimized images)
                dest_path.mkdir(parents=True, exist_ok=True)
                for item in src_path.iterdir():
                    dest_item = dest_path / item.name
                    if item.is_file():
                        shutil.copy2(item, dest_item)
                    elif item.is_dir() and not dest_item.exists():
                        # Only copy subdirs that don't already exist
                        shutil.copytree(item, dest_item)
                print(f"  Merged: {asset_name}/ (preserving optimized images)")
            else:
                # Other assets: replace entirely
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
                print(f"  Copied: {asset_name}/")


def minify_css(css_content):
    """Minify CSS by removing comments, whitespace, and unnecessary characters."""
    # Remove CSS comments
    css_content = re.sub(r'/\*[\s\S]*?\*/', '', css_content)
    # Remove newlines and extra whitespace
    css_content = re.sub(r'\s+', ' ', css_content)
    # Remove spaces around special characters
    css_content = re.sub(r'\s*([{}:;,>~+])\s*', r'\1', css_content)
    # Remove trailing semicolons before closing braces
    css_content = re.sub(r';}', '}', css_content)
    # Remove leading/trailing whitespace
    css_content = css_content.strip()
    return css_content


def copy_css():
    """Copy and minify CSS from src/css to output/css."""
    dest_path = OUTPUT_DIR / "css"

    if SRC_CSS_DIR.exists():
        if dest_path.exists():
            shutil.rmtree(dest_path)
        dest_path.mkdir(parents=True, exist_ok=True)

        total_original = 0
        total_minified = 0

        for css_file in SRC_CSS_DIR.glob("*.css"):
            original_content = css_file.read_text(encoding="utf-8")
            original_size = len(original_content)
            total_original += original_size

            # Skip already minified files
            if css_file.name.endswith('.min.css'):
                minified_content = original_content
            else:
                minified_content = minify_css(original_content)

            minified_size = len(minified_content)
            total_minified += minified_size

            dest_file = dest_path / css_file.name
            dest_file.write_text(minified_content, encoding="utf-8")

        savings = total_original - total_minified
        savings_kb = savings / 1024
        print(f"  Copied and minified: css/ (saved {savings_kb:.1f} KB)")


def copy_fonts():
    """Copy fonts from src/fonts to output/fonts."""
    dest_path = OUTPUT_DIR / "fonts"

    if SRC_FONTS_DIR.exists():
        if dest_path.exists():
            shutil.rmtree(dest_path)
        shutil.copytree(SRC_FONTS_DIR, dest_path)
        print(f"  Copied: fonts/ (from src/fonts)")


def copy_existing_pages():
    """Copy existing HTML pages that aren't yet migrated to src/pages/."""
    # Get list of pages already in src/pages (these will be built, not copied)
    migrated_pages = set()
    if PAGES_DIR.exists():
        for page_file in PAGES_DIR.glob("**/*.html"):
            relative = page_file.relative_to(PAGES_DIR)
            # Convert to folder name (e.g., index.html -> "", about.html -> "about")
            if relative.name == "index.html":
                migrated_pages.add(relative.parent.as_posix())
            else:
                migrated_pages.add((relative.parent / relative.stem).as_posix())

    # Folders to copy from root (these contain index.html)
    page_folders = ["aboutus", "contact", "photo", "portfolio", "video"]

    for folder in page_folders:
        src_path = BASE_DIR / folder
        dest_path = OUTPUT_DIR / folder

        # Skip if already migrated to src/pages/
        if folder in migrated_pages:
            print(f"  Skipped (migrated): {folder}/")
            continue

        if src_path.exists() and src_path.is_dir():
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            print(f"  Copied existing: {folder}/")


def validate_video_references():
    """Scan built HTML for video references and validate they exist.

    Returns:
        tuple: (is_valid, missing_videos, large_videos, warnings)
    """
    print("\n[Validation] Checking video references...")

    missing_videos = []
    large_videos = []  # Files over 100MB (GitHub limit)
    warnings = []
    found_videos = set()

    # Patterns to find video references in HTML
    video_patterns = [
        r'data-video=["\']([^"\']+\.mp4)["\']',  # data-video attributes
        r'<source[^>]+src=["\']([^"\']+\.mp4)["\']',  # <source> tags
        r'<video[^>]+src=["\']([^"\']+\.mp4)["\']',  # <video src> tags
        r'href=["\']([^"\']+\.mp4)["\']',  # Direct video links
    ]

    # Scan all HTML files in output
    for html_file in OUTPUT_DIR.glob("**/*.html"):
        content = html_file.read_text(encoding="utf-8")

        for pattern in video_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for video_path in matches:
                # Normalize path (remove leading slash for file check)
                clean_path = video_path.lstrip("/")
                found_videos.add((video_path, clean_path, html_file))

    # Check each video reference
    checked_paths = set()
    for original_path, clean_path, html_file in found_videos:
        if clean_path in checked_paths:
            continue
        checked_paths.add(clean_path)

        video_file = OUTPUT_DIR / clean_path

        if not video_file.exists():
            missing_videos.append({
                "path": original_path,
                "referenced_in": html_file.relative_to(OUTPUT_DIR),
                "expected_at": video_file
            })
        else:
            # Check file size
            size_bytes = video_file.stat().st_size
            size_mb = size_bytes / (1024 * 1024)

            if size_mb > 100:
                large_videos.append({
                    "path": original_path,
                    "size_mb": round(size_mb, 1),
                    "file": video_file
                })

    # Report results
    total_videos = len(checked_paths)
    print(f"  Found {total_videos} video references in HTML")

    if missing_videos:
        print(f"\n  [ERROR] {len(missing_videos)} MISSING VIDEO(S):")
        for v in missing_videos:
            print(f"    - {v['path']}")
            print(f"      Referenced in: {v['referenced_in']}")

    if large_videos:
        print(f"\n  [WARNING] {len(large_videos)} video(s) exceed GitHub 100MB limit:")
        for v in large_videos:
            print(f"    - {v['path']} ({v['size_mb']} MB)")
        warnings.append(f"{len(large_videos)} videos exceed 100MB - cannot push to GitHub without Git LFS")

    is_valid = len(missing_videos) == 0

    if is_valid and not large_videos:
        print("  All video references valid!")

    return is_valid, missing_videos, large_videos, warnings


def generate_sitemap():
    """Generate sitemap.xml from built pages."""
    site_url = "https://www.firstsightfilms.com"
    today = datetime.now().strftime("%Y-%m-%d")

    # Pages to exclude from sitemap (redirects, old URLs, junk, etc.)
    exclude_patterns = [
        "st-augustine-jacksonville-video-production",  # Redirects to st-augustine-video-production
        "/images/",  # Image directories with HTML snippets
        "google",  # Google verification files
        "_snippets",  # Snippet files
        "saint-augustine-jacksonville-photographer",  # Old page
        "_service-template",  # Template file, not a real page
        "_article-template",  # Blog article template, not a real page
        "/410",  # Error page, not indexable
        "professional-services",  # noindex page — keep out of sitemap (2026-06-08)
        "event-video-st-augustine",  # retired -> 301 to event-video-coverage-st-augustine (2026-06-11)
    ]

    # Priority mapping based on URL depth/importance
    def get_priority(url_path):
        if url_path == "/":
            return "1.0"
        elif url_path in ["/aboutus/", "/contact/", "/st-augustine-video-production/",
                          "/st-augustine-photography/", "/corporate-video-st-augustine/"]:
            return "0.9"
        elif url_path.startswith("/st-augustine-video-production/") and url_path.count("/") == 3:
            return "0.8"  # Project pages
        else:
            return "0.7"

    # Change frequency mapping
    def get_changefreq(url_path):
        if url_path == "/":
            return "weekly"
        elif url_path in ["/aboutus/", "/contact/"]:
            return "monthly"
        else:
            return "monthly"

    # Find all HTML files in output
    urls = []
    for html_file in OUTPUT_DIR.glob("**/*.html"):
        relative_path = html_file.relative_to(OUTPUT_DIR)

        # Convert to URL path
        if relative_path.name == "index.html":
            if relative_path.parent == Path("."):
                url_path = "/"
            else:
                url_path = "/" + relative_path.parent.as_posix() + "/"
        else:
            url_path = "/" + relative_path.with_suffix("").as_posix() + "/"

        # Skip excluded patterns
        if any(pattern in url_path for pattern in exclude_patterns):
            continue

        urls.append({
            "loc": site_url + url_path,
            "lastmod": today,
            "changefreq": get_changefreq(url_path),
            "priority": get_priority(url_path)
        })

    # Sort URLs (homepage first, then alphabetically)
    urls.sort(key=lambda x: (x["loc"] != site_url + "/", x["loc"]))

    # Generate XML
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in urls:
        xml_parts.append("  <url>")
        xml_parts.append(f"    <loc>{url['loc']}</loc>")
        xml_parts.append(f"    <lastmod>{url['lastmod']}</lastmod>")
        xml_parts.append(f"    <changefreq>{url['changefreq']}</changefreq>")
        xml_parts.append(f"    <priority>{url['priority']}</priority>")
        xml_parts.append("  </url>")

    xml_parts.append("</urlset>")

    # Write sitemap
    sitemap_path = OUTPUT_DIR / "sitemap.xml"
    sitemap_path.write_text("\n".join(xml_parts), encoding="utf-8")
    print(f"  Generated sitemap.xml with {len(urls)} URLs")


# =============================================================================
# Blog Functions
# =============================================================================

def load_blog_config():
    """Load blog categories and authors configuration."""
    global BLOG_CATEGORIES, BLOG_AUTHORS

    # Load categories
    categories_file = BLOG_CONFIG_DIR / "categories.json"
    if categories_file.exists():
        BLOG_CATEGORIES = json.loads(categories_file.read_text(encoding="utf-8"))
        total_cats = sum(len(c.get('items', {})) for c in BLOG_CATEGORIES.values())
        print(f"  Loaded {total_cats} categories")

    # Load authors
    authors_file = BLOG_CONFIG_DIR / "authors.json"
    if authors_file.exists():
        BLOG_AUTHORS = json.loads(authors_file.read_text(encoding="utf-8"))
        print(f"  Loaded {len(BLOG_AUTHORS)} authors")


def load_blog_articles():
    """Load all blog article metadata."""
    global BLOG_ARTICLES
    BLOG_ARTICLES = []

    if not BLOG_ARTICLES_DIR.exists():
        return []

    for article_file in BLOG_ARTICLES_DIR.glob("*.json"):
        try:
            article_data = json.loads(article_file.read_text(encoding="utf-8"))
            BLOG_ARTICLES.append(article_data)
        except json.JSONDecodeError as e:
            print(f"  Error parsing {article_file.name}: {e}")

    # Sort by date (newest first)
    BLOG_ARTICLES.sort(key=lambda x: x.get("datePublished", ""), reverse=True)
    print(f"  Loaded {len(BLOG_ARTICLES)} blog articles")
    return BLOG_ARTICLES


def load_blog_content(slug):
    """Load the HTML content for an article."""
    content_file = BLOG_CONTENT_DIR / f"{slug}.html"
    if not content_file.exists():
        print(f"  Warning: Content file not found: {content_file}")
        return ""
    return content_file.read_text(encoding="utf-8")


def process_blog_images(content, article_data):
    """Replace {{image:id}} placeholders with full img tags from article data."""
    images = article_data.get("images", {}).get("content", [])
    image_map = {img["id"]: img for img in images}

    def replace_image(match):
        image_id = match.group(1).strip()
        if image_id not in image_map:
            print(f"  Warning: Image not found: {image_id}")
            return match.group(0)

        img = image_map[image_id]
        caption_html = ""
        if img.get("caption"):
            caption_html = f'<figcaption class="blog-image-caption">{img["caption"]}</figcaption>'

        return f'''<figure class="blog-image">
          <img src="{img['src']}" alt="{img['alt']}" width="{img.get('width', '')}" height="{img.get('height', '')}" loading="lazy">
          {caption_html}
        </figure>'''

    pattern = r"\{\{image:([a-zA-Z0-9_-]+)\}\}"
    return re.sub(pattern, replace_image, content)


def generate_blog_article_schema(article):
    """Generate JSON-LD schema for blog article."""
    if "schema" in article:
        return f'<script type="application/ld+json">\n{json.dumps(article["schema"], indent=2)}\n</script>'
    return ""


def generate_breadcrumb_schema(article):
    """Generate breadcrumb schema for article."""
    site_url = "https://www.firstsightfilms.com"

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": f"{site_url}/"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Blog",
                "item": f"{site_url}/blog/"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": article["title"]
            }
        ]
    }

    return f'<script type="application/ld+json">\n{json.dumps(breadcrumb, indent=2)}\n</script>'


def format_date(date_str):
    """Format ISO date to readable format."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except:
        return date_str


def build_blog_article(article, modules):
    """Build a single blog article page."""
    slug = article["slug"]

    # Load article template
    template_file = PAGES_DIR / "blog" / "_article-template.html"
    if not template_file.exists():
        print(f"  Warning: Blog article template not found")
        return

    template = template_file.read_text(encoding="utf-8")

    # Load article content
    content_html = load_blog_content(slug)
    content_html = process_blog_images(content_html, article)

    # Get author data
    author_id = article.get("author", "diego-cerquera")
    author = BLOG_AUTHORS.get(author_id, {})

    # Build placeholders
    seo = article.get("seo", {})
    hero_img = article.get("images", {}).get("hero", {})
    # Banner image for article hero (falls back to hero if not specified)
    banner_img = article.get("images", {}).get("banner", hero_img)

    # Replace article-specific placeholders
    replacements = {
        "{{blog-title}}": article["title"],
        "{{blog-seo-title}}": seo.get("title", f"{article['title']} | First Sight Films"),
        "{{blog-seo-description}}": seo.get("description", article["excerpt"]),
        "{{blog-og-image}}": hero_img.get("src", ""),
        "{{blog-date-published}}": article["datePublished"],
        "{{blog-date-modified}}": article.get("dateModified", article["datePublished"]),
        "{{blog-date-formatted}}": format_date(article["datePublished"]),
        "{{blog-excerpt}}": article["excerpt"],
        "{{blog-content}}": content_html,
        "{{blog-author-name}}": author.get("name", "Diego Cerquera"),
        "{{blog-author-bio}}": author.get("bio", ""),
        "{{blog-author-photo}}": author.get("photo", ""),
        "{{blog-hero-src}}": banner_img.get("src", ""),
        "{{blog-hero-alt}}": banner_img.get("alt", ""),
        "{{blog-article-schema}}": generate_blog_article_schema(article),
        "{{blog-breadcrumb-schema}}": generate_breadcrumb_schema(article),
    }

    for placeholder, value in replacements.items():
        template = template.replace(placeholder, str(value))

    # Process standard modules
    processed_content = process_page(template, modules)

    # Output path: /blog/article-slug/index.html
    output_path = OUTPUT_DIR / "blog" / slug / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Inject canonical and fix og:url
    url_path = f"/blog/{slug}/"
    processed_content = inject_canonical(processed_content, url_path)
    processed_content = fix_og_url(processed_content, url_path)
    processed_content = fix_blog_og_tags(processed_content)

    output_path.write_text(processed_content, encoding="utf-8")
    print(f"  Built blog article: {slug}")


def build_blog_listing(modules):
    """Build the blog listing page."""
    listing_template_file = PAGES_DIR / "blog" / "index.html"
    if not listing_template_file.exists():
        print(f"  Warning: Blog listing template not found")
        return

    template = listing_template_file.read_text(encoding="utf-8")

    # Generate article cards HTML
    cards_html = []
    for article in BLOG_ARTICLES:
        hero_img = article.get("images", {}).get("hero", {})
        date_formatted = format_date(article["datePublished"])
        img_position = hero_img.get("position", "")
        img_style = f' style="object-position: {img_position};"' if img_position else ""
        cards_html.append(f'''
        <article class="blog-card">
          <a href="/blog/{article['slug']}/" class="blog-card-link">
            <div class="blog-card-image">
              <img src="{hero_img.get('src', '')}" alt="{hero_img.get('alt', '')}"{img_style} loading="lazy">
            </div>
            <div class="blog-card-content">
              <time class="blog-card-date" datetime="{article['datePublished']}">{date_formatted}</time>
              <h2 class="blog-card-title">{article['title']}</h2>
              <p class="blog-card-excerpt">{article['excerpt']}</p>
              <span class="blog-card-readmore">Read More</span>
            </div>
          </a>
        </article>''')

    template = template.replace("{{blog-articles}}", "\n".join(cards_html))

    # Process modules
    processed_content = process_page(template, modules)

    # Output
    output_path = OUTPUT_DIR / "blog" / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    processed_content = inject_canonical(processed_content, "/blog/")
    processed_content = fix_og_url(processed_content, "/blog/")

    output_path.write_text(processed_content, encoding="utf-8")
    print(f"  Built blog listing: {len(BLOG_ARTICLES)} articles")


def build_blog(modules):
    """Build all blog pages."""
    print(f"\n[Blog] Loading configuration...")
    load_blog_config()

    print(f"\n[Blog] Loading articles...")
    load_blog_articles()

    print(f"\n[Blog] Building listing page...")
    build_blog_listing(modules)

    if not BLOG_ARTICLES:
        print("  No blog articles found")
        return

    print(f"\n[Blog] Building article pages...")
    for article in BLOG_ARTICLES:
        build_blog_article(article, modules)


# =============================================================================
# Watch Mode
# =============================================================================

class FSFBuildHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """Handles file system events and triggers selective rebuilds."""

    def __init__(self):
        self.modules = None
        self.last_build_time = 0
        self.debounce_seconds = 0.5  # Prevent rapid rebuilds
        self._load_modules()

    def _load_modules(self):
        """Load modules once for reuse."""
        self.modules = load_modules()
        load_page_config()
        load_image_manifests()

    def _should_rebuild(self):
        """Debounce rapid file changes."""
        now = time.time()
        if now - self.last_build_time < self.debounce_seconds:
            return False
        self.last_build_time = now
        return True

    def _get_page_from_path(self, file_path):
        """Determine which page to rebuild based on changed file."""
        path = Path(file_path)
        relative = path.relative_to(SRC_DIR) if SRC_DIR in path.parents or path.parent == SRC_DIR else path

        # Module changed - need to rebuild all (except protected)
        if "modules" in str(relative):
            return "__all_modules__"

        # CSS changed - just copy CSS
        if "css" in str(relative):
            return "__css__"

        # Page changed - rebuild just that page
        if "pages" in str(relative):
            # Extract page identifier
            parts = relative.parts
            if "pages" in parts:
                pages_idx = parts.index("pages")
                if len(parts) > pages_idx + 1:
                    return parts[pages_idx + 1]

        # Blog content changed
        if "blog" in str(relative):
            return "__blog__"

        # FAQ changed
        if "faqs" in str(relative):
            # Try to find which page uses this FAQ
            faq_name = path.stem
            return faq_name  # Will match pages that use this FAQ

        return None

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        # Only watch relevant files
        if not event.src_path.endswith(('.html', '.css', '.json')):
            return

        if not self._should_rebuild():
            return

        page = self._get_page_from_path(event.src_path)
        if not page:
            return

        print(f"\n[Watch] Detected change: {Path(event.src_path).name}")

        if page == "__css__":
            print("[Watch] Copying CSS...")
            copy_css()
            print("[Watch] Done!")

        elif page == "__all_modules__":
            print("[Watch] Module changed - rebuilding all pages (except protected)...")
            self._load_modules()  # Reload modules
            build_pages(self.modules, page_filter=None, skip_protected=True)
            print("[Watch] Done!")

        elif page == "__blog__":
            print("[Watch] Rebuilding blog...")
            build_blog(self.modules)
            print("[Watch] Done!")

        else:
            print(f"[Watch] Rebuilding: {page}")
            build_pages(self.modules, page_filter=page, skip_protected=True)
            print("[Watch] Done!")

    def on_created(self, event):
        """Handle new file creation."""
        self.on_modified(event)


def run_watch_mode():
    """Run the file watcher for automatic rebuilds."""
    if not WATCHDOG_AVAILABLE:
        print("\n[Error] Watch mode requires the 'watchdog' package.")
        print("Install it with: pip install watchdog")
        return

    print("\n" + "=" * 50)
    print("FSF Site Builder - Watch Mode")
    print("=" * 50)

    print("\n[Watch] Initial setup...")
    handler = FSFBuildHandler()

    print(f"\n[Watch] Protected pages (will not be overwritten):")
    for page in PROTECTED_PAGES:
        print(f"  - {page}")

    print(f"\n[Watch] Monitoring: {SRC_DIR}")
    print("[Watch] Press Ctrl+C to stop\n")

    observer = Observer()
    observer.schedule(handler, str(SRC_DIR), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Watch] Stopping...")
        observer.stop()
    observer.join()
    print("[Watch] Stopped.")


def build_single_page(page_name):
    """Build a single page by name."""
    print("\n" + "=" * 50)
    print(f"FSF Site Builder - Building: {page_name}")
    print("=" * 50)

    print("\n[1/3] Loading modules...")
    modules = load_modules()
    load_page_config()
    load_image_manifests()

    print(f"\n[2/3] Building page: {page_name}")
    build_pages(modules, page_filter=page_name, skip_protected=False)

    print(f"\n[3/3] Copying CSS...")
    copy_css()

    print("\n" + "=" * 50)
    print(f"Done! Built: {page_name}")
    print("=" * 50 + "\n")


def full_build():
    """Full site rebuild (original behavior, but skips protected pages)."""
    print("\n" + "=" * 50)
    print("FSF Site Builder - Full Rebuild")
    print("=" * 50)

    print(f"\n[Info] Protected pages (will not be overwritten):")
    for page in PROTECTED_PAGES:
        print(f"  - {page}")

    print("\n[1/11] Loading modules...")
    modules = load_modules()

    if not modules:
        print("No modules found. Add .html files to src/modules/")

    print(f"\n[2/11] Loading page config...")
    load_page_config()

    print(f"\n[3/11] Loading image manifests...")
    manifests = load_image_manifests()
    print(f"  Loaded {len(manifests)} images from manifests")

    print(f"\n[4/11] Building pages...")
    build_pages(modules, skip_protected=True)

    print(f"\n[5/11] Building blog...")
    build_blog(modules)

    print(f"\n[6/11] Copying existing pages (not yet migrated)...")
    copy_existing_pages()

    print(f"\n[7/11] Copying CSS...")
    copy_css()

    print(f"\n[8/11] Copying fonts...")
    copy_fonts()

    print(f"\n[9/11] Copying assets...")
    copy_assets()

    # Copy _redirects file for Netlify
    redirects_src = SRC_DIR / "_redirects"
    if redirects_src.exists():
        shutil.copy2(redirects_src, OUTPUT_DIR / "_redirects")
        print(f"  Copied: _redirects")

    # Copy favicon to root (browsers request /favicon.ico automatically)
    favicon_src = OUTPUT_DIR / "images" / "favicon" / "favicon.ico"
    if favicon_src.exists():
        shutil.copy2(favicon_src, OUTPUT_DIR / "favicon.ico")
        print(f"  Copied: favicon.ico to root")

    print(f"\n[10/11] Generating sitemap...")
    generate_sitemap()

    print(f"\n[11/11] Validating video references...")
    is_valid, missing, large, warnings = validate_video_references()

    print("\n" + "=" * 50)
    if not is_valid:
        print("BUILD COMPLETED WITH ERRORS")
        print("=" * 50)
        print(f"\n[BLOCKED] {len(missing)} missing video(s) - DO NOT PUSH")
        print("Fix: Add missing videos to output/video/portfolio/ or remove references")
        for v in missing:
            print(f"  - {v['path']}")
        print("\n" + "=" * 50 + "\n")
        return False  # Indicate build has issues
    elif large:
        print("BUILD COMPLETED WITH WARNINGS")
        print("=" * 50)
        print(f"\n[WARNING] {len(large)} video(s) exceed GitHub 100MB limit")
        print("These files won't push to GitHub without Git LFS or external hosting:")
        for v in large:
            print(f"  - {v['path']} ({v['size_mb']} MB)")
        print(f"\nOutput: {OUTPUT_DIR}")
        print("=" * 50 + "\n")
        return True  # Build ok but with warnings
    else:
        print(f"Full rebuild complete! Output: {OUTPUT_DIR}")
        print("=" * 50 + "\n")
        return True


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="FSF Site Builder - Build website from source files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build.py --watch              # Watch mode (recommended)
  python scripts/build.py --page photography   # Build single page
  python scripts/build.py --all                # Full rebuild
  python scripts/build.py --all --force        # Full rebuild INCLUDING protected pages
        """
    )

    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Watch mode: auto-rebuild on file changes'
    )

    parser.add_argument(
        '--page', '-p',
        type=str,
        help='Build only a specific page (e.g., "st-augustine-photography")'
    )

    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Full site rebuild'
    )

    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force rebuild of protected pages (use with --all)'
    )

    args = parser.parse_args()

    # Determine which mode to run
    if args.watch:
        run_watch_mode()
    elif args.page:
        build_single_page(args.page)
    elif args.all:
        if args.force:
            # Temporarily clear protected pages
            global PROTECTED_PAGES
            print("\n[Warning] --force flag: Protected pages WILL be overwritten!")
            PROTECTED_PAGES = []
        full_build()
    else:
        # No arguments - show help
        print("\n" + "=" * 50)
        print("FSF Site Builder")
        print("=" * 50)
        print("\nNo build mode specified. Choose one:\n")
        print("  --watch, -w    Watch mode (recommended)")
        print("                 Auto-rebuilds when you save files")
        print("                 Protected pages won't be overwritten\n")
        print("  --page, -p X   Build single page")
        print("                 Example: --page st-augustine-photography\n")
        print("  --all, -a      Full site rebuild")
        print("                 Rebuilds everything except protected pages\n")
        print("  --force, -f    Include protected pages (use with --all)\n")
        print(f"Protected pages: {', '.join(PROTECTED_PAGES)}")
        print("\nRun with --help for more details.")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
