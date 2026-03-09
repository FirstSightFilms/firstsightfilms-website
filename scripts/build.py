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
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
MODULES_DIR = SRC_DIR / "modules"
PAGES_DIR = SRC_DIR / "pages"
OUTPUT_DIR = BASE_DIR / "output"

# Assets to copy from root to output
ASSETS_TO_COPY = ["css", "images", "js"]


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


def process_page(page_content, modules):
    """Replace {{module_name}} placeholders with module content."""

    def replace_module(match):
        module_name = match.group(1).strip()
        if module_name in modules:
            return modules[module_name]
        else:
            print(f"  Warning: Module not found: {module_name}")
            return match.group(0)  # Keep original if not found

    # Match {{module_name}} pattern
    pattern = r"\{\{(\w+)\}\}"
    return re.sub(pattern, replace_module, page_content)


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
    """Copy static assets (css, images, js) to output directory."""
    for asset_name in ASSETS_TO_COPY:
        src_path = BASE_DIR / asset_name
        dest_path = OUTPUT_DIR / asset_name

        if src_path.exists():
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            print(f"  Copied: {asset_name}/")


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

    print("\n[1/4] Loading modules...")
    modules = load_modules()

    if not modules:
        print("No modules found. Add .html files to src/modules/")

    print(f"\n[2/4] Building pages...")
    build_pages(modules)

    print(f"\n[3/4] Copying existing pages (not yet migrated)...")
    copy_existing_pages()

    print(f"\n[4/4] Copying assets...")
    copy_assets()

    print("\n" + "=" * 50)
    print(f"Build complete! Output: {OUTPUT_DIR}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
