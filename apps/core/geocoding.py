"""Address → (latitude, longitude) geocoding for listings and events (item #20).

Pluggable provider, selected with the ``GEOCODER`` setting:

* ``nominatim`` (default) — OpenStreetMap's free service, no API key required.
  Respect its usage policy (≤1 req/sec, a real User-Agent) — the bulk backfill
  command throttles for this reason.
* ``mapbox`` — needs ``MAPBOX_TOKEN``.
* ``none`` — disables geocoding entirely (useful in tests / offline dev).

Every lookup is best-effort: network, HTTP and parse errors are swallowed and
logged so a failed geocode never blocks a save or breaks an API request. Records
saved without coordinates can be filled later with ``manage.py geocode_locations``.
"""
import json
import logging
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation

from django.conf import settings

logger = logging.getLogger(__name__)

USER_AGENT = 'SankofaX/1.0 (+https://sankofax.com)'


def build_address(*parts):
    """Join non-empty address components into a single query string."""
    return ', '.join(str(p).strip() for p in parts if p and str(p).strip())


def geocode(query, *, timeout=6):
    """Return ``(Decimal lat, Decimal lng)`` for a free-form address, or ``None``.

    Never raises — any failure returns ``None``.
    """
    provider = (getattr(settings, 'GEOCODER', 'nominatim') or 'none').lower()
    if not query or provider == 'none':
        return None
    try:
        if provider == 'nominatim':
            return _nominatim(query, timeout)
        if provider == 'mapbox':
            return _mapbox(query, timeout)
        logger.warning('Unknown GEOCODER %r; skipping geocoding', provider)
        return None
    except Exception as exc:  # noqa: BLE001 — geocoding must never break a save
        logger.warning('Geocoding failed for %r: %s', query, exc)
        return None


def _http_get_json(url, timeout):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 — fixed https hosts
        return json.loads(resp.read().decode('utf-8'))


def _coords(lat, lng):
    """Validate + coerce a lat/lng pair to Decimals, or ``None`` if out of range."""
    try:
        lat, lng = Decimal(str(lat)), Decimal(str(lng))
    except (InvalidOperation, TypeError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None
    return lat, lng


def _nominatim(query, timeout):
    base = getattr(settings, 'NOMINATIM_URL', 'https://nominatim.openstreetmap.org/search')
    params = urllib.parse.urlencode({'q': query, 'format': 'json', 'limit': 1})
    data = _http_get_json(f'{base}?{params}', timeout)
    if not data:
        return None
    first = data[0]
    return _coords(first.get('lat'), first.get('lon'))


def _mapbox(query, timeout):
    token = getattr(settings, 'MAPBOX_TOKEN', '')
    if not token:
        logger.warning('GEOCODER=mapbox but MAPBOX_TOKEN is empty')
        return None
    q = urllib.parse.quote(query)
    url = (f'https://api.mapbox.com/geocoding/v5/mapbox.places/{q}.json'
           f'?access_token={urllib.parse.quote(token)}&limit=1')
    data = _http_get_json(url, timeout)
    features = (data or {}).get('features') or []
    if not features:
        return None
    center = features[0].get('center') or []
    if len(center) != 2:
        return None
    lng, lat = center  # Mapbox returns [lng, lat]
    return _coords(lat, lng)


# --- Model helpers -----------------------------------------------------------

def _apply(instance, coords, save):
    instance.latitude, instance.longitude = coords
    if save and instance.pk:
        # Update only the coordinate columns — avoids re-running model.save()
        # side effects and avoids clobbering concurrent edits to other fields.
        type(instance).objects.filter(pk=instance.pk).update(
            latitude=instance.latitude, longitude=instance.longitude,
        )
    return True


def geocode_listing(listing, *, force=False, save=True):
    """Fill ``listing`` coordinates from its address. Returns True if updated.

    Skips (returns False) when coordinates are already present unless ``force``.
    """
    if not force and listing.latitude is not None and listing.longitude is not None:
        return False
    query = build_address(
        listing.address_line, listing.city, listing.state,
        listing.postal_code, listing.country,
    )
    coords = geocode(query)
    return _apply(listing, coords, save) if coords else False


def geocode_event(event, *, force=False, save=True):
    """Fill ``event`` coordinates from its venue/city/country. Returns True if updated.

    Virtual events with no physical location are skipped.
    """
    if event.is_virtual and not (event.venue_name or event.city):
        return False
    if not force and event.latitude is not None and event.longitude is not None:
        return False
    query = build_address(event.venue_name, event.city, event.country)
    coords = geocode(query)
    return _apply(event, coords, save) if coords else False
