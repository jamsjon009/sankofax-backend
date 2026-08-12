from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    """One command to load ALL demo data, in the recommended order.

    Runs: seed_demo -> seed_real_businesses -> seed_real_images -> geocode_locations.
    Every underlying seeder is idempotent, so this is safe to re-run. Network
    steps (images, geocoding) can be skipped for offline / CI use.

        python manage.py seed_all
        python manage.py seed_all --force-images        # replace placeholder images
        python manage.py seed_all --skip-images --skip-geocode   # offline
    """

    help = 'Load all demo data in one go (seed_demo, seed_real_businesses, seed_real_images, geocode_locations).'

    def add_arguments(self, parser):
        parser.add_argument('--force-images', action='store_true',
                            help='Pass --force to seed_real_images (replace existing images).')
        parser.add_argument('--skip-images', action='store_true',
                            help='Skip seed_real_images (avoids network image fetch).')
        parser.add_argument('--skip-geocode', action='store_true',
                            help='Skip geocode_locations (avoids network geocoding).')

    def handle(self, *args, **opts):
        steps = [
            ('seed_demo', {}),
            ('seed_real_businesses', {}),
        ]
        if not opts['skip_images']:
            steps.append(('seed_real_images', {'force': True} if opts['force_images'] else {}))
        if not opts['skip_geocode']:
            steps.append(('geocode_locations', {}))

        failed = []
        for name, kwargs in steps:
            self.stdout.write(self.style.MIGRATE_HEADING(f'\n=== {name} ==='))
            try:
                call_command(name, **kwargs)
            except Exception as exc:  # noqa: BLE001 — keep going; seeders are idempotent
                failed.append(name)
                self.stderr.write(self.style.ERROR(f'  {name} failed: {exc}'))

        if failed:
            self.stdout.write(self.style.WARNING(
                f'\nDone with errors. Failed step(s): {", ".join(failed)}. '
                'Re-run to retry (seeders are idempotent).'))
        else:
            self.stdout.write(self.style.SUCCESS('\nAll demo data seeded successfully.'))
