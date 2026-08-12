from django.db import migrations

# Dedicated blog categories that power the Success Stories and Diaspora News
# landing pages (item #15). Admins publish posts into these categories in
# Django admin; the landing pages filter the blog by these slugs.
CATEGORIES = [
    ('success-stories', 'Success Stories',
     'Business stories & legacy — founders and companies thriving across the diaspora.', 10),
    ('diaspora-news', 'Diaspora News',
     'News and updates from across the global African diaspora.', 11),
]


def seed_categories(apps, schema_editor):
    BlogCategory = apps.get_model('blog', 'BlogCategory')
    for slug, name, description, order in CATEGORIES:
        BlogCategory.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'description': description, 'order': order},
        )


def unseed_categories(apps, schema_editor):
    BlogCategory = apps.get_model('blog', 'BlogCategory')
    BlogCategory.objects.filter(slug__in=[c[0] for c in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_blogpost_content'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
