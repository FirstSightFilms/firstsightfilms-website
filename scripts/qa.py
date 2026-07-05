#!/usr/bin/env python3
"""
FSF Pre-Push QA — technical-SEO gate.

Run AFTER `build.py --all`, BEFORE pushing live. Read-only: never touches the
live site or writes files. Exits non-zero on ANY failure so it can gate a push
(we only push on a complete pass).

Coverage (default): only the built pages that changed in git (output/**/*.html).
  python3 scripts/qa.py                      # audit changed pages
  python3 scripts/qa.py --all                # audit every built page
  python3 scripts/qa.py output/work/hma-mortgage/index.html   # audit named page(s)

Checks per page: JSON-LD validity · title <=60 · meta <=156 · exactly one H1 ·
canonical · FAQ visible == schema (1:1) · every <img> has an alt attr · internal
links/assets resolve (file exists or matches a redirect) · og:title/og:image/og:url ·
viewport meta · no mixed content (http:// resources) · Umami · referenced .mp4s exist.
Site-wide: sitemap.xml 200-only · robots.txt present + doesn't block crawling.

COMPANION: references/PAGE_OPTIMIZATION_SKILL.md is the MANUAL checklist for the
things this tool can't (Lighthouse performance, Core Web Vitals, contrast/keyboard/
screen-reader a11y). This script is the automated technical-SEO subset of it.
"""

import re, json, sys, os, glob, html, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "output")

TITLE_MAX, META_MAX = 60, 156
# <img> tags that are allowed to carry an empty alt (intentional/decorative).
ALT_EXEMPT_IDS = {"work-modal-image"}


# ---- redirects ------------------------------------------------------------
def load_redirect_rules():
    """Parse output/_redirects into (serve_200, redir_exact, redir_wild).
    A `... 200` rule serves as-is (NOT a redirect). Only 3xx/4xx are redirects.
    Match sources exactly (a `/foo` -> `/foo/` normalizer must NOT flag `/foo/`)."""
    serve_200, redir_exact, redir_wild = set(), set(), []
    p = os.path.join(OUT, "_redirects")
    if not os.path.exists(p):
        return serve_200, redir_exact, redir_wild
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        src = parts[0]
        status = next((t.rstrip("!") for t in parts[1:] if t.rstrip("!").isdigit()), "")
        if status.startswith("2"):          # 200 serve rule -> not a redirect
            serve_200.add(src)
        elif src.endswith("*"):
            redir_wild.append(src[:-1])     # "/foo/*" -> prefix "/foo/"
        else:
            redir_exact.add(src)
    return serve_200, redir_exact, redir_wild

SERVE_200, REDIR_EXACT, REDIR_WILD = load_redirect_rules()

def is_redirect(path):
    if path in SERVE_200:
        return False
    if path in REDIR_EXACT:
        return True
    return any(path.startswith(w) and path != w for w in REDIR_WILD)


# ---- path resolution ------------------------------------------------------
def resolve(path):
    """Map a site path to its output file, or None. Strips query/fragment."""
    path = path.split("#")[0].split("?")[0]
    if not path.startswith("/"):
        return None
    if path == "/":
        cand = os.path.join(OUT, "index.html")
    elif path.endswith("/"):
        cand = os.path.join(OUT, path.strip("/"), "index.html")
    elif "." in os.path.basename(path):        # has extension -> a file
        cand = os.path.join(OUT, path.strip("/"))
    else:                                       # extensionless -> directory index
        cand = os.path.join(OUT, path.strip("/"), "index.html")
    return cand if os.path.exists(cand) else None


# ---- per-page checks ------------------------------------------------------
def blocks_ld(h):
    return re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)

def check_page(path):
    """Return a list of failure strings ([] == pass)."""
    fails = []
    h = open(path, encoding="utf-8").read()

    # JSON-LD valid
    parsed = []
    for b in blocks_ld(h):
        try:
            parsed.append(json.loads(b))
        except Exception as e:
            fails.append(f"invalid JSON-LD ({str(e)[:60]})")

    # title / meta
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    if not t:
        fails.append("no <title>")
    elif len(html.unescape(t.group(1))) > TITLE_MAX:
        fails.append(f"title {len(html.unescape(t.group(1)))} chars (>{TITLE_MAX})")
    m = re.search(r'name="description" content="(.*?)"', h)
    if not m:
        fails.append("no meta description")
    elif len(html.unescape(m.group(1))) > META_MAX:
        fails.append(f"meta {len(html.unescape(m.group(1)))} chars (>{META_MAX})")

    # exactly one H1
    n_h1 = len(re.findall(r"<h1[\s>]", h))
    if n_h1 != 1:
        fails.append(f"{n_h1} <h1> (need 1)")

    # canonical
    if not re.search(r'rel="canonical"', h):
        fails.append("no canonical")

    # FAQ 1:1 — count actual question elements, not stray substrings (e.g. inline CSS selectors)
    visible = h.count('class="faq-question"')
    faq = next((d for d in parsed if isinstance(d, dict) and d.get("@type") == "FAQPage"), None)
    sch = len(faq["mainEntity"]) if faq else 0
    if (visible or sch) and visible != sch:
        fails.append(f"FAQ visible={visible} != schema={sch}")

    # img alt (missing attr fails; alt="" allowed only for exempt ids)
    for tag in re.findall(r"<img\b[^>]*>", h):
        if re.search(r'\balt="[^"]', tag):
            continue
        img_id = re.search(r'\bid="([^"]+)"', tag)
        if re.search(r'\balt=""', tag) and img_id and img_id.group(1) in ALT_EXEMPT_IDS:
            continue
        if not re.search(r"\balt=", tag):
            srcm = re.search(r'src="([^"]+)"', tag)
            fails.append("img missing alt: " + (srcm.group(1) if srcm else tag[:50]))

    # internal links + assets resolve (or match a redirect)
    for attr in ("href", "src"):
        for u in set(re.findall(rf'{attr}="(/[^"]*)"', h)):
            if u.startswith("//") or u.startswith("#"):
                continue
            if resolve(u) is None and not (attr == "href" and is_redirect(u.split("?")[0])):
                fails.append(f"broken {attr}: {u}")

    # OG presence (og:url added per PAGE_OPTIMIZATION_SKILL §4)
    if not re.search(r'property="og:title"', h):
        fails.append("no og:title")
    if not re.search(r'property="og:image"', h):
        fails.append("no og:image")
    if not re.search(r'property="og:url"', h):
        fails.append("no og:url")

    # viewport meta (mobile-friendly — PAGE_OPTIMIZATION_SKILL §4 Technical)
    if not re.search(r'name="viewport"', h):
        fails.append("no viewport meta")

    # mixed content — insecure resources loaded on an https page (Best Practices §3)
    for m in set(re.findall(r'src="(http://[^"]+)"', h)):
        fails.append(f"insecure http resource: {m}")

    # Umami
    if "cloud.umami.is" not in h:
        fails.append("no Umami script")

    # referenced videos exist
    for v in set(re.findall(r'(?:data-lightbox-video|data-video)="([^"]+\.mp4)"', h) +
                 re.findall(r'<source[^>]+src="([^"]+\.mp4)"', h)):
        if resolve(v) is None:
            fails.append(f"missing video: {v}")

    return fails


# ---- site-wide: sitemap 200-only ------------------------------------------
def check_sitemap():
    fails = []
    p = os.path.join(OUT, "sitemap.xml")
    if not os.path.exists(p):
        return ["sitemap.xml missing"]
    for loc in re.findall(r"<loc>https?://[^/]+(/[^<]*)</loc>", open(p, encoding="utf-8").read()):
        if resolve(loc) is None:
            fails.append(f"sitemap URL not a real file: {loc}")
        elif is_redirect(loc):
            fails.append(f"sitemap URL is a redirect (must be 200-only): {loc}")
    return fails


def check_robots():
    p = os.path.join(OUT, "robots.txt")
    if not os.path.exists(p):
        return ["robots.txt missing"]
    if re.search(r"(?im)^\s*Disallow:\s*/\s*$", open(p, encoding="utf-8").read()):
        return ["robots.txt has 'Disallow: /' (blocks all crawling)"]
    return []


# ---- target selection -----------------------------------------------------
def changed_pages():
    try:
        r = subprocess.run(["git", "-C", BASE, "status", "--porcelain", "output"],
                           capture_output=True, text=True)
        out = set()
        for line in r.stdout.splitlines():
            f = line[3:].strip()
            full = os.path.join(BASE, f)
            if f.endswith(".html") and os.path.exists(full):
                out.add(full)
            elif os.path.isdir(full):   # untracked new dir -> expand to its pages
                out.update(glob.glob(os.path.join(full, "**", "*.html"), recursive=True))
        return list(out)
    except Exception:
        return []

def main():
    args = [a for a in sys.argv[1:] if a != "--all"]
    if "--all" in sys.argv:
        pages = glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True)
    elif args:
        pages = []
        for a in args:
            pages += glob.glob(a, recursive=True) or ([a] if os.path.exists(a) else [])
    else:
        pages = changed_pages()

    # ignore non-page artifacts and pages that 301 in production (never serve their content)
    def page_url(p):
        rel = os.path.relpath(p, OUT)
        if rel == "index.html":
            return "/"
        return "/" + (rel[:-len("index.html")] if rel.endswith("/index.html") else rel)
    pages = [p for p in pages if "_snippets" not in p and "/410" not in p
             and "_template" not in p and os.path.basename(p) != "410.html"
             and not is_redirect(page_url(p))]

    print("=" * 60)
    print(f"FSF Pre-Push QA — {len(pages)} page(s)")
    print("=" * 60)
    if not pages:
        print("No changed built pages found. (build first, or pass paths / --all)")
        return 0

    total_fail = 0
    for p in sorted(pages):
        rel = os.path.relpath(p, OUT)
        f = check_page(p)
        if f:
            total_fail += len(f)
            print(f"✗ {rel}")
            for x in f:
                print(f"    - {x}")
        else:
            print(f"✓ {rel}")

    sm = check_sitemap()
    print("\n--- sitemap.xml (200-only) ---")
    if sm:
        total_fail += len(sm)
        for x in sm:
            print(f"  ✗ {x}")
    else:
        print("  ✓ all sitemap URLs are real 200 files")

    rb = check_robots()
    print("--- robots.txt ---")
    if rb:
        total_fail += len(rb)
        for x in rb:
            print(f"  ✗ {x}")
    else:
        print("  ✓ robots.txt allows crawling")

    print("\n" + "=" * 60)
    if total_fail:
        print(f"FAIL — {total_fail} issue(s). DO NOT PUSH until clean.")
        print("=" * 60)
        return 1
    print("PASS — all checks clean. Clear to push (Diego's go).")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
