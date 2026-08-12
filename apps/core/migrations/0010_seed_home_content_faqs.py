"""Load the real website copy into admin (item #22).

- Instantiates HomeContent (pk=1) so its real-copy defaults show up in admin immediately.
- Seeds the four real FAQs from "Website Content_Aug2025".
- Creates the About page ("What is SankofaX?" + mission) if it doesn't exist.
- Fills SiteSetting.meta_description if blank.

Idempotent and non-destructive: existing FAQs / About page / meta are never overwritten.
"""
from django.db import migrations

FAQS = [
    ('Is SankofaX an online store?',
     '<p>No. SankofaX is a directory — we help people find, connect with, and support '
     'Black-owned businesses across the globe. We don’t facilitate transactions; we '
     'facilitate visibility.</p>'),
    ('Can service-based businesses join?',
     '<p>Absolutely! Whether you’re a therapist, graphic designer, lawyer, educator, or '
     'mobile nail tech — your business belongs on SankofaX.</p>'),
    ('Why is there a subscription if I’m not selling anything?',
     '<p>The subscription funds your visibility, our outreach, and the tools we provide for '
     'your profile and marketing. Think of it as paying for premium exposure and access — '
     'not sales commissions.</p>'),
    ('Can I list my business if I’m just starting out?',
     '<p>Yes. We welcome side hustlers, startups, freelancers, and full-fledged brands alike. '
     'If you’re serious about your growth and your culture — you’re in the right place.</p>'),
]

ABOUT_HTML = (
    '<h2>What is SankofaX?</h2>'
    '<p>SankofaX is the ultimate digital directory for Black and African-owned businesses '
    'worldwide. Our mission is to make it easy for people to discover, support, and connect '
    'with Black entrepreneurs, service providers, and creatives — no matter where they are '
    'in the world.</p>'
    '<p>Think of us as the Yellow Pages for the Diaspora — curated, connected, and '
    'culture-driven. Whether you\'re a tech founder in Accra, a fashion house in Toronto, or '
    'a wellness coach in Barbados, SankofaX makes sure the world knows your name.</p>'
    '<p>Inspired by the West African concept of Sankofa — “go back and get it” — we believe '
    'that reclaiming our global economic power starts with knowing who we are and where we '
    'are. This isn’t just a directory. It’s our digital village.</p>'
    '<h2>Our Mission</h2>'
    '<p>SankofaX exists to amplify the reach, recognition, and resilience of Black-owned '
    'businesses across the globe — because we believe that economic liberation is the '
    'foundation of cultural empowerment, and connection is where it begins.</p>'
    '<p>Our vision is to become the largest, most inclusive digital directory for Black-owned '
    'businesses across the diaspora — a place where heritage, innovation, and community come '
    'together to thrive.</p>'
)

META_DESCRIPTION = (
    'SankofaX is the global directory for Black and African-owned businesses — discover, '
    'support, and connect with entrepreneurs, services, and creatives across the diaspora.'
)


def seed(apps, schema_editor):
    HomeContent = apps.get_model('core', 'HomeContent')
    FAQ = apps.get_model('core', 'FAQ')
    Page = apps.get_model('core', 'Page')
    SiteSetting = apps.get_model('core', 'SiteSetting')

    # Materialise the singleton so its real-copy defaults are editable in admin.
    HomeContent.objects.get_or_create(pk=1)

    for i, (question, answer) in enumerate(FAQS, start=1):
        FAQ.objects.get_or_create(
            question=question,
            defaults={'answer': answer, 'order': i, 'is_active': True},
        )

    Page.objects.get_or_create(
        slug='about',
        defaults={'title': 'About Us', 'content': ABOUT_HTML, 'is_active': True},
    )

    site, _ = SiteSetting.objects.get_or_create(pk=1)
    if not site.meta_description:
        site.meta_description = META_DESCRIPTION
        site.save(update_fields=['meta_description'])


def unseed(apps, schema_editor):
    # Only remove the FAQs this migration introduced; leave HomeContent / About / meta.
    FAQ = apps.get_model('core', 'FAQ')
    FAQ.objects.filter(question__in=[q for q, _ in FAQS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_homecontent'),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]
