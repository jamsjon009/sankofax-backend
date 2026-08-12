"""
Management command: seed demo data for new tables.
Run: python manage.py seed_blog_data
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
import random
import urllib.request


class Command(BaseCommand):
    help = 'Seed demo data for Blog, Newsletter, and other new tables'

    def handle(self, *args, **options):
        self._seed_blog()
        self._seed_newsletter()
        self._seed_accounts()
        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))

    def _fetch_image(self, seed, width=800, height=450):
        """Download a deterministic image from picsum.photos. Returns (filename, ContentFile) or (None, None)."""
        url = f'https://picsum.photos/seed/{seed}/{width}/{height}'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SankofaX-seed/1.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            return f'{seed}.jpg', ContentFile(data)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f'  [warn] image download failed ({seed}): {exc}'))
            return None, None

    # ------------------------------------------------------------------
    def _seed_blog(self):
        from apps.blog.models import BlogCategory, BlogPost
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get or create an admin author
        author = User.objects.filter(is_staff=True).first()

        # Categories
        cats_data = [
            ('Business Growth', 'Tips and strategies for growing your diaspora business', 1),
            ('Community',       'Stories and insights from the African diaspora community', 2),
            ('Tips & Guides',   'Practical guides for entrepreneurs and business owners', 3),
            ('Culture',         'Celebrating African and diaspora culture worldwide', 4),
            ('Finance',         'Financial literacy and investment for the diaspora', 5),
        ]
        categories = {}
        for name, desc, order in cats_data:
            slug = slugify(name)
            cat, created = BlogCategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'order': order}
            )
            categories[name] = cat
            if created:
                self.stdout.write(f'  Created category: {name}')

        # Blog posts
        posts_data = [
            {
                'title': 'Why Black-Owned Businesses Need a Global Presence',
                'image_seed': 'sankofax-global-business',
                'category': 'Business Growth',
                'excerpt': 'In an increasingly connected world, limiting your business to local markets means leaving money and opportunity on the table.',
                'content': '''<h2>The Global Opportunity</h2>
<p>The African diaspora represents a combined spending power of over $1.5 trillion. Yet the majority of Black-owned businesses remain locally focused, missing out on a vast, untapped global market.</p>
<h2>Why Go Global?</h2>
<ul>
<li><strong>Diaspora loyalty:</strong> Black consumers actively seek out Black-owned businesses — they just need to find you.</li>
<li><strong>Digital infrastructure:</strong> Platforms like SankofaX make it easier than ever to reach diaspora customers worldwide.</li>
<li><strong>Brand credibility:</strong> A global presence signals legitimacy and scale to potential partners and investors.</li>
</ul>
<h2>First Steps</h2>
<p>Start by listing your business on a diaspora-focused directory, optimising your Google Business profile for international searches, and creating content that speaks to the diaspora experience.</p>
<p>The world is waiting. Your next customer might be in London, Toronto, or Lagos — not your local high street.</p>''',
                'tags': 'business,global,diaspora,growth',
                'is_featured': True,
                'read_time_minutes': 5,
                'days_ago': 20,
            },
            {
                'title': 'The Power of the Diaspora Economy',
                'image_seed': 'sankofax-diaspora-community',
                'category': 'Community',
                'excerpt': 'The African diaspora represents a combined spending power of over $1.5 trillion. Here is how to tap into this community.',
                'content': '''<h2>Understanding Diaspora Economics</h2>
<p>Remittances from the African diaspora to the continent exceeded $95 billion in 2023, dwarfing foreign direct investment in many countries. Yet this financial power is rarely harnessed for community-owned enterprise.</p>
<h2>Collective Purchasing Power</h2>
<p>When diaspora communities deliberately direct spending toward Black-owned businesses, the multiplier effect is extraordinary. Research shows that a dollar spent in a Black community circulates six times before leaving, compared to once in many other communities.</p>
<h2>How You Can Participate</h2>
<ol>
<li>Discover and support businesses listed on SankofaX</li>
<li>Leave reviews to help others find quality businesses</li>
<li>Share listings on social media to amplify reach</li>
<li>List your own business to join the movement</li>
</ol>''',
                'tags': 'community,economy,diaspora,wealth',
                'is_featured': True,
                'read_time_minutes': 7,
                'days_ago': 27,
            },
            {
                'title': 'How to Optimise Your SankofaX Listing for Maximum Visibility',
                'image_seed': 'sankofax-tips-listing',
                'category': 'Tips & Guides',
                'excerpt': 'A complete listing gets 10x more views than an incomplete one. Follow these tips to make your business stand out.',
                'content': '''<h2>Completeness Is Everything</h2>
<p>Our data shows that businesses with complete profiles — logo, description, photos, opening hours, and contact details — receive 10x more profile views than those with minimal information.</p>
<h2>Writing a Compelling Description</h2>
<p>Your description should answer three questions immediately:</p>
<ul>
<li><em>What do you do?</em> — Be specific, not vague.</li>
<li><em>Who do you serve?</em> — Speak directly to your ideal customer.</li>
<li><em>Why choose you?</em> — Your unique story is your differentiator.</li>
</ul>
<h2>Photos Matter</h2>
<p>Upload at least 5 high-quality photos. Listings with photos see 3x more enquiries. Show your product, your space, your team, and your happy customers.</p>
<h2>Collect Reviews Early</h2>
<p>Ask your best customers to leave a review during your first week live. Social proof builds trust and drives conversions.</p>''',
                'tags': 'tips,listing,visibility,marketing',
                'is_featured': False,
                'read_time_minutes': 4,
                'days_ago': 34,
            },
            {
                'title': 'Building Generational Wealth Through Black Entrepreneurship',
                'image_seed': 'sankofax-wealth-finance',
                'category': 'Finance',
                'excerpt': 'Entrepreneurship is one of the most powerful tools for building lasting wealth across generations. Here is how to get started.',
                'content': '''<h2>The Wealth Gap and Entrepreneurship</h2>
<p>The racial wealth gap persists globally. Entrepreneurship, when done strategically, is one of the few vehicles capable of closing that gap within a single generation.</p>
<h2>Assets Over Income</h2>
<p>High income does not equal wealth. Focus on building assets: intellectual property, equity in businesses, real estate, and investment portfolios. A successful business is an asset that can be sold, inherited, or expanded.</p>
<h2>Structuring for the Long Term</h2>
<ul>
<li>Register your business as a limited company from day one</li>
<li>Open separate business banking accounts</li>
<li>Reinvest a percentage of profits into growth</li>
<li>Build a board or advisory network early</li>
</ul>''',
                'tags': 'wealth,finance,entrepreneurship,generational',
                'is_featured': False,
                'read_time_minutes': 6,
                'days_ago': 41,
            },
            {
                'title': 'African Fashion Designers Taking the World Stage',
                'image_seed': 'sankofax-african-fashion',
                'category': 'Culture',
                'excerpt': 'From Lagos to London, African designers are redefining global fashion — and building empires in the process.',
                'content': '''<h2>A Renaissance in African Design</h2>
<p>The global fashion industry is waking up to what the diaspora has always known: African design is world-class. From Ankara prints to contemporary minimalist collections, African designers are leading conversations at the highest levels of fashion.</p>
<h2>Designers to Watch</h2>
<p>The new wave of African designers is characterised by unapologetic cultural pride combined with global commercial sophistication. They are not adapting their work to fit Western tastes — they are reshaping what Western tastes look like.</p>
<h2>How You Can Support</h2>
<p>Buy directly from African designers. Follow them on social media. Attend showcases. List their boutiques on SankofaX so the diaspora can discover them wherever they are in the world.</p>''',
                'tags': 'culture,fashion,africa,design,creativity',
                'is_featured': False,
                'read_time_minutes': 5,
                'days_ago': 48,
            },
        ]

        for data in posts_data:
            slug = slugify(data['title'])
            if BlogPost.objects.filter(slug=slug).exists():
                # Backfill image if missing
                post = BlogPost.objects.get(slug=slug)
                if not post.cover_image:
                    fname, fcontent = self._fetch_image(data['image_seed'], 800, 450)
                    if fname:
                        post.cover_image.save(fname, fcontent, save=True)
                        self.stdout.write(f'  Updated image for existing post: {data["title"]}')
                    else:
                        self.stdout.write(f'  Skipping existing post (image failed): {data["title"]}')
                else:
                    self.stdout.write(f'  Skipping existing post: {data["title"]}')
                continue
            published_at = timezone.now() - timedelta(days=data['days_ago'])
            post = BlogPost.objects.create(
                title=data['title'],
                slug=slug,
                author=author,
                category=categories[data['category']],
                excerpt=data['excerpt'],
                content=data['content'],
                tags=data['tags'],
                is_featured=data['is_featured'],
                status=BlogPost.Status.PUBLISHED,
                read_time_minutes=data['read_time_minutes'],
                published_at=published_at,
                view_count=random.randint(50, 800),
            )
            fname, fcontent = self._fetch_image(data['image_seed'], 800, 450)
            if fname:
                post.cover_image.save(fname, fcontent, save=True)
                self.stdout.write(f'  Created post with image: {data["title"]}')
            else:
                self.stdout.write(f'  Created post (no image): {data["title"]}')

    # ------------------------------------------------------------------
    def _seed_newsletter(self):
        from apps.newsletter.models import Subscriber as NewsletterSubscriber

        emails = [
            ('amara.diallo@gmail.com', 'homepage'),
            ('kofi.mensah@outlook.com', 'homepage'),
            ('aisha.ba@yahoo.com', 'homepage'),
            ('obinna.eze@gmail.com', 'footer'),
            ('fatou.ndiaye@hotmail.com', 'footer'),
            ('kwame.asante@gmail.com', 'homepage'),
            ('zainab.ibrahim@gmail.com', 'footer'),
            ('chidi.okonkwo@outlook.com', 'homepage'),
        ]
        for email, source in emails:
            obj, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'source': source, 'is_active': True}
            )
            if created:
                self.stdout.write(f'  Created subscriber: {email}')

    # ------------------------------------------------------------------
    def _seed_accounts(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        users_data = [
            {
                'email': 'amara.diallo@example.com',
                'first_name': 'Amara',
                'last_name': 'Diallo',
                'country': 'FR',
                'is_verified': True,
            },
            {
                'email': 'kofi.mensah@example.com',
                'first_name': 'Kofi',
                'last_name': 'Mensah',
                'country': 'GB',
                'is_verified': True,
            },
            {
                'email': 'aisha.ba@example.com',
                'first_name': 'Aisha',
                'last_name': 'Ba',
                'country': 'US',
                'is_verified': False,
            },
            {
                'email': 'obinna.eze@example.com',
                'first_name': 'Obinna',
                'last_name': 'Eze',
                'country': 'CA',
                'is_verified': True,
            },
            {
                'email': 'fatou.ndiaye@example.com',
                'first_name': 'Fatou',
                'last_name': 'Ndiaye',
                'country': 'DE',
                'is_verified': False,
            },
        ]

        for data in users_data:
            if User.objects.filter(email=data['email']).exists():
                continue
            user = User.objects.create_user(
                email=data['email'],
                password='Demo1234!',
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
            # Set extra fields if they exist on the model
            if hasattr(user, 'country'):
                user.country = data['country']
            if hasattr(user, 'is_verified'):
                user.is_verified = data['is_verified']
            user.save()
            self.stdout.write(f'  Created user: {data["email"]}')
