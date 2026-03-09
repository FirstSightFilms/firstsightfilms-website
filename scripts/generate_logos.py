#!/usr/bin/env python3
"""
Logo Manager for FSF Website

Features:
  - Optimize logos (resize, compress, convert to WebP)
  - Generate HTML with proper alt descriptions
  - Auto-update page files with new logos
  - CSV config for custom alt text
  - Validation and reporting

Usage:
  python3 scripts/generate_logos.py              # Show help
  python3 scripts/generate_logos.py list         # List all logos
  python3 scripts/generate_logos.py optimize     # Optimize all logos
  python3 scripts/generate_logos.py generate     # Generate HTML
  python3 scripts/generate_logos.py update       # Update page files
  python3 scripts/generate_logos.py init-config  # Create alt text config
"""

import os
import sys
import csv
import json
import shutil
from pathlib import Path
from datetime import datetime

# Try to import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# =============================================================================
# Configuration
# =============================================================================

BASE_DIR = Path(__file__).parent.parent
LOGOS_DIR = BASE_DIR / "images" / "logos"
LOGOS_OPTIMIZED_DIR = BASE_DIR / "images" / "logos" / "optimized"
CONFIG_FILE = BASE_DIR / "scripts" / "logos_config.csv"
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif'}

# Optimization settings for FSF collaborators section
# Display size: 150x60px - optimizing for 2x retina
MAX_WIDTH = 400        # Max width in pixels (allows flexibility for wide logos)
MAX_HEIGHT = 120       # Max height in pixels (2x display height)
QUALITY = 90           # Higher quality for logo clarity
CONVERT_TO_WEBP = True # Convert all to WebP for smaller file sizes

# =============================================================================
# Helper Functions
# =============================================================================

def get_logos():
    """Get all logo files from the logos directory."""
    if not LOGOS_DIR.exists():
        return []

    logos = []
    for file in sorted(LOGOS_DIR.iterdir()):
        if file.suffix.lower() in IMAGE_EXTENSIONS and file.is_file():
            logos.append(file)
    return logos


def filename_to_alt(filename: str) -> str:
    """Convert filename to readable alt text."""
    name = Path(filename).stem

    # Remove common suffixes
    for suffix in ['-logo', '_logo', '-Logo', '_Logo']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    # Replace hyphens and underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')

    # Handle abbreviations
    abbreviations = {
        'fl': 'Florida',
        'dep': 'DEP',
        'st': 'St.',
        'uf': 'UF',
        'sma': 'SMA',
        'mchd': 'MCHD',
        'amp': 'AMP',
        'fans': 'FANS',
        'aerdf': 'AERDF',
    }

    words = name.split()
    result = []

    for word in words:
        lower = word.lower()
        if lower in abbreviations:
            result.append(abbreviations[lower])
        else:
            result.append(word.title())

    return ' '.join(result)


def load_config():
    """Load custom alt text from CSV config file."""
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                config[row['filename']] = row['alt_text']
    return config


def save_config(config):
    """Save alt text config to CSV file."""
    with open(CONFIG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'alt_text'])
        writer.writeheader()
        for filename, alt_text in sorted(config.items()):
            writer.writerow({'filename': filename, 'alt_text': alt_text})


def get_alt_text(filename: str, config: dict) -> str:
    """Get alt text from config or generate from filename."""
    if filename in config:
        return config[filename]
    return filename_to_alt(filename)


def get_file_size(filepath_or_bytes) -> str:
    """Get human-readable file size."""
    if isinstance(filepath_or_bytes, (int, float)):
        size = filepath_or_bytes
    else:
        size = filepath_or_bytes.stat().st_size
    for unit in ['B', 'KB', 'MB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


# =============================================================================
# Commands
# =============================================================================

def cmd_list():
    """List all logos with details."""
    logos = get_logos()
    config = load_config()

    if not logos:
        print(f"No logos found in: {LOGOS_DIR}")
        return

    print(f"\n{'='*70}")
    print(f"Found {len(logos)} logo(s) in {LOGOS_DIR}")
    print(f"{'='*70}\n")

    total_size = 0
    for logo in logos:
        size = logo.stat().st_size
        total_size += size
        alt = get_alt_text(logo.name, config)
        custom = "(custom)" if logo.name in config else "(auto)"

        # Get dimensions if PIL available
        dims = ""
        if PIL_AVAILABLE:
            try:
                with Image.open(logo) as img:
                    dims = f"{img.width}x{img.height}"
            except:
                dims = "???"

        print(f"  {logo.name}")
        print(f"    Alt: {alt} {custom}")
        print(f"    Size: {get_file_size(logo)}  Dimensions: {dims}")
        print()

    print(f"{'='*70}")
    print(f"Total: {len(logos)} files, {get_file_size(total_size)}")
    print()


def cmd_optimize():
    """Optimize all logos (resize, compress, convert)."""
    if not PIL_AVAILABLE:
        print("Error: Pillow library required for optimization.")
        print("Install with: pip3 install Pillow")
        return

    logos = get_logos()
    if not logos:
        print(f"No logos found in: {LOGOS_DIR}")
        return

    # Create optimized directory
    LOGOS_OPTIMIZED_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("Optimizing logos...")
    print(f"Settings: Max {MAX_WIDTH}x{MAX_HEIGHT}px, Quality {QUALITY}%")
    print(f"{'='*70}\n")

    total_before = 0
    total_after = 0

    for logo in logos:
        original_size = logo.stat().st_size
        total_before += original_size

        try:
            with Image.open(logo) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Calculate new dimensions maintaining aspect ratio
                ratio = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height)
                if ratio < 1:  # Only resize if larger than max
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Save optimized version
                if CONVERT_TO_WEBP:
                    output_name = logo.stem + '.webp'
                    output_path = LOGOS_OPTIMIZED_DIR / output_name
                    img.save(output_path, 'WEBP', quality=QUALITY)
                else:
                    output_path = LOGOS_OPTIMIZED_DIR / logo.name
                    if logo.suffix.lower() in ['.jpg', '.jpeg']:
                        img.save(output_path, 'JPEG', quality=QUALITY, optimize=True)
                    else:
                        img.save(output_path, 'PNG', optimize=True)

                new_size = output_path.stat().st_size
                total_after += new_size
                savings = ((original_size - new_size) / original_size) * 100

                print(f"  {logo.name}")
                print(f"    -> {output_path.name}")
                print(f"    {get_file_size(logo)} -> {get_file_size(output_path)} ({savings:.0f}% smaller)")
                print()

        except Exception as e:
            print(f"  Error processing {logo.name}: {e}")
            # Copy original as fallback
            shutil.copy(logo, LOGOS_OPTIMIZED_DIR / logo.name)
            total_after += original_size

    savings = ((total_before - total_after) / total_before) * 100 if total_before > 0 else 0
    print(f"{'='*70}")
    print(f"Total: {get_file_size(total_before)} -> {get_file_size(total_after)} ({savings:.0f}% smaller)")
    print(f"\nOptimized logos saved to: {LOGOS_OPTIMIZED_DIR}")
    print("\nTo use optimized logos, update image paths to /images/logos/optimized/")


def cmd_generate():
    """Generate HTML for collaborators section."""
    logos = get_logos()
    config = load_config()

    if not logos:
        print(f"No logos found in: {LOGOS_DIR}")
        return

    print(f"\n{'='*70}")
    print("GENERATED HTML - Copy and paste into your page:")
    print(f"{'='*70}\n")

    print('      <div class="collaborators-grid">')
    for logo in logos:
        alt = get_alt_text(logo.name, config)
        print(f'        <div class="collaborator-logo"><img src="/images/logos/{logo.name}" alt="{alt}" loading="lazy"></div>')
    print('      </div>')
    print()


def cmd_update():
    """Update page files with current logos."""
    logos = get_logos()
    config = load_config()

    if not logos:
        print(f"No logos found in: {LOGOS_DIR}")
        return

    # Build the new HTML
    lines = ['      <div class="collaborators-grid">']
    for logo in logos:
        alt = get_alt_text(logo.name, config)
        lines.append(f'        <div class="collaborator-logo"><img src="/images/logos/{logo.name}" alt="{alt}" loading="lazy"></div>')
    lines.append('      </div>')
    new_html = '\n'.join(lines)

    # Find pages with collaborators section
    pages_dir = BASE_DIR / "src" / "pages"
    updated_files = []

    for html_file in pages_dir.rglob("*.html"):
        content = html_file.read_text()

        if 'class="collaborators-grid"' in content:
            # Replace the collaborators-grid div
            import re
            pattern = r'<div class="collaborators-grid">.*?</div>\s*(?=</div>)'
            new_content = re.sub(pattern, new_html, content, flags=re.DOTALL)

            if new_content != content:
                html_file.write_text(new_content)
                updated_files.append(html_file.relative_to(BASE_DIR))

    if updated_files:
        print(f"\nUpdated {len(updated_files)} file(s):")
        for f in updated_files:
            print(f"  - {f}")
        print("\nRun 'python3 scripts/build.py' to rebuild the site.")
    else:
        print("No files with collaborators section found.")


def cmd_init_config():
    """Create/update alt text config file."""
    logos = get_logos()
    config = load_config()

    # Add missing logos to config
    for logo in logos:
        if logo.name not in config:
            config[logo.name] = filename_to_alt(logo.name)

    save_config(config)
    print(f"\nConfig file created/updated: {CONFIG_FILE}")
    print(f"Edit this file to customize alt text for each logo.")
    print(f"\nCurrent entries:")
    for filename, alt_text in sorted(config.items()):
        print(f"  {filename}: {alt_text}")


def cmd_help():
    """Show help message."""
    print(__doc__)

    if not PIL_AVAILABLE:
        print("\n" + "="*70)
        print("NOTE: Pillow not installed. Image optimization unavailable.")
        print("Install with: pip3 install Pillow")
        print("="*70)


# =============================================================================
# Main
# =============================================================================

def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1].lower()

    commands = {
        'list': cmd_list,
        'optimize': cmd_optimize,
        'generate': cmd_generate,
        'update': cmd_update,
        'init-config': cmd_init_config,
        'help': cmd_help,
        '-h': cmd_help,
        '--help': cmd_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        cmd_help()


if __name__ == "__main__":
    main()
