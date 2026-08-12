from django.db import migrations


def backfill_levels(apps, schema_editor):
    """Existing is_verified=True companies had gone through manual document
    review, so map them to Level 2 (Verified — Documents) with a rolling
    one-year expiry from when they were created."""
    from datetime import timedelta
    CompanyProfile = apps.get_model('profiles', 'CompanyProfile')
    for company in CompanyProfile.objects.filter(is_verified=True, verification_level=0):
        company.verification_level = 2  # VERIFIED
        company.verified_at = company.created_at
        company.verification_expires_at = (company.created_at + timedelta(days=365)) if company.created_at else None
        company.save(update_fields=['verification_level', 'verified_at', 'verification_expires_at'])


def reverse_backfill(apps, schema_editor):
    CompanyProfile = apps.get_model('profiles', 'CompanyProfile')
    CompanyProfile.objects.filter(verification_level=2).update(
        verification_level=0, verified_at=None, verification_expires_at=None)


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_companyprofile_verification_expires_at_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_levels, reverse_backfill),
    ]
