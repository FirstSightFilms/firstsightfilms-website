#!/usr/bin/env python3
"""
FSF Site Builder
Combines modules + pages into complete HTML files.

Usage:
    python scripts/build.py

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
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
MODULES_DIR = SRC_DIR / "modules"
PAGES_DIR = SRC_DIR / "pages"
FAQS_DIR = SRC_DIR / "faqs"
REVIEWS_DIR = SRC_DIR / "reviews"
CONFIG_DIR = SRC_DIR / "config"
OUTPUT_DIR = BASE_DIR / "output"

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


def load_faq(faq_name):
    """Load FAQ JSON and generate HTML."""
    faq_data = load_faq_data(faq_name)
    if not faq_data:
        return ""

    # Generate FAQ HTML (answers already contain HTML)
    html_parts = ['<div class="faq-list">']

    for item in faq_data.get("questions", []):
        question = item.get("question", "")
        answer = item.get("answer", "")
        html_parts.append(f'''        <details class="faq-item">
          <summary class="faq-question">{question}</summary>
          <div class="faq-answer">
            {answer}
          </div>
        </details>''')

    html_parts.append('      </div>')

    return '\n'.join(html_parts)


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
        expand_btn_html = '<button class="review-expand" aria-label="Expand review">Read more</button>' if is_long else ""

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


def build_pages(modules):
    """Process all page templates and output complete HTML."""
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


def copy_css():
    """Copy CSS from src/css to output/css."""
    dest_path = OUTPUT_DIR / "css"

    if SRC_CSS_DIR.exists():
        if dest_path.exists():
            shutil.rmtree(dest_path)
        shutil.copytree(SRC_CSS_DIR, dest_path)
        print(f"  Copied: css/ (from src/css)")


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


def main():
    print("\n" + "=" * 50)
    print("FSF Site Builder")
    print("=" * 50)

    print("\n[1/10] Loading modules...")
    modules = load_modules()

    if not modules:
        print("No modules found. Add .html files to src/modules/")

    print(f"\n[2/10] Loading page config...")
    load_page_config()

    print(f"\n[3/10] Loading image manifests...")
    manifests = load_image_manifests()
    print(f"  Loaded {len(manifests)} images from manifests")

    print(f"\n[4/10] Building pages...")
    build_pages(modules)

    print(f"\n[5/10] Building blog...")
    build_blog(modules)

    print(f"\n[6/10] Copying existing pages (not yet migrated)...")
    copy_existing_pages()

    print(f"\n[7/10] Copying CSS...")
    copy_css()

    print(f"\n[8/10] Copying fonts...")
    copy_fonts()

    print(f"\n[9/10] Copying assets...")
    copy_assets()

    # Copy _redirects file for Netlify
    redirects_src = SRC_DIR / "_redirects"
    if redirects_src.exists():
        shutil.copy2(redirects_src, OUTPUT_DIR / "_redirects")
        print(f"  Copied: _redirects")

    print(f"\n[10/10] Generating sitemap...")
    generate_sitemap()

    print("\n" + "=" * 50)
    print(f"Build complete! Output: {OUTPUT_DIR}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
