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
            <div class="review-quote-wrapper">
              <blockquote class="review-quote">"{text}"</blockquote>
            </div>
            <div class="review-footer">
              <span class="review-date">{date}</span>
              {link_html}
            </div>
          </div>'''
        cards_html.append(card)

    total_pages = (len(reviews) + 2) // 3  # 3 cards per page on desktop

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
        <span class="current-page">1</span> / <span class="total-pages">{total_pages}</span>
      </div>
      <button class="review-nav next" aria-label="Next reviews">&#8250;</button>
    </div>

    <div class="review-pagination review-pagination-desktop">
      <span class="current-page">1</span> / <span class="total-pages">{total_pages}</span>
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

        # Read page template
        page_content = page_file.read_text(encoding="utf-8")

        # Process modules
        processed_content = process_page(page_content, modules)

        # Determine output path
        if relative_path.name == "index.html":
            # Root or subfolder index stays as-is
            output_path = OUTPUT_DIR / relative_path
        else:
            # Other pages become folder/index.html for clean URLs
            # e.g., about.html -> about/index.html
            folder_name = relative_path.stem
            parent = relative_path.parent
            output_path = OUTPUT_DIR / parent / folder_name / "index.html"

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


def main():
    print("\n" + "=" * 50)
    print("FSF Site Builder")
    print("=" * 50)

    print("\n[1/7] Loading modules...")
    modules = load_modules()

    if not modules:
        print("No modules found. Add .html files to src/modules/")

    print(f"\n[2/7] Loading page config...")
    load_page_config()

    print(f"\n[3/7] Loading image manifests...")
    manifests = load_image_manifests()
    print(f"  Loaded {len(manifests)} images from manifests")

    print(f"\n[4/7] Building pages...")
    build_pages(modules)

    print(f"\n[5/7] Copying existing pages (not yet migrated)...")
    copy_existing_pages()

    print(f"\n[6/8] Copying CSS...")
    copy_css()

    print(f"\n[7/8] Copying fonts...")
    copy_fonts()

    print(f"\n[8/8] Copying assets...")
    copy_assets()

    print("\n" + "=" * 50)
    print(f"Build complete! Output: {OUTPUT_DIR}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
