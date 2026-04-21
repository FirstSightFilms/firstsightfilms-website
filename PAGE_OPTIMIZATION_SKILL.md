# Page Optimization Skill

A repeatable checklist for optimizing new pages for Performance, Accessibility, Best Practices, and SEO.

**Target Scores:** 90+ in all Lighthouse categories

---

## Quick Reference

| Category | Target | Key Metrics |
|----------|--------|-------------|
| Performance | 90+ | LCP < 2.5s, CLS < 0.1, INP < 200ms |
| Accessibility | 100 | WCAG 2.1 AA compliance |
| Best Practices | 100 | HTTPS, no vulnerabilities |
| SEO | 100 | Crawlable, structured data |

---

## 1. PERFORMANCE CHECKLIST

### Images (Highest Impact)

- [ ] **Convert to WebP/AVIF** - 25-50% smaller than PNG/JPEG
  ```bash
  # Using Python PIL
  from PIL import Image
  img = Image.open('image.png')
  img.save('image.webp', 'WEBP', quality=85)
  ```

- [ ] **Set explicit dimensions** - Prevents CLS
  ```html
  <img src="image.webp" width="800" height="600" alt="Description">
  ```

- [ ] **Lazy load below-fold images**
  ```html
  <img src="image.webp" loading="lazy" alt="Description">
  ```

- [ ] **Eager load LCP image** - The largest visible image
  ```html
  <img src="hero.webp" loading="eager" fetchpriority="high" alt="Hero">
  ```

- [ ] **Resize images appropriately** - Don't serve 2000px images in 400px containers
  ```bash
  # macOS: Resize to max 800px width
  sips -Z 800 image.png
  ```

### Fonts (Critical for LCP)

- [ ] **Use system fonts when possible** - Zero download time
  ```css
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  ```

- [ ] **If using custom fonts:**
  - Use `font-display: swap` in @font-face
  - Preload only critical fonts
  - Subset fonts to only needed characters
  - Use woff2 format (best compression)

- [ ] **Avoid preloading large variable fonts** - 99KB+ fonts hurt mobile LCP

### CSS

- [ ] **Minify CSS files**
  ```bash
  npx clean-css-cli -o main.min.css main.css
  ```

- [ ] **Inline critical CSS** - For above-fold content (optional, can cause CLS if done wrong)

- [ ] **Remove unused CSS** - Use PurgeCSS or manual audit

- [ ] **Never defer CSS with media="print" hack** - Causes massive CLS

### JavaScript

- [ ] **Defer non-critical JS**
  ```html
  <script src="app.js" defer></script>
  ```

- [ ] **Async for independent scripts**
  ```html
  <script src="analytics.js" async></script>
  ```

- [ ] **Remove unused JS** - Bundle analyze and tree-shake

### Mobile-Specific

- [ ] **Hide decorative elements on mobile** - Save bandwidth
  ```css
  @media (max-width: 768px) {
    .decorative-element { display: none; }
  }
  ```

- [ ] **Test on 3G throttling** - Lighthouse mobile simulates slow 3G (~1.6 Mbps)

- [ ] **Critical path budget: < 150KB** - HTML + CSS + fonts for first paint

---

## 2. ACCESSIBILITY CHECKLIST

### Images

- [ ] **Alt text on all images** - Descriptive for content, empty for decorative
  ```html
  <img src="photo.webp" alt="Team meeting in conference room">
  <img src="divider.svg" alt="" role="presentation">
  ```

### Color & Contrast

- [ ] **Contrast ratio 4.5:1** for normal text (AA)
- [ ] **Contrast ratio 3:1** for large text (18px+ or 14px+ bold)
- [ ] **Test with:** Chrome DevTools > Rendering > Emulate vision deficiencies

### Forms

- [ ] **Label all form inputs**
  ```html
  <label for="email">Email</label>
  <input type="email" id="email" name="email">
  ```

- [ ] **Error messages are descriptive and associated**

### Navigation

- [ ] **Skip link for keyboard users**
  ```html
  <a href="#main-content" class="skip-link">Skip to main content</a>
  ```

- [ ] **Logical heading hierarchy** - h1 > h2 > h3, no skipping levels

- [ ] **Focus indicators visible** - Never `outline: none` without replacement

### ARIA

- [ ] **aria-label for icon buttons**
  ```html
  <button aria-label="Close menu"><svg>...</svg></button>
  ```

- [ ] **aria-hidden="true" for decorative duplicates**
  ```html
  <div class="logo-set" aria-hidden="true"><!-- duplicate for animation --></div>
  ```

- [ ] **Buttons have matching aria-label and visible text** (if both exist)

### Testing

- [ ] **Keyboard navigation test** - Tab through entire page
- [ ] **Screen reader test** - VoiceOver (Mac) or NVDA (Windows)
- [ ] **Lighthouse catches only 30-40%** - Manual testing required

---

## 3. BEST PRACTICES CHECKLIST

### Security

- [ ] **HTTPS everywhere** - All resources served securely
- [ ] **No mixed content** - No HTTP resources on HTTPS pages
- [ ] **CSP headers configured** (in netlify.toml)
  ```toml
  [[headers]]
    for = "/*"
    [headers.values]
      X-Frame-Options = "DENY"
      X-XSS-Protection = "1; mode=block"
      X-Content-Type-Options = "nosniff"
  ```

### Console

- [ ] **No console errors**
- [ ] **No deprecated API warnings**
- [ ] **No 404 requests**

### Libraries

- [ ] **No vulnerable dependencies** - Run `npm audit`
- [ ] **Keep libraries updated**

---

## 4. SEO CHECKLIST

### Meta Tags

- [ ] **Unique title tag** - 50-60 characters
  ```html
  <title>Primary Keyword | Brand Name</title>
  ```

- [ ] **Meta description** - 150-160 characters
  ```html
  <meta name="description" content="Compelling description with keyword...">
  ```

- [ ] **Canonical URL**
  ```html
  <link rel="canonical" href="https://www.example.com/page/">
  ```

### Open Graph / Social

- [ ] **OG tags for social sharing**
  ```html
  <meta property="og:title" content="Page Title">
  <meta property="og:description" content="Description">
  <meta property="og:image" content="https://example.com/image.jpg">
  <meta property="og:url" content="https://example.com/page/">
  ```

### Structure

- [ ] **One H1 per page**
- [ ] **Logical heading hierarchy**
- [ ] **Descriptive URLs** - `/service-name/` not `/page?id=123`

### Structured Data (JSON-LD)

- [ ] **Organization schema** (homepage)
- [ ] **LocalBusiness schema** (if applicable)
- [ ] **BreadcrumbList** (all pages)
- [ ] **Service/Product schema** (service pages)
- [ ] **Review/AggregateRating** (if reviews exist)
- [ ] **Validate with:** https://search.google.com/test/rich-results

### Technical

- [ ] **robots.txt allows crawling**
- [ ] **XML sitemap exists and is submitted**
- [ ] **No orphan pages** - All pages linked from somewhere
- [ ] **No broken links** - 404s hurt crawl budget
- [ ] **Mobile-friendly** - Responsive design

### Core Web Vitals (Ranking Factor)

- [ ] **LCP < 2.5s** - Largest Contentful Paint
- [ ] **INP < 200ms** - Interaction to Next Paint
- [ ] **CLS < 0.1** - Cumulative Layout Shift

---

## 5. LESSONS LEARNED (First Sight Films)

### What Worked

| Optimization | Savings | Impact |
|--------------|---------|--------|
| System fonts instead of custom | 148KB | Major LCP improvement |
| PNG → WebP conversion | ~100KB | Faster image loading |
| CSS minification | 22KB | Reduced parse time |
| Lazy loading carousel logos | 90KB deferred | Faster initial load |
| Hiding decorative elements on mobile | 31KB | Mobile bandwidth savings |

### What Failed

| Attempt | Problem | Lesson |
|---------|---------|--------|
| CSS deferral with `media="print"` | CLS spike to 0.39 | Don't defer CSS without inlining critical styles |
| Removing all font preloads | Layout shift | If using custom fonts, preload the primary one |

### Mobile Performance Reality

On simulated 3G (~200 KB/s = 1.6 Mbps):
- Every 100KB = 0.5 seconds added to load
- Target: < 150KB for critical path
- Fonts are often the biggest blocker

---

## 6. TOOLS

### Testing
- **Lighthouse** - Chrome DevTools > Lighthouse tab
- **PageSpeed Insights** - https://pagespeed.web.dev/
- **WebPageTest** - https://www.webpagetest.org/

### Accessibility
- **axe DevTools** - Browser extension
- **WAVE** - https://wave.webaim.org/

### SEO
- **Rich Results Test** - https://search.google.com/test/rich-results
- **Google Search Console** - Monitor indexing and performance

### Image Optimization
- **Squoosh** - https://squoosh.app/
- **TinyPNG** - https://tinypng.com/

---

## 7. AUDIT SCHEDULE

| Frequency | Action |
|-----------|--------|
| Every new page | Run through this checklist |
| Weekly | Check Search Console for errors |
| Monthly | Full Lighthouse audit of key pages |
| Quarterly | Comprehensive technical SEO audit |

---

## Sources

- [DebugBear - Lighthouse Performance](https://www.debugbear.com/docs/metrics/lighthouse-performance)
- [Empathy First Media - 2025 Lighthouse Updates](https://empathyfirstmedia.com/google-lighthouse-performance-insight-audits/)
- [Scanluma - Accessibility Score](https://scanluma.com/blog/how-to-improve-your-lighthouse-accessibility-score/)
- [Chrome Developers - Accessibility Scoring](https://developer.chrome.com/docs/lighthouse/accessibility/scoring)
- [DebugBear - Technical SEO Checklist 2026](https://www.debugbear.com/blog/technical-seo-checklist)
- [NoGood - Technical SEO Checklist 2026](https://nogood.io/blog/technical-seo-checklist/)
