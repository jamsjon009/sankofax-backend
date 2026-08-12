"""Seed the client-confirmed regional pricing (item #23).

Three tiers — Directory Basic / Pro / Elite — priced per region:
  Global North:  $15 / $29 / $49
  Global South:  $7.50 / $14.50 / $24.50   (equitable pricing, same features)

Uses update_or_create so the authoritative prices/features are enforced even if a
row already exists. Any other active plan (legacy demo tiers) is deactivated so the
public pricing shows exactly these three tiers per region — re-activate in admin if a
free tier is wanted.
"""
from django.db import migrations

FEATURES = {
    1: ['Full profile listing', 'Included in directory search', 'One featured tag'],
    2: ['Everything in Basic', 'Priority search placement', 'Image gallery', 'Promo slots'],
    3: ['Everything in Pro', 'Homepage feature', 'Monthly social media spotlight', 'Article / blog feature'],
}
LIMITS = {  # tier -> (max_listings, featured_slots, analytics, priority_support)
    1: (1, 1, False, False),
    2: (5, 3, True, False),
    3: (20, 10, True, True),
}
NAMES = {1: 'Directory Basic', 2: 'Directory Pro', 3: 'Directory Elite'}

# region -> {tier: (price, description)}
PRICING = {
    'global_north': {
        1: ('15.00', 'Full profile listing, search inclusion, one featured tag.'),
        2: ('29.00', 'Priority search placement, image gallery, promo slots.'),
        3: ('49.00', 'Homepage feature, monthly social media spotlight, article/blog feature.'),
    },
    'global_south': {
        1: ('7.50', 'Same features as Global North — equitable pricing.'),
        2: ('14.50', 'All Pro benefits at a globally conscious rate.'),
        3: ('24.50', 'Premium placement, same perks, roughly half the cost.'),
    },
}


def seed(apps, schema_editor):
    Plan = apps.get_model('subscriptions', 'Plan')

    kept_ids = []
    for region, tiers in PRICING.items():
        for tier, (price, description) in tiers.items():
            max_listings, featured, analytics, priority = LIMITS[tier]
            plan, _ = Plan.objects.update_or_create(
                name=NAMES[tier], region=region,
                defaults=dict(
                    tier_level=tier, price=price, currency='USD',
                    billing_cycle='monthly', max_listings=max_listings,
                    featured_listing_slots=featured, analytics_access=analytics,
                    priority_support=priority, is_active=True,
                    description=description, features_list=FEATURES[tier],
                ),
            )
            kept_ids.append(plan.id)

    # Hide any other currently-active plan (legacy demo tiers) from public pricing.
    Plan.objects.filter(is_active=True).exclude(id__in=kept_ids).update(is_active=False)


def unseed(apps, schema_editor):
    Plan = apps.get_model('subscriptions', 'Plan')
    Plan.objects.filter(name__in=list(NAMES.values()),
                        region__in=['global_north', 'global_south']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('subscriptions', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]
