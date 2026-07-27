from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta
import urllib.request


class Command(BaseCommand):
    help = 'Insert demo data for all sections'

    def handle(self, *args, **kwargs):
        self.stdout.write('\n>>> Seeding SankofaX demo data...\n')
        self._users()
        self._categories_amenities()
        self._companies()
        self._identity_badges()
        self._listings()
        self._subscriptions()
        self._reviews()
        self._crm()
        self._newsletter()
        self._events()
        self._marketplace()
        self._blog()
        self._core_content()
        self.stdout.write('\n>>> Done! Demo data seeded.\n')

    def _fetch_image(self, seed, width=800, height=600):
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

    def _users(self):
        from apps.accounts.models import User
        users_data = [
            dict(email='moderator@sankofax.com', password='Demo@1234', role=User.Role.MODERATOR,
                 first_name='Kwame', last_name='Asante', is_staff=True),
            dict(email='staff@sankofax.com', password='Demo@1234', role=User.Role.STAFF,
                 first_name='Amara', last_name='Diallo', is_staff=True),
            dict(email='admin@sankofax.com', password='Demo@1234', role=User.Role.ADMIN,
                 first_name='Fatima', last_name='Nkrumah', is_staff=True),
            dict(email='owner1@sankofax.com', password='Demo@1234', role=User.Role.BUSINESS_OWNER,
                 first_name='Zuri', last_name='Mensah'),
            dict(email='owner2@sankofax.com', password='Demo@1234', role=User.Role.BUSINESS_OWNER,
                 first_name='Kofi', last_name='Osei'),
            dict(email='owner3@sankofax.com', password='Demo@1234', role=User.Role.BUSINESS_OWNER,
                 first_name='Nia', last_name='Kamara'),
            dict(email='user1@sankofax.com', password='Demo@1234', role=User.Role.VISITOR,
                 first_name='Marcus', last_name='Williams'),
            dict(email='user2@sankofax.com', password='Demo@1234', role=User.Role.VISITOR,
                 first_name='Aisha', last_name='Johnson'),
            dict(email='user3@sankofax.com', password='Demo@1234', role=User.Role.VISITOR,
                 first_name='Darius', last_name='Brown'),
            dict(email='user4@sankofax.com', password='Demo@1234', role=User.Role.VISITOR,
                 first_name='Yemi', last_name='Adeyemi'),
        ]
        self._users_created = {}
        for d in users_data:
            pw = d.pop('password')
            email = d['email']
            if not User.objects.filter(email=email).exists():
                u = User.objects.create_user(password=pw, **d)
                u.is_verified = True
                u.save()
                self._users_created[email] = pw
                self.stdout.write('  + User  ' + email)
            else:
                self.stdout.write('  ~ skip  ' + email + ' (exists)')

    def _categories_amenities(self):
        from apps.directory.models import Category, Amenity
        cats = [
            ('Restaurant & Food', 'utensils', 'business'),
            ('Beauty & Wellness', 'scissors', 'business'),
            ('Fashion & Clothing', 'shirt', 'business'),
            ('Technology & IT', 'laptop', 'business'),
            ('Music & Entertainment', 'music', 'event'),
        ]
        cat_seeds = {
            'Restaurant & Food': 'cat-restaurant-food',
            'Beauty & Wellness': 'cat-beauty-wellness',
            'Fashion & Clothing': 'cat-fashion-clothing',
            'Technology & IT': 'cat-technology-it',
            'Music & Entertainment': 'cat-music-entertainment',
        }
        self._categories = {}
        for name, icon, ltype in cats:
            cat, created = Category.objects.get_or_create(
                name=name, defaults={'icon': icon, 'listing_type': ltype}
            )
            self._categories[name] = cat
            if created:
                self.stdout.write('  + Category  ' + name)
            if not cat.cover_image and name in cat_seeds:
                fname, fcontent = self._fetch_image(cat_seeds[name], 1200, 400)
                if fname:
                    cat.cover_image.save(fname, fcontent, save=True)
                    self.stdout.write('  ~ image added for  ' + name)
        amenities = ['Wi-Fi', 'Parking', 'Wheelchair Accessible', 'Outdoor Seating',
                     'Delivery Available', 'Accepts Cards', 'Pet Friendly']
        self._amenities = []
        for name in amenities:
            a, created = Amenity.objects.get_or_create(name=name)
            self._amenities.append(a)
            if created:
                self.stdout.write('  + Amenity  ' + name)

    def _companies(self):
        from apps.accounts.models import User
        from apps.profiles.models import CompanyProfile
        companies_data = [
            dict(owner_email='owner1@sankofax.com', company_name='Sankofa Kitchen',
                 logo_seed='logo-sankofa-kitchen', cover_seed='cover-sankofa-kitchen',
                 description='Authentic West African cuisine in the heart of London.',
                 founder_story='Zuri Mensah left Accra for London with her grandmother\'s recipes and a dream. What began as weekend suppers for homesick friends grew into Sankofa Kitchen — now one of Brixton\'s most-loved tables, keeping three generations of West African cooking alive in the diaspora.',
                 website='https://sankofakitchen.co.uk', contact_email='hello@sankofakitchen.co.uk',
                 services='Dine-in, Takeaway, Catering, Private events, Delivery',
                 instagram_url='https://instagram.com/sankofakitchen', facebook_url='https://facebook.com/sankofakitchen',
                 contact_phone='+44 20 7946 0958', company_size='1-10', founded_year=2018, is_verified=True),
            dict(owner_email='owner2@sankofax.com', company_name='AfroTech Solutions',
                 logo_seed='logo-afrotech', cover_seed='cover-afrotech',
                 description='Pan-African software development house building fintech and edtech products.',
                 founder_story='After years building payment systems abroad, Kofi Osei returned home determined to solve the problems he grew up with. AfroTech Solutions now spans Lagos, Nairobi and New York, engineering offline-first fintech for the realities of African markets.',
                 website='https://afrotech.io', contact_email='info@afrotech.io',
                 services='Custom software, Mobile apps, Fintech platforms, API integration, Consulting',
                 instagram_url='https://instagram.com/afrotech', linkedin_url='https://linkedin.com/company/afrotech',
                 twitter_url='https://x.com/afrotech',
                 contact_phone='+1 646 555 0201', company_size='11-50', founded_year=2020, is_verified=True),
            dict(owner_email='owner3@sankofax.com', company_name='Kente and Co.',
                 logo_seed='logo-kente-co', cover_seed='cover-kente-co',
                 description='Luxury African fashion, bespoke Ankara and Kente garments shipped worldwide.',
                 founder_story='Nia Kamara learned to weave Kente at her grandfather\'s loom in Ghana. Frustrated that diaspora weddings rarely featured authentic cloth, she founded Kente and Co. to bring hand-crafted Ankara and Kente garments to celebrations around the world.',
                 website='https://kenteandco.com', contact_email='orders@kenteandco.com',
                 services='Bespoke tailoring, Ready-to-wear, Wedding outfits, Worldwide shipping',
                 instagram_url='https://instagram.com/kenteandco', tiktok_url='https://tiktok.com/@kenteandco',
                 contact_phone='+1 929 555 0187', company_size='solo', founded_year=2021, is_verified=False),
        ]
        self._companies = {}
        for d in companies_data:
            owner_email = d.pop('owner_email')
            logo_seed = d.pop('logo_seed')
            cover_seed = d.pop('cover_seed')
            try:
                owner = User.objects.get(email=owner_email)
            except User.DoesNotExist:
                continue
            if not CompanyProfile.objects.filter(owner=owner).exists():
                cp = CompanyProfile.objects.create(owner=owner, **d)
                fname, fcontent = self._fetch_image(logo_seed, 400, 400)
                if fname:
                    cp.logo.save(fname, fcontent, save=False)
                fname2, fcontent2 = self._fetch_image(cover_seed, 1200, 400)
                if fname2:
                    cp.cover_image.save(fname2, fcontent2, save=False)
                cp.save()
                self._companies[owner_email] = cp
                self.stdout.write('  + Company  ' + cp.company_name)
            else:
                cp = CompanyProfile.objects.filter(owner=owner).first()
                # Backfill images if missing
                changed = False
                if not cp.logo:
                    fname, fcontent = self._fetch_image(logo_seed, 400, 400)
                    if fname:
                        cp.logo.save(fname, fcontent, save=False)
                        changed = True
                if not cp.cover_image:
                    fname2, fcontent2 = self._fetch_image(cover_seed, 1200, 400)
                    if fname2:
                        cp.cover_image.save(fname2, fcontent2, save=False)
                        changed = True
                # Backfill founder story if missing
                if not cp.founder_story and d.get('founder_story'):
                    cp.founder_story = d['founder_story']
                    changed = True
                # Backfill services & social links if missing
                for f in ('services', 'instagram_url', 'facebook_url', 'twitter_url',
                          'linkedin_url', 'youtube_url', 'tiktok_url'):
                    if not getattr(cp, f) and d.get(f):
                        setattr(cp, f, d[f])
                        changed = True
                if changed:
                    cp.save()
                    self.stdout.write('  ~ updated images for  ' + cp.company_name)
                else:
                    self.stdout.write('  ~ skip  ' + cp.company_name + ' (exists)')
                self._companies[owner_email] = cp

    def _identity_badges(self):
        from apps.profiles.models import IdentityBadge
        badges = [
            ('Black-Owned', 'black-owned', '✊🏾', '#2a2420', 1),
            ('Women-Owned', 'women-owned', '♀', '#b5813b', 2),
            ('LGBTQ+-Owned', 'lgbtq-owned', '🏳️‍🌈', '#7c3aed', 3),
            ('Veteran-Owned', 'veteran-owned', '🎖️', '#166534', 4),
            ('Youth-Owned', 'youth-owned', '🌱', '#16a34a', 5),
            ('Immigrant-Owned', 'immigrant-owned', '🌍', '#0369a1', 6),
            ('Disability-Owned', 'disability-owned', '♿', '#0891b2', 7),
            ('Minority-Owned', 'minority-owned', '🤝', '#9333ea', 8),
        ]
        self._badges = {}
        for name, slug, icon, color, order in badges:
            b, created = IdentityBadge.objects.get_or_create(
                name=name, defaults={'slug': slug, 'icon': icon, 'color': color, 'order': order}
            )
            # Backfill correct slug if an earlier run stored a non-normalised one
            if b.slug != slug:
                b.slug = slug
                b.save(update_fields=['slug'])
            self._badges[name] = b
            if created:
                self.stdout.write('  + Badge  ' + name)
        # Attach to demo companies
        assignments = {
            'owner1@sankofax.com': ['Black-Owned', 'Women-Owned'],
            'owner2@sankofax.com': ['Black-Owned', 'Immigrant-Owned'],
            'owner3@sankofax.com': ['Black-Owned', 'Women-Owned', 'LGBTQ+-Owned'],
        }
        for email, names in assignments.items():
            cp = self._companies.get(email)
            if not cp:
                continue
            if cp.badges.exists():
                continue
            cp.badges.set([self._badges[n] for n in names if n in self._badges])
            self.stdout.write('  ~ badges set for  ' + cp.company_name)

    def _listings(self):
        from apps.directory.models import Listing, ListingImage
        now = timezone.now()
        listings_data = [
            dict(company_key='owner1@sankofax.com', category_name='Restaurant & Food',
                 image_seeds=['listing-kitchen-brixton-1', 'listing-kitchen-brixton-2', 'listing-kitchen-brixton-3'],
                 title='Sankofa Kitchen Brixton',
                 short_description='Authentic West African restaurant serving jollof, suya and fufu.',
                 full_description='Step into Sankofa Kitchen for a true taste of West Africa. Our chefs prepare traditional dishes using imported spices and locally sourced ingredients. Famous for our smoky suya skewers, peanut soup, and award-winning jollof rice.',
                 listing_status='published', city='London', country='United Kingdom',
                 address_line='45 Atlantic Road, Brixton', phone='+44 20 7946 0958',
                 email='hello@sankofakitchen.co.uk', price_range='$$', featured=True, business_type='both',
                 published_at=now - timedelta(days=10), avg_rating='4.80', review_count=24),
            dict(company_key='owner1@sankofax.com', category_name='Restaurant & Food',
                 image_seeds=['listing-kitchen-peckham-1', 'listing-kitchen-peckham-2'],
                 title='Sankofa Kitchen Peckham',
                 short_description='Our second location, same great food, new neighbourhood.',
                 full_description='The Peckham branch of Sankofa Kitchen brings the same delicious West African flavours to South East London. Dine in or take away. Catering available for events.',
                 listing_status='pending_review', city='London', country='United Kingdom',
                 address_line='12 Rye Lane, Peckham', phone='+44 20 7946 0959',
                 email='peckham@sankofakitchen.co.uk', price_range='$$', featured=False, business_type='both',
                 published_at=None, avg_rating='0', review_count=0),
            dict(company_key='owner2@sankofax.com', category_name='Technology & IT',
                 image_seeds=['listing-afrotech-dev-1', 'listing-afrotech-dev-2', 'listing-afrotech-dev-3'],
                 title='AfroTech Software Development',
                 short_description='Custom software, mobile apps and fintech built by African engineers.',
                 full_description='AfroTech Solutions is a Pan-African software house with teams in Lagos, Nairobi and New York. We build scalable fintech platforms, edtech tools and enterprise software.',
                 listing_status='published', city='New York', country='United States',
                 address_line='350 5th Avenue, Suite 4100', phone='+1 646 555 0201',
                 email='info@afrotech.io', price_range='$$$', featured=True, business_type='service',
                 published_at=now - timedelta(days=5), avg_rating='4.90', review_count=11),
            dict(company_key='owner3@sankofax.com', category_name='Fashion & Clothing',
                 image_seeds=['listing-kente-fashion-1', 'listing-kente-fashion-2', 'listing-kente-fashion-3'],
                 title='Kente and Co Luxury African Fashion',
                 short_description='Bespoke Ankara, Kente and Adire garments crafted for the diaspora.',
                 full_description='Kente and Co celebrates African textile heritage with contemporary silhouettes. Each piece is hand-crafted using authentic Ghanaian Kente cloth and Nigerian Ankara fabric.',
                 listing_status='published', city='Atlanta', country='United States',
                 address_line='221 Auburn Avenue NE', phone='+1 929 555 0187',
                 email='orders@kenteandco.com', price_range='$$$', featured=False, business_type='product',
                 published_at=now - timedelta(days=3), avg_rating='4.60', review_count=8),
            dict(company_key='owner2@sankofax.com', category_name='Technology & IT',
                 image_seeds=['listing-afrotech-mobile-1', 'listing-afrotech-mobile-2'],
                 title='AfroTech Mobile App Development',
                 short_description='Cross-platform mobile apps for African markets.',
                 full_description='Specialising in React Native and Flutter apps tailored for low-bandwidth African markets. Offline-first architecture, M-Pesa and Flutterwave payment integration.',
                 listing_status='pending_review', city='Nairobi', country='Kenya',
                 address_line='Westlands Business Park', phone='+254 700 123456',
                 email='mobile@afrotech.io', price_range='$$', featured=False, business_type='service',
                 published_at=None, avg_rating='0', review_count=0),
        ]
        from django.utils.text import slugify
        self._listings = {}
        for d in listings_data:
            company_key = d.pop('company_key')
            category_name = d.pop('category_name')
            image_seeds = d.pop('image_seeds', [])
            title = d['title']
            slug = slugify(title)
            company = self._companies.get(company_key)
            category = self._categories.get(category_name)
            if not company or not category:
                continue
            if not Listing.objects.filter(slug=slug).exists():
                lst = Listing.objects.create(company=company, category=category, **d)
                if self._amenities:
                    lst.amenities.set(self._amenities[:3])
                # Gallery images
                for seed in image_seeds:
                    fname, fcontent = self._fetch_image(seed, 800, 600)
                    if fname:
                        img = ListingImage(listing=lst)
                        img.image.save(fname, fcontent, save=True)
                self._listings[title] = lst
                self.stdout.write('  + Listing  ' + title + f' ({len(image_seeds)} images)')
            else:
                lst = Listing.objects.get(slug=slug)
                self._listings[title] = lst
                # Backfill business_type on pre-existing rows
                bt = d.get('business_type')
                if bt and lst.business_type != bt:
                    lst.business_type = bt
                    lst.save(update_fields=['business_type'])
                    self.stdout.write('  ~ business_type set for  ' + title)
                # Backfill gallery images if none exist
                if image_seeds and not lst.gallery_images.exists():
                    for seed in image_seeds:
                        fname, fcontent = self._fetch_image(seed, 800, 600)
                        if fname:
                            img = ListingImage(listing=lst)
                            img.image.save(fname, fcontent, save=True)
                    self.stdout.write('  ~ updated gallery for  ' + title)
                else:
                    self.stdout.write('  ~ skip  ' + title + ' (exists)')

    def _subscriptions(self):
        from apps.accounts.models import User
        from apps.subscriptions.models import Plan, Subscription
        plans_data = [
            dict(name='Starter', tier_level=1, price='0.00', billing_cycle='monthly',
                 max_listings=1, featured_listing_slots=0,
                 description='Free plan, get discovered on SankofaX.',
                 features_list=['1 listing', 'Basic analytics', 'Community support']),
            dict(name='Growth', tier_level=2, price='29.00', billing_cycle='monthly',
                 max_listings=5, featured_listing_slots=1, analytics_access=True,
                 description='Perfect for growing businesses.',
                 features_list=['5 listings', '1 featured slot', 'Full analytics', 'Email support']),
            dict(name='Pro', tier_level=3, price='79.00', billing_cycle='monthly',
                 max_listings=20, featured_listing_slots=5, analytics_access=True, priority_support=True,
                 description='For established businesses ready to dominate.',
                 features_list=['20 listings', '5 featured slots', 'Priority support', 'CRM access']),
            dict(name='Enterprise', tier_level=4, price='199.00', billing_cycle='monthly',
                 max_listings=100, featured_listing_slots=20, analytics_access=True, priority_support=True,
                 description='Unlimited power for large organisations.',
                 features_list=['Unlimited listings', 'Dedicated manager', 'API access', 'White-label']),
        ]
        self._plans = {}
        for d in plans_data:
            plan, created = Plan.objects.get_or_create(name=d['name'], defaults=d)
            self._plans[plan.name] = plan
            if created:
                self.stdout.write('  + Plan  ' + plan.name)
        now = timezone.now()
        subs_data = [
            ('owner1@sankofax.com', 'Growth', 'active', now + timedelta(days=20)),
            ('owner2@sankofax.com', 'Pro', 'active', now + timedelta(days=15)),
            ('owner3@sankofax.com', 'Starter', 'trialing', now + timedelta(days=7)),
        ]
        for email, plan_name, status, period_end in subs_data:
            try:
                user = User.objects.get(email=email)
                plan = self._plans[plan_name]
                company = self._companies.get(email)
            except (User.DoesNotExist, KeyError):
                continue
            if not Subscription.objects.filter(user=user).exists():
                Subscription.objects.create(user=user, plan=plan, company=company,
                                            status=status, current_period_end=period_end)
                self.stdout.write('  + Subscription  ' + email + ' -> ' + plan_name)

    def _reviews(self):
        from apps.accounts.models import User
        from apps.reviews.models import Review
        reviews_data = [
            dict(listing_title='Sankofa Kitchen Brixton', user_email='user1@sankofax.com',
                 rating=5, status='approved', title='Best jollof in London!',
                 body='I have eaten at many African restaurants but Sankofa Kitchen is on another level. The jollof rice is smoky, the suya perfectly spiced. Will be back every week!'),
            dict(listing_title='Sankofa Kitchen Brixton', user_email='user2@sankofax.com',
                 rating=5, status='approved', title='Authentic and delicious',
                 body='Reminded me of home. The peanut soup was rich and the service was warm and friendly.'),
            dict(listing_title='AfroTech Software Development', user_email='user3@sankofax.com',
                 rating=5, status='approved', title='Delivered beyond expectations',
                 body='AfroTech built our fintech dashboard in 6 weeks. Clean code, excellent communication.'),
            dict(listing_title='AfroTech Software Development', user_email='user4@sankofax.com',
                 rating=4, status='approved', title='Great team, highly professional',
                 body='Very responsive team. Minor delays in delivery but the quality was outstanding.'),
            dict(listing_title='Kente and Co Luxury African Fashion', user_email='user1@sankofax.com',
                 rating=5, status='approved', title='My wedding outfit was stunning',
                 body='Ordered a custom Kente suit for my wedding. The craftsmanship was impeccable!'),
            dict(listing_title='Kente and Co Luxury African Fashion', user_email='user2@sankofax.com',
                 rating=4, status='pending', title='Beautiful fabric, worth every penny',
                 body='The Ankara wrap dress I ordered is gorgeous. Shipping took a few extra days.'),
        ]
        for d in reviews_data:
            listing_title = d.pop('listing_title')
            user_email = d.pop('user_email')
            listing = self._listings.get(listing_title)
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                continue
            if listing and not Review.objects.filter(listing=listing, user=user).exists():
                Review.objects.create(listing=listing, user=user, **d)
                self.stdout.write('  + Review  ' + user_email)

    def _crm(self):
        from apps.accounts.models import User
        from apps.crm.models import Lead, SupportTicket
        leads_data = [
            dict(name='James Okafor', email='james.okafor@gmail.com', phone='+44 7700 900123',
                 source='listing_inquiry', status='new'),
            dict(name='Beatrice Mensah', email='bea.mensah@outlook.com', phone='+1 917 555 0144',
                 source='contact_form', status='new'),
            dict(name='Tunde Adewale', email='tadewale@yahoo.com', phone='+234 802 555 6789',
                 source='newsletter', status='contacted'),
            dict(name='Priya Nair', email='priya.nair@icloud.com', phone='+1 415 555 0182',
                 source='listing_inquiry', status='new'),
        ]
        for d in leads_data:
            if not Lead.objects.filter(email=d['email']).exists():
                Lead.objects.create(**d)
                self.stdout.write('  + Lead  ' + d['name'])
        try:
            u1 = User.objects.get(email='user1@sankofax.com')
            u2 = User.objects.get(email='user2@sankofax.com')
            u3 = User.objects.get(email='user3@sankofax.com')
        except User.DoesNotExist:
            return
        tickets_data = [
            dict(user=u1, subject='Cannot upload listing images',
                 message='I keep getting an error when I try to upload photos. Tried Chrome and Firefox.',
                 status='open', priority='high'),
            dict(user=u2, subject='Payment not going through',
                 message='My subscription payment failed twice. Card is valid and has funds.',
                 status='open', priority='urgent'),
            dict(user=u3, subject='How do I update business hours?',
                 message='I cannot find where to edit my opening hours on the listing page.',
                 status='open', priority='low'),
            dict(user=u1, subject='Request to feature our listing',
                 message='We would like to upgrade to a featured listing slot.',
                 status='in_progress', priority='medium'),
        ]
        for d in tickets_data:
            if not SupportTicket.objects.filter(user=d['user'], subject=d['subject']).exists():
                SupportTicket.objects.create(**d)
                self.stdout.write('  + Ticket  ' + d['subject'][:40])

    def _newsletter(self):
        from apps.newsletter.models import Subscriber
        subs = [
            ('james.okafor@gmail.com', 'listing'),
            ('bea.mensah@outlook.com', 'homepage'),
            ('tadewale@yahoo.com', 'footer'),
            ('priya.nair@icloud.com', 'homepage'),
            ('user1@sankofax.com', 'homepage'),
            ('user2@sankofax.com', 'listing'),
            ('africa.diaspora.news@gmail.com', 'footer'),
            ('kweku.acheampong@yahoo.com', 'homepage'),
        ]
        for email, source in subs:
            if not Subscriber.objects.filter(email=email).exists():
                Subscriber.objects.create(email=email, source=source, is_active=True)
                self.stdout.write('  + Subscriber  ' + email)

    def _events(self):
        from apps.events.models import Event
        now = timezone.now()
        cat = self._categories.get('Music & Entertainment') or list(self._categories.values())[0]
        company = self._companies.get('owner2@sankofax.com') or list(self._companies.values())[0]
        events_data = [
            dict(organizer=company, category=cat,
                 title='AfroFuture Music Summit 2026',
                 description='Three days of Afrobeats, Amapiano and Afro-soul with live performances and panels.',
                 city='London', country='United Kingdom', venue_name='The O2 Arena',
                 start_datetime=now + timedelta(days=30), end_datetime=now + timedelta(days=33),
                 ticket_url='https://afrofuture.co.uk/tickets', ticket_price='45.00', status='published'),
            dict(organizer=company, category=cat,
                 title='Black Tech Founders Summit',
                 description='Connecting Black founders, investors and mentors across the diaspora.',
                 city='New York', country='United States', venue_name='Brooklyn Museum',
                 start_datetime=now + timedelta(days=15), end_datetime=now + timedelta(days=15, hours=8),
                 ticket_price='25.00', status='published',
                 rsvp_enabled=True, capacity=3, allow_waitlist=True),
            dict(organizer=company, category=cat,
                 title='Diaspora Wellness and Culture Fair',
                 description='Yoga, meditation, African herbal medicine stalls, food vendors and live drumming.',
                 city='Atlanta', country='United States', venue_name='Piedmont Park',
                 start_datetime=now + timedelta(days=8), end_datetime=now + timedelta(days=8, hours=6),
                 ticket_url='', ticket_price='0.00', status='published',
                 rsvp_enabled=True, capacity=None, allow_waitlist=True),
        ]
        for d in events_data:
            if not Event.objects.filter(title=d['title']).exists():
                Event.objects.create(**d)
                self.stdout.write('  + Event  ' + d['title'])
        self._event_registrations()

    def _event_registrations(self):
        from apps.accounts.models import User
        from apps.events.models import Event, EventRegistration
        # Fill the capacity-limited event so the waitlist path is visible in the demo.
        event = Event.objects.filter(title='Black Tech Founders Summit').first()
        if not event or event.registrations.exists():
            return
        signups = [
            ('user1@sankofax.com', 2),   # -> confirmed (2/3)
            ('user2@sankofax.com', 1),   # -> confirmed (3/3, now full)
            ('user3@sankofax.com', 1),   # -> waitlisted
        ]
        for email, qty in signups:
            user = User.objects.filter(email=email).first()
            if not user:
                continue
            confirmed = event.confirmed_count
            if event.capacity is None or confirmed + qty <= event.capacity:
                st = EventRegistration.Status.CONFIRMED
            else:
                st = EventRegistration.Status.WAITLISTED
            EventRegistration.objects.create(
                event=event, attendee=user,
                name=(user.get_full_name() or '').strip() or user.email.split('@')[0],
                email=user.email, quantity=qty, status=st,
            )
            self.stdout.write(f'  + RSVP   {email} -> {event.title} ({st})')

    def _marketplace(self):
        from apps.accounts.models import User
        from apps.marketplace.models import Product, Service, Order, OrderItem, ServiceBooking

        fashion = self._categories.get('Fashion & Clothing')
        food = self._categories.get('Restaurant & Food')
        tech = self._categories.get('Technology & IT')
        kente = self._companies.get('owner3@sankofax.com')
        kitchen = self._companies.get('owner1@sankofax.com')
        afrotech = self._companies.get('owner2@sankofax.com')

        # --- Products (buy in-platform) ---
        products = [
            dict(company=kente, category=fashion, name='Hand-woven Kente Scarf',
                 description='Authentic hand-woven Kente scarf in royal gold and green. One size.',
                 price='45.00', currency='USD', stock_status='in_stock'),
            dict(company=kente, category=fashion, name='Bespoke Ankara Dress',
                 description='Made-to-order Ankara dress tailored to your measurements. Choose your print.',
                 price='180.00', currency='USD', stock_status='made_to_order'),
            dict(company=kitchen, category=food, name='West African Spice Blend (3-pack)',
                 description='Suya, jollof and pepper-soup spice blends. Ships worldwide.',
                 price='24.00', currency='USD', stock_status='in_stock'),
        ]
        self._products = {}
        for d in products:
            if d['company'] and not Product.objects.filter(name=d['name']).exists():
                p = Product.objects.create(**d)
                self._products[d['name']] = p
                self.stdout.write('  + Product  ' + d['name'])
            else:
                self._products[d['name']] = Product.objects.filter(name=d['name']).first()

        # --- Services (book in-platform) ---
        services = [
            dict(company=afrotech, category=tech, name='Fintech Product Consultation',
                 description='A 60-minute strategy session with our senior product team.',
                 price='150.00', currency='USD', duration_minutes=60, is_virtual=True),
            dict(company=afrotech, category=tech, name='Free Intro Call',
                 description='A 20-minute introductory call to discuss your project — no charge.',
                 price='0.00', currency='USD', duration_minutes=20, is_virtual=True),
            dict(company=kitchen, category=food, name='Private Catering Consultation',
                 description='Plan your event menu with our head chef (in-person, London).',
                 price='75.00', currency='USD', duration_minutes=45, is_virtual=False, location='London, UK'),
        ]
        self._services = {}
        for d in services:
            if d['company'] and not Service.objects.filter(name=d['name']).exists():
                s = Service.objects.create(**d)
                self._services[d['name']] = s
                self.stdout.write('  + Service  ' + d['name'])
            else:
                self._services[d['name']] = Service.objects.filter(name=d['name']).first()

        # --- Sample order + bookings (so dashboards aren't empty) ---
        u1 = User.objects.filter(email='user1@sankofax.com').first()
        u2 = User.objects.filter(email='user2@sankofax.com').first()
        scarf = self._products.get('Hand-woven Kente Scarf')
        if u1 and scarf and not Order.objects.filter(buyer=u1, company=scarf.company).exists():
            order = Order.objects.create(
                buyer=u1, company=scarf.company, currency='USD', total='90.00',
                contact_name='Marcus Williams', contact_email=u1.email,
                shipping_address='12 Peckham Rd, London', status=Order.Status.PAID,
                paid_at=timezone.now(),
            )
            OrderItem.objects.create(order=order, product=scarf, name=scarf.name,
                                     unit_price=scarf.price, quantity=2)
            self.stdout.write('  + Order    ' + order.order_number + ' (paid)')

        free_call = self._services.get('Free Intro Call')
        if u2 and free_call and not ServiceBooking.objects.filter(customer=u2, service=free_call).exists():
            ServiceBooking.objects.create(
                service=free_call, company=free_call.company, customer=u2,
                service_name=free_call.name, scheduled_for=timezone.now() + timedelta(days=5),
                currency='USD', total='0.00', contact_name='Aisha Johnson',
                contact_email=u2.email, status=ServiceBooking.Status.PENDING,
                note='Interested in a mobile banking MVP.',
            )
            self.stdout.write('  + Booking  Free Intro Call (pending request)')

    def _blog(self):
        from apps.accounts.models import User
        from apps.blog.models import BlogCategory, BlogPost
        now = timezone.now()

        categories = [
            ('Business Tips', 'Practical advice for growing your business on SankofaX.'),
            ('Diaspora Stories', 'Inspiring journeys from Black and African entrepreneurs.'),
            ('Culture & Heritage', 'Celebrating African culture, food, fashion and music.'),
            ('Platform Updates', 'News and feature announcements from the SankofaX team.'),
            ('Success Stories', 'Business stories & legacy — founders and companies thriving across the diaspora.'),
            ('Diaspora News', 'News and updates from across the global African diaspora.'),
        ]
        self._blog_categories = {}
        for name, desc in categories:
            cat, created = BlogCategory.objects.get_or_create(
                name=name, defaults={'description': desc}
            )
            self._blog_categories[name] = cat
            if created:
                self.stdout.write('  + BlogCategory  ' + name)

        try:
            author = User.objects.get(email='admin@sankofax.com')
        except User.DoesNotExist:
            author = User.objects.filter(is_staff=True).first()

        posts = [
            dict(title='5 Ways to Make Your Business Listing Stand Out',
                 category='Business Tips', cover_seed='blog-listing-tips',
                 tags='listings, marketing, seo, growth', is_featured=True,
                 read_time_minutes=6, view_count=428, days_ago=12,
                 excerpt='Your listing is your storefront on SankofaX. Here is how to make it shine and attract more customers.',
                 content='<h2>Make a strong first impression</h2><p>Your SankofaX listing is often the first thing a potential customer sees. A complete, well-crafted listing builds trust instantly.</p>'
                         '<ol><li><strong>Use high-quality photos.</strong> Listings with a full gallery get up to 3x more views.</li>'
                         '<li><strong>Write a clear description.</strong> Explain what makes your business unique.</li>'
                         '<li><strong>Add all your contact details.</strong> Make it effortless for customers to reach you.</li>'
                         '<li><strong>Collect reviews.</strong> Social proof drives conversions.</li>'
                         '<li><strong>Keep it updated.</strong> Fresh listings rank higher.</li></ol>'
                         '<p>Follow these steps and watch your engagement grow.</p>'),
            dict(title='From Accra to London: The Sankofa Kitchen Story',
                 category='Diaspora Stories', cover_seed='blog-sankofa-story',
                 tags='food, entrepreneurship, london, west-africa', is_featured=True,
                 read_time_minutes=8, view_count=612, days_ago=20,
                 excerpt='How one family turned a love of West African cooking into a thriving London restaurant chain.',
                 content='<p>When Zuri Mensah moved from Accra to London, she missed the flavours of home. What started as weekend cooking for friends became <strong>Sankofa Kitchen</strong> — now one of Brixton\'s most loved restaurants.</p>'
                         '<h2>Rooted in tradition</h2><p>"Every dish tells a story," says Zuri. "Our jollof recipe has been in my family for three generations."</p>'
                         '<p>Today the business is expanding to Peckham, bringing authentic West African cuisine to even more people across the diaspora.</p>'),
            dict(title='Why African Fashion Is Taking Over the Global Stage',
                 category='Culture & Heritage', cover_seed='blog-african-fashion',
                 tags='fashion, kente, ankara, culture', is_featured=False,
                 read_time_minutes=5, view_count=289, days_ago=6,
                 excerpt='From runways in Paris to weddings in Atlanta, African prints and craftsmanship are having a global moment.',
                 content='<p>African fashion is no longer a niche — it is a global movement. Brands like <strong>Kente and Co.</strong> are leading the way with bespoke Ankara and Kente garments shipped worldwide.</p>'
                         '<h2>Heritage meets modern design</h2><p>Contemporary silhouettes crafted from authentic Ghanaian and Nigerian fabrics are winning over a new generation.</p>'),
            dict(title='Introducing Featured Listings and CRM Tools',
                 category='Platform Updates', cover_seed='blog-platform-update',
                 tags='product, features, crm, announcement', is_featured=False,
                 read_time_minutes=3, view_count=154, days_ago=2,
                 excerpt='We are rolling out powerful new tools to help business owners get discovered and manage their customers.',
                 content='<p>We are excited to announce two major features on SankofaX:</p>'
                         '<ul><li><strong>Featured Listings</strong> — get premium placement in search and category pages.</li>'
                         '<li><strong>Built-in CRM</strong> — manage leads and support tickets right from your dashboard.</li></ul>'
                         '<p>Both are available now on our Growth, Pro and Enterprise plans.</p>'),
            dict(title='Building Fintech for the African Market',
                 category='Diaspora Stories', cover_seed='blog-fintech',
                 tags='technology, fintech, africa, startups', is_featured=False,
                 read_time_minutes=7, view_count=203, days_ago=9,
                 excerpt='AfroTech Solutions is building the payment rails that power the next generation of African businesses.',
                 content='<p>With teams in Lagos, Nairobi and New York, <strong>AfroTech Solutions</strong> is tackling one of the continent\'s biggest challenges: seamless digital payments.</p>'
                         '<h2>Offline-first, always</h2><p>"We design for low-bandwidth realities," explains founder Kofi Osei. Their apps integrate M-Pesa and Flutterwave and work even with spotty connectivity.</p>'),
            dict(title='A Beginner\'s Guide to SEO for Small Businesses',
                 category='Business Tips', cover_seed='blog-seo-guide',
                 tags='seo, marketing, growth, tips', is_featured=False,
                 read_time_minutes=6, view_count=97, days_ago=1, status='draft',
                 excerpt='Search engine optimisation sounds intimidating, but a few simple habits can dramatically boost your visibility.',
                 content='<p>SEO does not have to be complicated. Start with these fundamentals to help customers find you online.</p>'
                         '<h2>The basics</h2><p>Use clear titles, write descriptive content, and keep your business information consistent everywhere.</p>'),
            # --- Success Stories (business stories & legacy) ---
            dict(title='How Kente and Co. Grew From a Market Stall to a Global Brand',
                 category='Success Stories', cover_seed='story-kente-legacy',
                 tags='fashion, legacy, growth, atlanta', is_featured=True,
                 read_time_minutes=7, view_count=534, days_ago=5,
                 excerpt='A decade ago it was a single stall. Today Kente and Co. ships handcrafted garments to customers on four continents.',
                 content='<p>What began as a weekend market stall in Atlanta is now a globally recognised name in African fashion.</p>'
                         '<h2>Staying true to the craft</h2><p>"We never compromised on authenticity," the founder recalls. "Every piece honours the weavers who taught us."</p>'
                         '<p>With SankofaX visibility and a loyal diaspora community, Kente and Co. now employs a team of 20 and mentors the next generation of designers.</p>'),
            dict(title='A Family Legacy: Three Generations of West African Cooking',
                 category='Success Stories', cover_seed='story-sankofa-legacy',
                 tags='food, legacy, family, london', is_featured=False,
                 read_time_minutes=6, view_count=311, days_ago=14,
                 excerpt='Sankofa Kitchen proves that heritage recipes, done with love, can build a lasting business.',
                 content='<p>From a grandmother\'s kitchen in Accra to a beloved Brixton institution, Sankofa Kitchen is a story of legacy and love.</p>'
                         '<h2>Passing it on</h2><p>The founders now run cooking classes so the recipes — and the stories behind them — live on.</p>'),
            # --- Diaspora News ---
            dict(title='Diaspora Investment Summit Comes to Nairobi This Autumn',
                 category='Diaspora News', cover_seed='news-nairobi-summit',
                 tags='events, investment, nairobi, diaspora', is_featured=True,
                 read_time_minutes=4, view_count=276, days_ago=3,
                 excerpt='Founders, investors and diaspora leaders will gather in Nairobi to unlock cross-border opportunities.',
                 content='<p>The inaugural Diaspora Investment Summit will bring together hundreds of founders and investors from across the diaspora.</p>'
                         '<h2>What to expect</h2><p>Pitch sessions, matchmaking and workshops focused on building bridges between diaspora capital and African enterprise.</p>'),
            dict(title='New Trade Corridor Opens Opportunities for Black-Owned Exporters',
                 category='Diaspora News', cover_seed='news-trade-corridor',
                 tags='trade, policy, export, africa', is_featured=False,
                 read_time_minutes=5, view_count=188, days_ago=10,
                 excerpt='Recent trade agreements are making it easier than ever for diaspora businesses to reach African markets.',
                 content='<p>New trade agreements are lowering barriers for exporters, opening fresh opportunities for diaspora-owned businesses.</p>'
                         '<h2>What it means for you</h2><p>Simplified customs and reduced tariffs mean small businesses can now compete across borders.</p>'),
        ]
        for p in posts:
            title = p['title']
            if BlogPost.objects.filter(title=title).exists():
                self.stdout.write('  ~ skip  blog: ' + title[:40] + ' (exists)')
                continue
            cat = self._blog_categories.get(p['category'])
            cover_seed = p.pop('cover_seed', None)
            days_ago = p.pop('days_ago', 0)
            status = p.pop('status', 'published')
            p.pop('category')
            published_at = None if status != 'published' else now - timedelta(days=days_ago)
            post = BlogPost(
                author=author, category=cat, status=status,
                published_at=published_at, **p,
            )
            if cover_seed:
                fname, fcontent = self._fetch_image(cover_seed, 1200, 600)
                if fname:
                    post.cover_image.save(fname, fcontent, save=False)
            post.save()
            self.stdout.write('  + BlogPost  ' + title[:45])

    def _core_content(self):
        from apps.accounts.models import User
        from apps.core.models import SiteSetting, Page, FAQ, Testimonial

        # Site settings (singleton)
        s = SiteSetting.get()
        if not s.contact_email:
            s.site_name = 'SankofaX'
            s.contact_email = 'hello@sankofax.com'
            s.contact_phone = '+44 20 7946 0000'
            s.contact_address = '128 City Road, London, EC1V 2NX, United Kingdom'
            s.footer_text = 'SankofaX — the global directory connecting Black & African businesses with the diaspora.'
            s.meta_description = 'Discover and support Black and African-owned businesses worldwide on SankofaX.'
            s.response_time = 'Within 24–48 hours'
            s.instagram_url = 'https://www.instagram.com/sankofax'
            s.facebook_url = 'https://www.facebook.com/sankofax'
            s.twitter_url = 'https://x.com/sankofax'
            s.linkedin_url = 'https://www.linkedin.com/company/sankofax'
            s.save()
            self.stdout.write('  + SiteSetting  configured')
        else:
            self.stdout.write('  ~ skip  SiteSetting (configured)')

        # Static pages
        pages = [
            dict(title='About Us', slug='about',
                 content='<h2>Our Mission</h2><p>SankofaX exists to connect Black and African-owned businesses with customers across the global diaspora. The word <em>Sankofa</em> means to reach back and reclaim what is valuable — and that is exactly what we help businesses do.</p>'
                         '<p>Whether you run a restaurant in London, a tech company in Nairobi, or a fashion label in Atlanta, SankofaX helps you get discovered.</p>'),
            dict(title='Contact', slug='contact',
                 content='<h2>Get in touch</h2><p>Have a question or want to partner with us? Reach out at <a href="mailto:hello@sankofax.com">hello@sankofax.com</a> and our team will respond within 24–48 hours.</p>'),
            dict(title='Terms of Service', slug='terms',
                 content='<h2>Terms of Service</h2><p>By using SankofaX you agree to our terms and conditions. Please use the platform respectfully and in accordance with all applicable laws.</p><p>This is placeholder demo content.</p>'),
            dict(title='Privacy Policy', slug='privacy',
                 content='<h2>Privacy Policy</h2><p>We respect your privacy and are committed to protecting your personal data. We only collect what is necessary to provide our services.</p><p>This is placeholder demo content.</p>'),
            dict(title='Cookie Policy', slug='cookies',
                 content='<h2>Cookie Policy</h2><p>SankofaX uses essential cookies to keep you signed in and analytics cookies to understand how the platform is used. You can manage cookies from your browser settings.</p><p>This is placeholder demo content.</p>'),
        ]
        for d in pages:
            if not Page.objects.filter(slug=d['slug']).exists():
                Page.objects.create(is_active=True, **d)
                self.stdout.write('  + Page  ' + d['title'])

        # FAQs
        faqs = [
            ('How do I list my business on SankofaX?',
             '<p>Create a free account, choose a plan, and click "Add Listing" from your dashboard. Fill in your business details, add photos, and publish!</p>', 1),
            ('Is there a free plan?',
             '<p>Yes! Our Starter plan is completely free and lets you publish one listing with basic analytics.</p>', 2),
            ('How do featured listings work?',
             '<p>Featured listings get premium placement at the top of search results and category pages. They are available on our Growth, Pro and Enterprise plans.</p>', 3),
            ('Can customers leave reviews?',
             '<p>Absolutely. Verified users can leave star ratings and written reviews on any published listing. Reviews are moderated before appearing publicly.</p>', 4),
            ('How do I upgrade or cancel my subscription?',
             '<p>You can manage your subscription anytime from the Billing section of your dashboard. Changes take effect at the end of your current billing cycle.</p>', 5),
            ('Which countries does SankofaX cover?',
             '<p>SankofaX is a global platform. We welcome Black and African-owned businesses from anywhere in the world.</p>', 6),
        ]
        for question, answer, order in faqs:
            if not FAQ.objects.filter(question=question).exists():
                FAQ.objects.create(question=question, answer=answer, order=order, is_active=True)
                self.stdout.write('  + FAQ  ' + question[:40])

        # Testimonials (tied to real users)
        testimonials = [
            ('owner1@sankofax.com', 'Restaurant Owner – London, UK',
             'SankofaX brought a whole new wave of customers to Sankofa Kitchen. Within weeks of listing, our weekend bookings doubled!', 1),
            ('owner2@sankofax.com', 'Tech Founder – New York, USA',
             'The CRM tools alone are worth it. We manage all our leads in one place and the featured listing keeps us at the top of search.', 2),
            ('owner3@sankofax.com', 'Fashion Designer – Atlanta, USA',
             'As a small fashion label, visibility is everything. SankofaX connected Kente and Co. with customers across the diaspora.', 3),
            ('user1@sankofax.com', 'Food Lover – London, UK',
             'I discovered so many amazing Black-owned restaurants through SankofaX. It has become my go-to for finding authentic food.', 4),
        ]
        for email, role, body, order in testimonials:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                continue
            if not Testimonial.objects.filter(user=user, body=body).exists():
                Testimonial.objects.create(
                    user=user, role=role, body=body, order=order,
                    status=Testimonial.Status.APPROVED,
                )
                self.stdout.write('  + Testimonial  ' + email)

        # Community / forum — sample threads + replies
        from apps.community.models import ForumCategory, Thread, Reply
        forum_seed = [
            ('business-networking', 'owner1@sankofax.com',
             'Looking to collaborate with other diaspora food businesses',
             'We run Sankofa Kitchen in London and would love to partner with African-owned '
             'suppliers and caterers across the UK. Anyone open to collaborating on pop-up events?',
             [('owner3@sankofax.com', 'Kente and Co. would love to do a fashion + food pop-up! DM me.'),
              ('user1@sankofax.com', 'As a customer I would 100% attend this. Please post dates!')]),
            ('tips-resources', 'owner2@sankofax.com',
             'What tools are you using to manage bookings and payments?',
             'Curious what the community recommends for invoicing and online payments — especially '
             'anything that works well across both the US and African markets.',
             [('owner1@sankofax.com', 'We use Stripe for cards and it has been smooth so far.')]),
        ]
        for cat_slug, author_email, title, body, replies in forum_seed:
            cat = ForumCategory.objects.filter(slug=cat_slug).first()
            if not cat:
                continue
            try:
                author = User.objects.get(email=author_email)
            except User.DoesNotExist:
                continue
            if Thread.objects.filter(title=title).exists():
                continue
            thread = Thread.objects.create(category=cat, author=author, title=title, body=body)
            for reply_email, reply_body in replies:
                ru = User.objects.filter(email=reply_email).first()
                if ru:
                    Reply.objects.create(thread=thread, author=ru, body=reply_body)
            self.stdout.write('  + Thread  ' + title[:40])