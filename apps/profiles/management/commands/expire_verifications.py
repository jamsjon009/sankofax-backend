from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.profiles.models import CompanyProfile


class Command(BaseCommand):
    help = ('Revoke verification for companies whose tier has expired '
            '(periodic re-verification). Run on a schedule, e.g. daily.')

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Show what would be revoked without changing anything.')

    def handle(self, *args, **options):
        now = timezone.now()
        expired = CompanyProfile.objects.filter(
            verification_expires_at__lt=now,
            verification_level__gt=CompanyProfile.VerificationLevel.NONE,
        )
        count = expired.count()
        if options['dry_run']:
            for c in expired:
                self.stdout.write(f'  would revoke: {c.company_name} (L{c.verification_level}, '
                                  f'expired {c.verification_expires_at:%Y-%m-%d})')
            self.stdout.write(self.style.WARNING(f'Dry run — {count} company(ies) would be revoked.'))
            return

        for company in expired:
            company.revoke_verification()
            self.stdout.write(f'  revoked: {company.company_name}')
        self.stdout.write(self.style.SUCCESS(f'Revoked {count} expired verification(s).'))
