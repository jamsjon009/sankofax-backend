"""
Management command to seed the database with realistic demo data.
Run: python manage.py seed_data
"""
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

fake = Faker()

CATEGORIES = [
    {'name': 'Black Vegan Restaurants', 'icon': 'utensils', 'listing_type': 'business'},
    {'name': 'African Wellness Retreats', 'icon': 'heart-pulse', 'listing_type': 'business'},
    {'name': 'Black-Owned Healthcare', 'icon': 'stethoscope', 'listing_type': 'business'},
    {'name': 'African Diaspora Events', 'icon': 'calendar', 'listing_type': 'event'},
    {'name': 'Afrocentric Travel', 'icon': 'plane', 'listing_type': 'business'},
    {'name': 'African Creatives', 'icon': 'palette', 'listing_type': 'business'},
    {'name': 'Black Therapists', 'icon': 'brain', 'listing_type': 'business'},
    {'name': 'Ethical African Products', 'icon': 'shopping-bag', 'listing_type': 'product'},
    {'name': 'African-Owned Tech', 'icon': 'laptop', 'listing_type': 'business'},
    {'name': 'African Spiritual & Healing', 'icon': 'sparkles', 'listing_type': 'business'},
]

AMENITIES = [
    'Vegan Options', 'Wheelchair Accessible', 'Outdoor Seating', 'Free Wifi',
    'Online Booking', 'Home Visits', 'Sliding Scale Fees', 'Language Support',
    'Child Friendly', 'Women-Led', 'LGBTQ+ Friendly', 'Black-Owned Badge',
]

CITIES = [
    ('London', 'England', 'United Kingdom', 51.5074, -0.1278),
    ('New York', 'New York', 'United States', 40.7128, -74.0060),
    ('Lagos', 'Lagos', 'Nigeria', 6.5244, 3.3792),
    ('Accra', 'Greater Accra', 'Ghana', 5.6037, -0.1870),
    ('Nairobi', 'Nairobi', 'Kenya', -1.2921, 36.8219),
    ('Toronto', 'Ontario', 'Canada', 43.6532, -79.3832),
    ('Paris', 'Île-de-France', 'France', 48.8566, 2.3522),
    ('Cape Town', 'Western Cape', 'South Africa', -33.9249, 18.4241),
    ('Johannesburg', 'Gauteng', 'South Africa', -26.2041, 28.0473),
    ('Washington DC', 'DC', 'United States', 38.9072, -77.0369),
    ('Atlanta', 'Georgia', 'United States', 33.7490, -84.3880),
    ('Amsterdam', 'North Holland', 'Netherlands', 52.3676, 4.9041),
    ('Berlin', 'Berlin', 'Germany', 52.5200, 13.4050),
    ('Kampala', 'Central', 'Uganda', 0.3476, 32.5825),
    ('Addis Ababa', 'Addis Ababa', 'Ethiopia', 9.0320, 38.7469),
]

BUSINESS_NAMES_BY_CAT = {
    'Black Vegan Restaurants': [
        'Roots & Greens Kitchen', 'Ubuntu Plates', 'The Baobab Bowl', 'Ancestors Table',
        'Akara & Co.', 'Kente Leaf Cafe', 'Sankofa Bites', 'Jollof & Greens',
    ],
    'African Wellness Retreats': [
        'Serengeti Soul Retreat', 'Ubuntu Wellness Center', 'Adinkra Healing Haven',
        'Nguzo Saba Spa', 'The Kente Sanctuary', 'Maasai Mindfulness Lodge',
    ],
    'Black-Owned Healthcare': [
        'Diaspora Health Clinic', 'Ubuntu Medical Group', 'Roots Health Partners',
        'Sankofa Wellness Clinic', 'Africana Care Center', 'Baobab Family Health',
    ],
    'African Diaspora Events': [
        'Afrotech Summit', 'Pan-African Arts Festival', 'Diaspora Business Week',
        'African Film Showcase', 'Black Excellence Gala', 'Ubuntu Cultural Fair',
    ],
    'Afrocentric Travel': [
        'Roots Heritage Tours', 'Ubuntu Travel Co.', 'Sankofa Expeditions',
        'Diaspora Journeys', 'Africa Homecoming Tours', 'Kente Routes',
    ],
    'African Creatives': [
        'Adinkra Design Studio', 'Kente Art Collective', 'Ubuntu Creative Hub',
        'Roots Photography', 'Diaspora Fashion House', 'Baobab Arts Agency',
    ],
    'Black Therapists': [
        'Ubuntu Counseling Group', 'Roots Therapy Network', 'Sankofa Mind & Soul',
        'Diaspora Wellness Therapy', 'Africana Psychology Practice', 'Healing Roots Therapy',
    ],
    'Ethical African Products': [
        'Kente & Co.', 'Ubuntu Crafts', 'Roots Market', 'Baobab Goods',
        'Adinkra Essentials', 'African Roots Emporium', 'Ubuntu Artisan Shop',
    ],
    'African-Owned Tech': [
        'Sankofa Tech Solutions', 'Ubuntu Digital', 'Roots Software Studio',
        'Baobab Analytics', 'Kente AI Labs', 'Diaspora Dev Agency', 'Adinkra Systems',
    ],
    'African Spiritual & Healing': [
        'Sankofa Spirit Center', 'Ubuntu Healing Arts', 'Roots & Ancestors Sanctuary',
        'Baobab Sacred Space', 'Adinkra Ancestral Practice', 'Ubuntu Ifa Center',
    ],
}

SHORT_DESCRIPTIONS = [
    'A welcoming space celebrating African culture and Black excellence.',
    'Authentically rooted in tradition, boldly reaching toward the future.',
    'Where community, wellness, and heritage come together.',
    'Proudly Black-owned, community-driven, and diaspora-focused.',
    'Serving the global African community with passion and purpose.',
    'Connecting the diaspora through culture, health, and creativity.',
    'Built by and for the African diaspora worldwide.',
    'Celebrating Black excellence — from root to branch.',
]

PRICE_RANGES = ['$', '$$', '$$$', '$$$$']


class Command(BaseCommand):
    help = 'Seed database with demo data (categories, amenities, companies, listings)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')
        self._seed_categories()

        self.stdout.write('Seeding amenities...')
        self._seed_amenities()

        self.stdout.write('Seeding users and companies...')
        self._seed_users_and_companies()

        self.stdout.write('Seeding listings...')
        self._seed_listings()

        self.stdout.write('Seeding subscription plans...')
        self._seed_plans()

        self.stdout.write(self.style.SUCCESS('Seed complete!'))

    def _seed_categories(self):
        from apps.directory.models import Category
        self._categories = {}
        for i, cat in enumerate(CATEGORIES):
            obj, _ = Category.objects.get_or_create(
                name=cat['name'],
                defaults={
                    'icon': cat['icon'],
                    'listing_type': cat['listing_type'],
                    'order': i,
                }
            )
            self._categories[cat['name']] = obj

    def _seed_amenities(self):
        from apps.directory.models import Amenity
        self._amenities = []
        for name in AMENITIES:
            obj, _ = Amenity.objects.get_or_create(name=name)
            self._amenities.append(obj)

    def _seed_users_and_companies(self):
        from apps.accounts.models import User
        from apps.profiles.models import CompanyProfile

        self._companies = {}
        for cat_name, biz_names in BUSINESS_NAMES_BY_CAT.items():
            for biz_name in biz_names[:4]:
                email = f'{biz_name.lower().replace(" ", ".").replace("&", "and")[:30]}@example.com'
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'role': User.Role.BUSINESS_OWNER,
                        'region': random.choice([User.Region.GLOBAL_NORTH, User.Region.GLOBAL_SOUTH]),
                        'is_active': True,
                    }
                )
                if created:
                    user.set_password('Demo1234!')
                    user.save()

                company, _ = CompanyProfile.objects.get_or_create(
                    company_name=biz_name,
                    defaults={
                        'owner': user,
                        'description': fake.paragraph(nb_sentences=4),
                        'website': f'https://www.{biz_name.lower().replace(" ", "").replace("&", "")[:20]}.com',
                        'contact_email': email,
                        'founded_year': random.randint(2010, 2023),
                        'is_verified': random.choice([True, False]),
                    }
                )
                self._companies.setdefault(cat_name, []).append(company)

    def _seed_listings(self):
        from apps.directory.models import Listing
        from django.utils.text import slugify

        for cat_name, companies in self._companies.items():
            category = self._categories.get(cat_name)
            if not category:
                continue

            for company in companies:
                city_data = random.choice(CITIES)
                city, state, country, lat, lng = city_data

                if Listing.objects.filter(company=company).exists():
                    continue

                listing = Listing.objects.create(
                    company=company,
                    category=category,
                    title=company.company_name,
                    short_description=random.choice(SHORT_DESCRIPTIONS),
                    full_description='\n\n'.join(fake.paragraphs(nb=4)),
                    listing_status=Listing.Status.PUBLISHED,
                    featured=random.random() > 0.8,
                    city=city,
                    state=state,
                    country=country,
                    latitude=lat + random.uniform(-0.05, 0.05),
                    longitude=lng + random.uniform(-0.05, 0.05),
                    phone=fake.phone_number()[:20],
                    email=company.contact_email,
                    website=company.website,
                    price_range=random.choice(PRICE_RANGES) if category.listing_type == 'business' else '',
                    avg_rating=round(random.uniform(3.5, 5.0), 2),
                    review_count=random.randint(2, 150),
                    view_count=random.randint(50, 5000),
                    published_at=timezone.now(),
                    opening_hours={
                        'monday': '9:00-18:00', 'tuesday': '9:00-18:00',
                        'wednesday': '9:00-18:00', 'thursday': '9:00-18:00',
                        'friday': '9:00-20:00', 'saturday': '10:00-16:00',
                        'sunday': 'Closed',
                    }
                )
                amenity_sample = random.sample(self._amenities, k=random.randint(2, 6))
                listing.amenities.set(amenity_sample)

    def _seed_plans(self):
        from apps.subscriptions.models import Plan

        plans = [
            {
                'name': 'Basic', 'tier_level': 1, 'region': 'global_north', 'price': 19,
                'billing_cycle': 'monthly', 'max_listings': 1, 'featured_listing_slots': 0,
                'analytics_access': False, 'priority_support': False,
                'features_list': ['1 listing', 'Basic profile', 'Email support'],
            },
            {
                'name': 'Basic', 'tier_level': 1, 'region': 'global_south', 'price': 9,
                'billing_cycle': 'monthly', 'max_listings': 1, 'featured_listing_slots': 0,
                'analytics_access': False, 'priority_support': False,
                'features_list': ['1 listing', 'Basic profile', 'Email support'],
            },
            {
                'name': 'Pro', 'tier_level': 2, 'region': 'global_north', 'price': 49,
                'billing_cycle': 'monthly', 'max_listings': 5, 'featured_listing_slots': 1,
                'analytics_access': True, 'priority_support': False,
                'features_list': ['5 listings', 'Analytics dashboard', '1 featured slot', 'Priority listing'],
            },
            {
                'name': 'Pro', 'tier_level': 2, 'region': 'global_south', 'price': 19,
                'billing_cycle': 'monthly', 'max_listings': 5, 'featured_listing_slots': 1,
                'analytics_access': True, 'priority_support': False,
                'features_list': ['5 listings', 'Analytics dashboard', '1 featured slot', 'Priority listing'],
            },
            {
                'name': 'Elite', 'tier_level': 3, 'region': 'global_north', 'price': 99,
                'billing_cycle': 'monthly', 'max_listings': 20, 'featured_listing_slots': 3,
                'analytics_access': True, 'priority_support': True,
                'features_list': ['20 listings', 'Advanced analytics', '3 featured slots', 'Priority support', 'Verified badge'],
            },
            {
                'name': 'Elite', 'tier_level': 3, 'region': 'global_south', 'price': 39,
                'billing_cycle': 'monthly', 'max_listings': 20, 'featured_listing_slots': 3,
                'analytics_access': True, 'priority_support': True,
                'features_list': ['20 listings', 'Advanced analytics', '3 featured slots', 'Priority support', 'Verified badge'],
            },
        ]

        for plan_data in plans:
            Plan.objects.get_or_create(
                name=plan_data['name'],
                region=plan_data['region'],
                billing_cycle=plan_data['billing_cycle'],
                defaults=plan_data,
            )
