#!/usr/bin/env python3
"""Update all {{reviews}} placeholders with Ultra Compact Grid"""

import os
from pathlib import Path

REVIEWS_HTML = '''<!-- Reviews Section - Ultra Compact Grid -->
  <section class="section-reviews-compact" id="reviews">
    <style>
    .section-reviews-compact { padding: 3rem 1rem; background: #fff; }
    .reviews-compact-header { text-align: center; margin-bottom: 1.5rem; }
    .reviews-compact-header h2 { font-size: 1.75rem; color: #1a1a2e; margin-bottom: 0.5rem; }
    .reviews-compact-header p { color: #666; font-size: 0.95rem; }
    .reviews-compact-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; max-width: 1400px; margin: 0 auto 1.5rem; }
    .review-card-compact { background: #fafafa; padding: 0.75rem; height: 130px; overflow: hidden; position: relative; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
    .review-card-compact .review-stars { color: #f4c057; font-size: 0.7rem; margin-bottom: 0.25rem; }
    .review-card-compact .review-text { font-size: 0.75rem; line-height: 1.4; color: #444; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 0.4rem; }
    .review-card-compact .review-author { font-size: 0.7rem; font-weight: 600; color: #1a1a2e; }
    .review-card-compact::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 25px; background: linear-gradient(transparent, #fafafa); pointer-events: none; }
    .reviews-compact-cta { text-align: center; }
    .reviews-compact-cta a { color: #1a1a2e; font-size: 0.9rem; text-decoration: none; border-bottom: 1px solid #f4c057; padding-bottom: 2px; }
    .reviews-compact-cta a:hover { color: #f4c057; }
    @media (max-width: 1100px) { .reviews-compact-grid { grid-template-columns: repeat(3, 1fr); } }
    @media (max-width: 768px) { .section-reviews-compact { padding: 2rem 0.75rem; } .reviews-compact-grid { grid-template-columns: repeat(2, 1fr); gap: 0.4rem; } .reviews-compact-header h2 { font-size: 1.5rem; } }
    @media (max-width: 480px) { .review-card-compact { height: 115px; padding: 0.6rem; } .review-card-compact .review-text { -webkit-line-clamp: 2; font-size: 0.7rem; } }
    </style>
    <div class="reviews-compact-header"><h2>What Our Clients Say</h2><p>50+ five-star reviews on Google</p></div>
    <div class="reviews-compact-grid">
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">So great to work with! Diego was fun and made the entire experience really easy. The final outcome was exceptional.</p><p class="review-author">Megan Vidal</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">The quality of your work, professionalism, and attention to detail are well above standard. I am very grateful.</p><p class="review-author">Isabelle Renault</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">The photos are absolutely incredible—I LOVE them! Your attention to detail really showed in the final product.</p><p class="review-author">Anna Gilbert</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">Diego and First Sight Films were instrumental to the success of our video project. He went above and beyond.</p><p class="review-author">Marcus Fung</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">His team was responsive in their replies. They took great photos and video clips for our exhibition design business.</p><p class="review-author">Quatrefoil Associates</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">The recording looks and sounds way better than I thought it could. Stoked this resource is here in St. Augustine.</p><p class="review-author">Kelsey May</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">Diego did an incredible job capturing our event! He has a great eye for detail. The final product exceeded our expectations.</p><p class="review-author">John Kersey</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">They made the whole family feel so comfortable in front of the camera and the photos came out absolutely stunning!</p><p class="review-author">Emma Parmar</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">Diego & Trista delivered high-quality photo, video, and audio that really helped us tell our organization's story.</p><p class="review-author">Laura Baldwin</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">He made it comfortable and easy. The equipment was top-notch and professionally operated.</p><p class="review-author">Chris Minnis</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">What a fabulous experience! Diego makes it easy, and makes you look great too.</p><p class="review-author">Amy Angelilli</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">The videos were absolutely spectacular! They completely captured our vibe and definitely made us look cool!</p><p class="review-author">HMA Mortgage</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">The entire process from booking to the final video deliverables, everything was professionally done.</p><p class="review-author">Melanie Schuler</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">They took beautiful photos of my wife and I's special day! They made the photo shoot fun.</p><p class="review-author">Logan</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">Diego exceeded all my expectations with his fantastic photography! He flawlessly captured the essence of my event.</p><p class="review-author">LA Tango Academy</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">Diego did an amazing job at capturing the perfect moments during our tango event. He's calm and very professional.</p><p class="review-author">Manon Narbonne</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">The photos were lovely. The moments were captured so beautifully. He has a very calming energy.</p><p class="review-author">Sharath Raj</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">Diego went above and beyond to make my promo video beautiful and personalized. Highly recommend.</p><p class="review-author">Lauren Shirer</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">He has an eye for consistency and insightful commentary that is above and beyond most professionals.</p><p class="review-author">Jewel Rechsteiner</p></div>
      <div class="review-card-compact"><div class="review-stars">★★★★★</div><p class="review-text">His pricing was fair and transparent and the photos were perfect. I highly recommend Diego.</p><p class="review-author">Raychill Muller</p></div>
    </div>
    <div class="reviews-compact-cta"><a href="https://www.google.com/maps/place/First+Sight+Films/" target="_blank" rel="noopener">See all reviews on Google →</a></div>
  </section>'''

BASE_DIR = Path(__file__).parent.parent
PAGES_DIR = BASE_DIR / "src" / "pages"

def update_file(filepath):
    content = filepath.read_text(encoding='utf-8')
    if '{{reviews}}' in content:
        new_content = content.replace('{{reviews}}', REVIEWS_HTML)
        filepath.write_text(new_content, encoding='utf-8')
        print(f"  Updated: {filepath.relative_to(BASE_DIR)}")
        return True
    return False

def main():
    print("Updating {{reviews}} to Ultra Compact Grid...\n")
    count = 0
    for html_file in PAGES_DIR.rglob("*.html"):
        if update_file(html_file):
            count += 1
    print(f"\nDone! Updated {count} files.")

if __name__ == "__main__":
    main()
