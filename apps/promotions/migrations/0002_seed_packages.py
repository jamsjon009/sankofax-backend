from django.db import migrations


PACKAGES = [
    dict(name='Founder Story Feature', slug='founder-story-feature', kind='founder_story',
         price='99.00', duration_days=30, subscriber_discount_percent=20, order=1,
         description='Tell your founder journey as a featured story on SankofaX.',
         features_list=[
             'Professionally published founder story',
             'Featured for 30 days on Success Stories',
             'Permanent home on your company profile',
             'Shared to our newsletter audience',
         ]),
    dict(name='Brand Feature', slug='brand-feature', kind='brand_feature',
         price='149.00', duration_days=45, subscriber_discount_percent=20, order=2,
         description='A polished spotlight on your brand, products and impact.',
         features_list=[
             'In-depth brand feature article',
             'Featured for 45 days',
             'Cover image + gallery',
             'Newsletter + social promotion',
         ]),
    dict(name='Press Release', slug='press-release', kind='press_release',
         price='199.00', duration_days=14, subscriber_discount_percent=25, order=3,
         description='Announce news — a launch, funding or milestone — to the diaspora.',
         features_list=[
             'Published to Diaspora News',
             'Featured for 14 days',
             'Distributed to our newsletter',
             'Priority editorial review',
         ]),
]


def seed(apps, schema_editor):
    StoryPackage = apps.get_model('promotions', 'StoryPackage')
    for p in PACKAGES:
        StoryPackage.objects.get_or_create(slug=p['slug'], defaults=p)


def unseed(apps, schema_editor):
    StoryPackage = apps.get_model('promotions', 'StoryPackage')
    StoryPackage.objects.filter(slug__in=[p['slug'] for p in PACKAGES]).delete()


class Migration(migrations.Migration):
    dependencies = [('promotions', '0001_initial')]
    operations = [migrations.RunPython(seed, unseed)]
