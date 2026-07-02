from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('tier_level', models.PositiveIntegerField(default=0, help_text='For sort order (0=lowest)')),
                ('region', models.CharField(blank=True, choices=[('global_north', 'Global North'), ('global_south', 'Global South')], help_text='Leave blank for a single global price', max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('billing_cycle', models.CharField(choices=[('monthly', 'Monthly'), ('annual', 'Annual'), ('one_time', 'One-Time')], default='monthly', max_length=10)),
                ('max_listings', models.PositiveIntegerField(default=1)),
                ('featured_listing_slots', models.PositiveIntegerField(default=0)),
                ('analytics_access', models.BooleanField(default=False)),
                ('priority_support', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('features_list', models.JSONField(blank=True, default=list, help_text='List of feature strings shown on pricing page')),
            ],
            options={
                'ordering': ['tier_level', 'price'],
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('past_due', 'Past Due'), ('canceled', 'Canceled'), ('trialing', 'Trialing')], default='active', max_length=10)),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=100)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100)),
                ('current_period_end', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='profiles.companyprofile')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='subscriptions.plan')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
