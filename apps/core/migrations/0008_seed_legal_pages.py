from django.db import migrations

# Starter content for the legal/static pages. Admins edit these in Django admin
# (Core → Pages) afterwards — the migration only guarantees the rows exist so the
# footer links (/terms, /privacy, /cookies) always resolve.
LEGAL_PAGES = [
    dict(
        slug='terms',
        title='Terms of Service',
        content=(
            '<h2>Terms of Service</h2>'
            '<p><em>Please replace this starter text with your own terms in Django admin '
            '(Core &rarr; Pages &rarr; Terms of Service).</em></p>'
            '<h3>1. Acceptance of Terms</h3>'
            '<p>By accessing or using SankofaX you agree to be bound by these Terms of Service '
            'and all applicable laws and regulations. If you do not agree, please do not use the platform.</p>'
            '<h3>2. Using the Platform</h3>'
            '<p>You agree to use SankofaX respectfully and lawfully. Business listings must be accurate, '
            'and you are responsible for the content you publish.</p>'
            '<h3>3. Accounts</h3>'
            '<p>You are responsible for keeping your account credentials secure and for all activity '
            'that occurs under your account.</p>'
            '<h3>4. Subscriptions &amp; Payments</h3>'
            '<p>Paid plans renew automatically until cancelled. You can manage or cancel your '
            'subscription at any time from your dashboard.</p>'
            '<h3>5. Changes to These Terms</h3>'
            '<p>We may update these terms from time to time. Continued use of SankofaX after changes '
            'take effect constitutes acceptance of the revised terms.</p>'
        ),
    ),
    dict(
        slug='privacy',
        title='Privacy Policy',
        content=(
            '<h2>Privacy Policy</h2>'
            '<p><em>Please replace this starter text with your own policy in Django admin '
            '(Core &rarr; Pages &rarr; Privacy Policy).</em></p>'
            '<h3>1. Information We Collect</h3>'
            '<p>We collect the information you provide when you create an account, list a business, '
            'or contact us — such as your name, email address, and business details.</p>'
            '<h3>2. How We Use Your Information</h3>'
            '<p>We use your information to operate and improve SankofaX, to power the directory, '
            'to process subscriptions, and to communicate with you.</p>'
            '<h3>3. Sharing</h3>'
            '<p>We do not sell your personal data. Public business listings are visible to all '
            'visitors by design; other personal information is only shared with service providers '
            'who help us run the platform.</p>'
            '<h3>4. Your Rights</h3>'
            '<p>You may access, update, or delete your personal information at any time by contacting us '
            'or through your account settings.</p>'
            '<h3>5. Contact</h3>'
            '<p>If you have questions about this policy, please reach out through our Contact page.</p>'
        ),
    ),
    dict(
        slug='cookies',
        title='Cookie Policy',
        content=(
            '<h2>Cookie Policy</h2>'
            '<p><em>Please replace this starter text with your own policy in Django admin '
            '(Core &rarr; Pages &rarr; Cookie Policy).</em></p>'
            '<h3>1. What Are Cookies</h3>'
            '<p>Cookies are small text files stored on your device that help websites remember your '
            'preferences and understand how the site is used.</p>'
            '<h3>2. How We Use Cookies</h3>'
            '<p>We use essential cookies to keep you signed in and to run core features, and analytics '
            'cookies to understand how visitors use SankofaX so we can improve it.</p>'
            '<h3>3. Managing Cookies</h3>'
            '<p>You can control or delete cookies through your browser settings. Disabling essential '
            'cookies may affect how the platform works.</p>'
            '<h3>4. Changes</h3>'
            '<p>We may update this Cookie Policy from time to time. Any changes will be posted on this page.</p>'
        ),
    ),
]


def seed_legal_pages(apps, schema_editor):
    Page = apps.get_model('core', 'Page')
    for data in LEGAL_PAGES:
        Page.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'title': data['title'],
                'content': data['content'],
                'is_active': True,
            },
        )


def unseed_legal_pages(apps, schema_editor):
    Page = apps.get_model('core', 'Page')
    Page.objects.filter(slug__in=[d['slug'] for d in LEGAL_PAGES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_sitesetting_instagram_embed_code'),
    ]

    operations = [
        migrations.RunPython(seed_legal_pages, unseed_legal_pages),
    ]
