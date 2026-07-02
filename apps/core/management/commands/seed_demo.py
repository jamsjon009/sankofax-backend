from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Insert demo data for all sections'

    def handle(self, *args, **kwargs):
        self.stdout.write('\n>>> Seeding SankofaX demo data...\n')
        self._users()
        self._categories_amenities()
        self._companies()
        self._listings()
        self._subscriptions()
        self._reviews()
        self._crm()
        self._newsletter()
        self._events()
        self.stdout.write('\n>>> Done! Demo data seeded.\n')

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
        self._categories = {}
        for name, icon, ltype in cats:
            cat, created = Category.objects.get_or_create(
                name=name, defaults={'icon': icon, 'listing_type': ltype}
            )
            self._categories[name] = cat
            if created:
                self.stdout.write('  + Category  ' + name)
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
                 description='Authentic West African cuisine in the heart of London.',
                 website='https://sankofakitchen.co.uk', contact_email='hello@sankofakitchen.co.uk',
                 contact_phone='+44 20 7946 0958', company_size='1-10', founded_year=2018, is_verified=True),
            dict(owner_email='owner2@sankofax.com', company_name='AfroTech Solutions',
                 description='Pan-African software development house building fintech and edtech products.',
                 website='https://afrotech.io', contact_email='info@afrotech.io',
                 contact_phone='+1 646 555 0201', company_size='11-50', founded_year=2020, is_verified=True),
            dict(owner_email='owner3@sankofax.com', company_name='Kente and Co.',
                 description='Luxury African fashion, bespoke Ankara and Kente garments shipped worldwide.',
                 website='https://kenteandco.com', contact_email='orders@kenteandco.com',
                 contact_phone='+1 929 555 0187', company_size='solo', founded_year=2021, is_verified=False),
        ]
        self._companies = {}
        for d in companies_data:
            owner_email = d.pop('owner_email')
            try:
                owner = User.objects.get(email=owner_email)
            except User.DoesNotExist:
                continue
            if not CompanyProfile.objects.filter(owner=owner).exists():
                cp = CompanyProfile.objects.create(owner=owner, **d)
                self._companies[owner_email] = cp
                self.stdout.write('  + Company  ' + cp.company_name)
            else:
                cp = CompanyProfile.objects.filter(owner=owner).first()
                self._companies[owner_email] = cp
                self.stdout.write('  ~ skip  ' + cp.company_name + ' (exists)')

    def _listings(self):
        from apps.directory.models import Listing
        now = timezone.now()
        listings_data = [
            dict(company_key='owner1@sankofax.com', category_name='Restaurant & Food',
                 title='Sankofa Kitchen Brixton',
                 short_description='Authentic West African restaurant serving jollof, suya and fufu.',
                 full_description='Step into Sankofa Kitchen for a true taste of West Africa. Our chefs prepare traditional dishes using imported spices and locally sourced ingredients. Famous for our smoky suya skewers, peanut soup, and award-winning jollof rice.',
                 listing_status='published', city='London', country='United Kingdom',
                 address_line='45 Atlantic Road, Brixton', phone='+44 20 7946 0958',
                 email='hello@sankofakitchen.co.uk', price_range='$$', featured=True,
                 published_at=now - timedelta(days=10), avg_rating='4.80', review_count=24),
            dict(company_key='owner1@sankofax.com', category_name='Restaurant & Food',
                 title='Sankofa Kitchen Peckham',
                 short_description='Our second location, same great food, new neighbourhood.',
                 full_description='The Peckham branch of Sankofa Kitchen brings the same delicious West African flavours to South East London. Dine in or take away. Catering available for events.',
                 listing_status='pending_review', city='London', country='United Kingdom',
                 address_line='12 Rye Lane, Peckham', phone='+44 20 7946 0959',
                 email='peckham@sankofakitchen.co.uk', price_range='$$', featured=False,
                 published_at=None, avg_rating='0', review_count=0),
            dict(company_key='owner2@sankofax.com', category_name='Technology & IT',
                 title='AfroTech Software Development',
                 short_description='Custom software, mobile apps and fintech built by African engineers.',
                 full_description='AfroTech Solutions is a Pan-African software house with teams in Lagos, Nairobi and New York. We build scalable fintech platforms, edtech tools and enterprise software.',
                 listing_status='published', city='New York', country='United States',
                 address_line='350 5th Avenue, Suite 4100', phone='+1 646 555 0201',
                 email='info@afrotech.io', price_range='$$$', featured=True,
                 published_at=now - timedelta(days=5), avg_rating='4.90', review_count=11),
            dict(company_key='owner3@sankofax.com', category_name='Fashion & Clothing',
                 title='Kente and Co Luxury African Fashion',
                 short_description='Bespoke Ankara, Kente and Adire garments crafted for the diaspora.',
                 full_description='Kente and Co celebrates African textile heritage with contemporary silhouettes. Each piece is hand-crafted using authentic Ghanaian Kente cloth and Nigerian Ankara fabric.',
                 listing_status='published', city='Atlanta', country='United States',
                 address_line='221 Auburn Avenue NE', phone='+1 929 555 0187',
                 email='orders@kenteandco.com', price_range='$$$', featured=False,
                 published_at=now - timedelta(days=3), avg_rating='4.60', review_count=8),
            dict(company_key='owner2@sankofax.com', category_name='Technology & IT',
                 title='AfroTech Mobile App Development',
                 short_description='Cross-platform mobile apps for African markets.',
                 full_description='Specialising in React Native and Flutter apps tailored for low-bandwidth African markets. Offline-first architecture, M-Pesa and Flutterwave payment integration.',
                 listing_status='pending_review', city='Nairobi', country='Kenya',
                 address_line='Westlands Business Park', phone='+254 700 123456',
                 email='mobile@afrotech.io', price_range='$$', featured=False,
                 published_at=None, avg_rating='0', review_count=0),
        ]
        self._listings = {}
        for d in listings_data:
            company_key = d.pop('company_key')
            category_name = d.pop('category_name')
            title = d['title']
            company = self._companies.get(company_key)
            category = self._categories.get(category_name)
            if not company or not category:
                continue
            if not Listing.objects.filter(title=title).exists():
                lst = Listing.objects.create(company=company, category=category, **d)
                if self._amenities:
                    lst.amenities.set(self._amenities[:3])
                self._listings[title] = lst
                self.stdout.write('  + Listing  ' + title)
            else:
                self._listings[title] = Listing.objects.get(title=title)
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
                 ticket_url='https://blacktechsummit.com', ticket_price='25.00', status='published'),
            dict(organizer=company, category=cat,
                 title='Diaspora Wellness and Culture Fair',
                 description='Yoga, meditation, African herbal medicine stalls, food vendors and live drumming.',
                 city='Atlanta', country='United States', venue_name='Piedmont Park',
                 start_datetime=now + timedelta(days=8), end_datetime=now + timedelta(days=8, hours=6),
                 ticket_url='', ticket_price='0.00', status='published'),
        ]
        for d in events_data:
            if not Event.objects.filter(title=d['title']).exists():
                Event.objects.create(**d)
                self.stdout.write('  + Event  ' + d['title'])