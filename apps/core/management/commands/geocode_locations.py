"""Backfill latitude/longitude for listings and events from their addresses (item #20).

    manage.py geocode_locations                # fill any records missing coordinates
    manage.py geocode_locations --force        # re-geocode everything
    manage.py geocode_locations --listings     # listings only
    manage.py geocode_locations --events       # events only
    manage.py geocode_locations --limit 50     # cap how many records are processed

Throttles between lookups (default 1s) to respect Nominatim's usage policy.
"""
# Output is kept ASCII-only so it prints on Windows consoles (cp1252) too.
import time

from django.core.management.base import BaseCommand

from apps.core.geocoding import geocode_event, geocode_listing
from apps.directory.models import Listing
from apps.events.models import Event


class Command(BaseCommand):
    help = 'Geocode listings and events (address -> latitude/longitude).'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Re-geocode records that already have coordinates.')
        parser.add_argument('--listings', action='store_true', help='Process listings only.')
        parser.add_argument('--events', action='store_true', help='Process events only.')
        parser.add_argument('--limit', type=int, default=None,
                            help='Maximum records to process per model.')
        parser.add_argument('--sleep', type=float, default=1.0,
                            help='Seconds to wait between lookups (Nominatim policy). Default 1.0.')

    def handle(self, *args, **opts):
        do_listings = opts['listings'] or not opts['events']
        do_events = opts['events'] or not opts['listings']

        if do_listings:
            self._run('listing', Listing.objects.all(), geocode_listing, opts)
        if do_events:
            self._run('event', Event.objects.all(), geocode_event, opts)

    def _run(self, label, qs, geocoder, opts):
        if not opts['force']:
            qs = qs.filter(latitude__isnull=True) | qs.filter(longitude__isnull=True)
            qs = qs.distinct()
        if opts['limit']:
            qs = qs[:opts['limit']]

        total = updated = 0
        for obj in qs:
            total += 1
            if geocoder(obj, force=opts['force']):
                updated += 1
                self.stdout.write(f'  [ok]   {label} "{obj}" -> {obj.latitude}, {obj.longitude}')
            else:
                self.stdout.write(f'  [skip] {label} "{obj}" - no result')
            if opts['sleep']:
                time.sleep(opts['sleep'])

        self.stdout.write(self.style.SUCCESS(
            f'{label}s: {updated}/{total} geocoded.'
        ))
