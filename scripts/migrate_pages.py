#!/usr/bin/env python3
"""
FSF Page Migration Script
Migrates existing HTML pages to the modular system by replacing
old Squarespace headers with {{header}} placeholder.

Usage:
    python scripts/migrate_pages.py

What it does:
    1. Reads each HTML file from specified page folders
    2. Finds and removes the old <header>...</header> section
    3. Inserts {{header}} placeholder
    4. Adds header.css link if not present
    5. Saves to src/pages/ folder structure
"""

import os
import re
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
PAGES_DIR = BASE_DIR / "src" / "pages"

# Page folders to migrate (each contains index.html)
PAGE_FOLDERS = ["aboutus", "contact", "photo", "portfolio", "video"]

# Also check for subpages in video folder
VIDEO_SUBPAGES = []


def find_header_bounds(content):
    """Find the start and end positions of the old header."""
    # Look for Squarespace header pattern
    header_patterns = [
        r'<header class="white header[^>]*>',
        r'<header class="[^"]*header[^>]*>',
        r'<header[^>]*data-controller="Header"[^>]*>',
    ]

    header_start = -1
    for pattern in header_patterns:
        match = re.search(pattern, content)
        if match:
            header_start = match.start()
            break

    if header_start == -1:
        return None, None

    # Find closing </header>
    header_end = content.find('</header>', header_start)
    if header_end == -1:
        return None, None

    header_end += len('</header>')
    return header_start, header_end


def add_header_css_link(content):
    """Add header.css link if not already present."""
    if 'header.css' in content:
        return content

    # Find </head> and insert before it
    head_end = content.find('</head>')
    if head_end == -1:
        return content

    css_link = '<link rel="stylesheet" href="/css/header.css">\n'
    return content[:head_end] + css_link + content[head_end:]


def migrate_page(source_path, dest_path):
    """Migrate a single page to the modular system."""
    print(f"  Processing: {source_path}")

    # Read original content
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find header bounds
    header_start, header_end = find_header_bounds(content)

    if header_start is None:
        print(f"    WARNING: Could not find header in {source_path}")
        return False

    # Calculate header size for reporting
    header_size = header_end - header_start
    print(f"    Found header: {header_size} characters")

    # Build new content
    before_header = content[:header_start]
    after_header = content[header_end:]

    new_content = before_header + "{{header}}\n\n" + after_header

    # Add header.css link
    new_content = add_header_css_link(new_content)

    # Create destination directory
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Write new content
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"    Migrated to: {dest_path.relative_to(BASE_DIR)}")
    return True


def main():
    print("\n" + "=" * 50)
    print("FSF Page Migration Script")
    print("=" * 50)

    migrated = 0
    failed = 0

    # Migrate main page folders
    for folder in PAGE_FOLDERS:
        source_path = BASE_DIR / folder / "index.html"
        dest_path = PAGES_DIR / folder / "index.html"

        if not source_path.exists():
            print(f"\n  Skipping {folder}/ - source not found")
            continue

        print(f"\n[{folder}]")
        if migrate_page(source_path, dest_path):
            migrated += 1
        else:
            failed += 1

    # Check for video subpages
    video_dir = BASE_DIR / "video"
    if video_dir.exists():
        for subpage in video_dir.iterdir():
            if subpage.is_dir() and (subpage / "index.html").exists():
                source_path = subpage / "index.html"
                dest_path = PAGES_DIR / "video" / subpage.name / "index.html"

                print(f"\n[video/{subpage.name}]")
                if migrate_page(source_path, dest_path):
                    migrated += 1
                else:
                    failed += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"Migration complete!")
    print(f"  Migrated: {migrated} pages")
    print(f"  Failed: {failed} pages")
    print("=" * 50)
    print("\nNext step: Run 'python3 scripts/build.py' to build all pages")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
