"""Seed the real businesses from "Company Descriptions_2025" into the directory (item #21).

Idempotent: safe to run repeatedly. Creates (or reuses) the categories each business
needs, a single curator owner account that holds the seeded companies until the real
owners claim them, one CompanyProfile per business, and one published Listing so each
appears in the directory.

    manage.py seed_real_businesses

Only data present in the source document is populated (name + description, plus the
country/state where the text states it). Locations, contact details, logos and covers
are intentionally left blank for the owner/admin to complete — nothing is fabricated.
Once addresses are added, `manage.py geocode_locations` fills map coordinates (item #20).
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

# Curator account that owns the seeded companies until real owners claim/are assigned them.
CURATOR_EMAIL = 'partners@sankofax.com'

# (name, lucide icon) — created if missing.
CATEGORIES = [
    ('Health & Medical', 'stethoscope'),
    ('Staffing & Recruitment', 'users'),
    ('Real Estate', 'home'),
    ('Education', 'graduation-cap'),
    ('Agriculture & Farming', 'sprout'),
    ('Energy & Environment', 'leaf'),
    ('Nonprofit & Community', 'heart-handshake'),
    ('Professional Services', 'briefcase'),
    ('Engineering', 'wrench'),
    ('Technology & IT', 'laptop'),
]

# name, category, business_type, country, state, short_description, full_description
BUSINESSES = [
    ('Human-Centered Agility', 'Professional Services', 'service', '', '',
     'People-first agile training, coaching, and consulting for organizations adapting to change.',
     "Human-Centered Agility helps organizations adapt to change by focusing on people first. "
     "They provide training, coaching, and consulting in agile practices. Their approach fosters "
     "collaboration, innovation, and cultural transformation. The goal is to create workplaces "
     "where people and businesses thrive together."),

    ('Ayawa Nursing Agency', 'Staffing & Recruitment', 'service', 'United States', '',
     'Qualified nurses, CNAs, and healthcare professionals for facilities across the U.S.',
     "Ayawa Nursing Agency supplies qualified nurses, CNAs, and healthcare professionals. They "
     "partner with hospitals, clinics, and long-term care facilities across the U.S. The agency "
     "emphasizes reliability, compassion, and high standards of care. Its mission is to bridge "
     "staffing gaps and support quality patient outcomes."),

    ('5 Care Staffing', 'Staffing & Recruitment', 'service', 'United States', '',
     'Connecting healthcare providers with skilled nurses, aides, and allied health workers.',
     "5 Care Staffing specializes in connecting healthcare providers with skilled staff. They "
     "recruit nurses, aides, and allied health workers for diverse medical settings. The company "
     "prioritizes matching talent to facilities with precision and care. Their vision is to "
     "improve patient services through reliable staffing solutions."),

    ('Wezesha Real Estate', 'Real Estate', 'both', '', '',
     'Property sales, development, and management focused on sustainable, affordable housing.',
     "Wezesha Real Estate delivers property sales, development, and management solutions. They "
     "focus on creating sustainable and affordable housing for communities. The company combines "
     "innovation with trust to meet client property needs. Their mission is to empower families "
     "and investors to build lasting value."),

    ("Panda Children's Clinic", 'Health & Medical', 'service', 'Uganda', '',
     'Affordable, high-quality pediatric care and child development support in Uganda.',
     "Panda Children's Clinic provides affordable, high-quality pediatric care in Uganda. They "
     "focus on preventive care, treatment, and child development support. The clinic serves "
     "families with compassion and professional medical expertise. Its mission is to nurture "
     "healthier generations through accessible healthcare."),

    ('Nisaa African Family Services', 'Nonprofit & Community', 'nonprofit', 'United States', 'Iowa',
     'Counseling, advocacy, and family support for African immigrants and refugees in Iowa.',
     "Nisaa African Family Services supports African immigrants and refugees as they rebuild "
     "their lives in Iowa. They offer counseling, advocacy, and family-centered support programs. "
     "The nonprofit is dedicated to ending violence and promoting self-sufficiency. Their mission "
     "is to empower African families to thrive in their new communities."),

    ('Kooltech Engineering LLC', 'Engineering', 'service', '', '',
     'Mechanical and electrical engineering — cooling systems, energy efficiency, industrial services.',
     "Kooltech Engineering LLC provides innovative mechanical and electrical solutions. They "
     "specialize in cooling systems, energy efficiency, and industrial services. The company "
     "serves both commercial and residential clients with expertise. Their vision is to engineer "
     "sustainable technologies for a modern world."),

    ('Go Green International Limited', 'Energy & Environment', 'both', '', '',
     'Renewable energy and environmental solutions — solar, waste management, and sustainability.',
     "Go Green International champions renewable energy and environmental solutions. They "
     "implement solar, waste management, and sustainability projects. The company partners with "
     "communities to build greener, healthier spaces. Their mission is to drive Africa's "
     "transition toward clean energy and conservation."),

    ('Freedom International School Africa (FISA)', 'Education', 'service', '', '',
     'Values-driven education equipping African children with global knowledge and leadership skills.',
     "Freedom International School Africa (FISA) provides a values-driven education rooted in "
     "excellence and leadership. The school equips African children with global knowledge and "
     "life skills. They foster creativity, critical thinking, and moral responsibility in "
     "learners. The vision is to raise future leaders who impact Africa and the world positively."),

    ('Banat Mendy', 'Nonprofit & Community', 'nonprofit', '', '',
     'Empowering women and girls through education, entrepreneurship, training, and mentorship.',
     "Banat Mendy empowers women and girls through education and entrepreneurship. The initiative "
     "provides training, mentorship, and opportunities for growth. They focus on breaking barriers "
     "that limit women's social and economic progress. Their mission is to create stronger, "
     "self-reliant, and inspired communities."),

    ('Agatha Amani House', 'Nonprofit & Community', 'nonprofit', '', '',
     'A safe shelter offering counseling, healing, and skills training for survivors of gender-based violence.',
     "Agatha Amani House is a safe shelter for survivors of gender-based violence. They provide "
     "counseling, healing programs, and practical skills training. The home supports women on "
     "their journey toward dignity and independence. Its vision is to restore hope and empower "
     "survivors to rebuild their lives."),

    ('Awatho', 'Technology & IT', 'service', '', '',
     'A digital platform connecting people to opportunities, resources, and partnerships.',
     "Awatho is a digital platform connecting people to opportunities and resources. It supports "
     "entrepreneurs, professionals, and communities to collaborate. The platform fosters growth "
     "through networking, learning, and partnerships. Its mission is to open doors for innovation "
     "and economic empowerment."),

    ('Baaa Health', 'Health & Medical', 'service', '', '',
     'Accessible, affordable healthcare — preventive care, medical services, and health education.',
     "Baaa Health promotes accessible and affordable healthcare solutions. They provide preventive "
     "care, medical services, and health education. The company works to close gaps in community "
     "health and awareness. Their goal is to create healthier societies through proactive care."),

    ('Kibuku Rabbit Farm', 'Agriculture & Farming', 'product', '', '',
     'Modern rabbit breeding — quality meat, fur, and organic fertilizer for the agribusiness sector.',
     "Kibuku Rabbit Farm specializes in modern rabbit breeding and production. They supply quality "
     "meat, fur, and organic fertilizer for the agribusiness sector. The farm combines sustainable "
     "practices with innovative farming techniques. Their mission is to boost food security and "
     "income for local communities."),

    ('Triangle Health Consulting', 'Professional Services', 'service', '', '',
     'Healthcare strategy and management consulting — operations, compliance, and quality assurance.',
     "Triangle Health Consulting provides expert guidance in healthcare strategy and management. "
     "They support organizations in improving systems, compliance, and patient outcomes. The firm "
     "offers consulting in operations, training, and quality assurance. Its mission is to "
     "strengthen healthcare delivery through innovation and expertise."),

    ('Kacey Staffing Agency', 'Staffing & Recruitment', 'service', '', '',
     'A recruitment firm placing professionals across the healthcare and hospitality sectors.',
     "Kacey Staffing Agency is a recruitment firm that specializes in placing professionals in "
     "both healthcare and hospitality sectors."),
]


class Command(BaseCommand):
    help = 'Seed the real businesses from "Company Descriptions_2025" into the directory (item #21).'

    @transaction.atomic
    def handle(self, *args, **opts):
        owner = self._curator()
        categories = self._categories()
        self._businesses(owner, categories)

    def _curator(self):
        from apps.accounts.models import User
        owner, created = User.objects.get_or_create(
            email=CURATOR_EMAIL,
            defaults=dict(
                role=User.Role.BUSINESS_OWNER, is_verified=True,
                first_name='SankofaX', last_name='Partners',
            ),
        )
        if created:
            owner.set_unusable_password()  # placeholder holder — not a login account
            owner.save(update_fields=['password'])
            self.stdout.write(f'  + Curator owner  {CURATOR_EMAIL}')
        else:
            self.stdout.write(f'  ~ Curator owner  {CURATOR_EMAIL} (exists)')
        return owner

    def _categories(self):
        from apps.directory.models import Category
        cats = {}
        for name, icon in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=name, defaults={'icon': icon, 'listing_type': Category.ListingType.BUSINESS},
            )
            cats[name] = cat
            self.stdout.write(('  + Category  ' if created else '  ~ Category  ') + name)
        return cats

    def _businesses(self, owner, categories):
        from apps.profiles.models import CompanyProfile
        from apps.directory.models import Listing

        now = timezone.now()
        companies = listings = 0
        for name, cat_name, btype, country, state, short, full in BUSINESSES:
            slug = slugify(name)
            company, c_created = CompanyProfile.objects.get_or_create(
                slug=slug,
                defaults=dict(
                    owner=owner, company_name=name,
                    description=f'<p>{full}</p>',
                ),
            )
            if c_created:
                companies += 1
                self.stdout.write('  + Company  ' + name)
            else:
                self.stdout.write('  ~ Company  ' + name + ' (exists)')

            category = categories[cat_name]
            _, l_created = Listing.objects.get_or_create(
                slug=slug,
                defaults=dict(
                    company=company, category=category, business_type=btype,
                    title=name, short_description=short[:300],
                    full_description=f'<p>{full}</p>',
                    listing_status=Listing.Status.PUBLISHED, published_at=now,
                    country=country, state=state, city='',
                ),
            )
            if l_created:
                listings += 1
                self.stdout.write('  + Listing  ' + name)
            else:
                self.stdout.write('  ~ Listing  ' + name + ' (exists)')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {companies} new companies, {listings} new listings '
            f'({len(BUSINESSES)} businesses total).'
        ))
