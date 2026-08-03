"""Replace placeholder / missing seed images with real, topical photos.

Pulls keyword-matched real photos from loremflickr (no API key), falling back to
picsum if a lookup fails. Images are deterministic per record (a stable lock seed),
so re-runs are idempotent.

    manage.py seed_real_images            # fill where an image is missing
    manage.py seed_real_images --force    # also replace existing (e.g. random picsum) images

Targets: directory categories (cover), companies (cover), listings (gallery cards)
and blog posts (cover). Company logos are left untouched (a stock photo is not a logo).
"""
import hashlib
import time
import urllib.request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

# Topical search keyword per directory category.
CATEGORY_KEYWORDS = {
    'Health & Medical': 'clinic',
    'Staffing & Recruitment': 'office',
    'Real Estate': 'house',
    'Education': 'classroom',
    'Agriculture & Farming': 'farm',
    'Energy & Environment': 'solar',
    'Nonprofit & Community': 'community',
    'Professional Services': 'business',
    'Engineering': 'engineering',
    'Technology & IT': 'technology',
    'Restaurant & Food': 'restaurant',
    'Beauty & Wellness': 'spa',
    'Fashion & Clothing': 'fashion',
    'Music & Entertainment': 'concert',
}

# A few per-business overrides for a sharper match (by listing/company slug).
SLUG_KEYWORDS = {
    'kibuku-rabbit-farm': 'rabbit',
    'go-green-international-limited': 'solar-panel',
    'panda-childrens-clinic': 'pediatric',
    'freedom-international-school-africa-fisa': 'school',
    'wezesha-real-estate': 'realestate',
}

BLOG_KEYWORDS = {
    'Business Tips': 'business',
    'Diaspora Stories': 'entrepreneur',
    'Culture & Heritage': 'africa,culture',
    'Platform Updates': 'technology',
    'Success Stories': 'entrepreneur',
    'Diaspora News': 'city',
}


class Command(BaseCommand):
    help = 'Replace placeholder/missing seed images with real, topical photos (loremflickr).'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Replace existing images too (not just fill blanks).')
        parser.add_argument('--sleep', type=float, default=0.4,
                            help='Delay between downloads. Default 0.4s.')

    def handle(self, *args, **opts):
        self.force = opts['force']
        self.sleep = opts['sleep']
        self._categories()
        self._companies()
        self._listings()
        self._blogs()
        self.stdout.write(self.style.SUCCESS('\nDone.'))

    # --- image fetching -----------------------------------------------------

    def _lock(self, seed):
        return int(hashlib.md5(seed.encode()).hexdigest()[:7], 16)

    def _fetch(self, keyword, seed, w, h):
        """Return (filename, ContentFile) for a topical photo, or (None, None)."""
        lock = self._lock(seed)
        urls = [
            f'https://loremflickr.com/{w}/{h}/{keyword}?lock={lock}',
            f'https://picsum.photos/seed/{lock}/{w}/{h}',  # fallback: real but generic
        ]
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SankofaX-seed/1.0'})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = resp.read()
                if len(data) > 2000:  # guard against error placeholders
                    if self.sleep:
                        time.sleep(self.sleep)
                    return f'{keyword}-{lock}.jpg', ContentFile(data)
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'  [warn] {url}: {exc}'))
        return None, None

    def _keyword_for(self, category_name, slug=''):
        if slug in SLUG_KEYWORDS:
            return SLUG_KEYWORDS[slug]
        return CATEGORY_KEYWORDS.get(category_name, 'business')

    # --- targets ------------------------------------------------------------

    def _categories(self):
        from apps.directory.models import Category
        for cat in Category.objects.all():
            if cat.cover_image and not self.force:
                continue
            kw = CATEGORY_KEYWORDS.get(cat.name, 'business')
            fname, content = self._fetch(kw, f'cat-{cat.slug}', 1200, 400)
            if fname:
                cat.cover_image.save(fname, content, save=True)
                self.stdout.write(f'  [ok] category "{cat.name}" <- {kw}')

    def _companies(self):
        from apps.profiles.models import CompanyProfile
        for company in CompanyProfile.objects.all():
            if company.cover_image and not self.force:
                continue
            first = company.listings.first()
            cat_name = first.category.name if first else ''
            kw = self._keyword_for(cat_name, company.slug)
            fname, content = self._fetch(kw, f'company-{company.slug}', 1200, 400)
            if fname:
                company.cover_image.save(fname, content, save=True)
                self.stdout.write(f'  [ok] company "{company.company_name}" <- {kw}')

    def _listings(self):
        from apps.directory.models import Listing, ListingImage
        for listing in Listing.objects.select_related('category').all():
            existing = listing.gallery_images.count()
            if existing and not self.force:
                continue
            if self.force and existing:
                listing.gallery_images.all().delete()
            kw = self._keyword_for(listing.category.name, listing.slug)
            added = 0
            for i in range(2):
                fname, content = self._fetch(kw, f'listing-{listing.slug}-{i}', 800, 600)
                if fname:
                    img = ListingImage(listing=listing, order=i)
                    img.image.save(fname, content, save=True)
                    added += 1
            if added:
                self.stdout.write(f'  [ok] listing "{listing.title}" <- {kw} ({added} imgs)')

    def _blogs(self):
        from apps.blog.models import BlogPost
        for post in BlogPost.objects.select_related('category').all():
            if post.cover_image and not self.force:
                continue
            cat_name = post.category.name if post.category else ''
            kw = BLOG_KEYWORDS.get(cat_name, 'africa')
            fname, content = self._fetch(kw, f'blog-{post.slug}', 1200, 600)
            if fname:
                post.cover_image.save(fname, content, save=True)
                self.stdout.write(f'  [ok] blog "{post.title[:40]}" <- {kw}')
