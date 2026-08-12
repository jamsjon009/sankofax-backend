from django.db import migrations
from django.utils.text import slugify

# Default discussion boards. Admins can edit/add more in Django admin
# (Community → Forum Categories).
CATEGORIES = [
    ('General Discussion', '💬', 'Introduce yourself and talk about anything SankofaX.', 1),
    ('Business Networking', '🤝', 'Connect with other founders and find collaborators.', 2),
    ('Investor Matchmaking', '📈', 'Founders and investors looking to connect.', 3),
    ('Tips & Resources', '🧰', 'Share tools, advice and resources for growing your business.', 4),
    ('Diaspora & Culture', '🌍', 'Conversations about the global African diaspora and community.', 5),
]


def seed_categories(apps, schema_editor):
    ForumCategory = apps.get_model('community', 'ForumCategory')
    for name, icon, description, order in CATEGORIES:
        ForumCategory.objects.get_or_create(
            slug=slugify(name),
            defaults={'name': name, 'icon': icon, 'description': description,
                      'order': order, 'is_active': True},
        )


def unseed_categories(apps, schema_editor):
    ForumCategory = apps.get_model('community', 'ForumCategory')
    ForumCategory.objects.filter(slug__in=[slugify(c[0]) for c in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
