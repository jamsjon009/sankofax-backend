"""Tests for the geocoding service (item #20). Network is always mocked."""
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.core import geocoding
from apps.directory.models import Listing
from apps.events.models import Event


class BuildAddressTests(TestCase):
    def test_joins_non_empty_parts(self):
        self.assertEqual(
            geocoding.build_address('12 High St', '', 'Accra', None, 'Ghana'),
            '12 High St, Accra, Ghana',
        )

    def test_empty_when_all_blank(self):
        self.assertEqual(geocoding.build_address('', None, '  '), '')


class GeocodeTests(TestCase):
    @override_settings(GEOCODER='nominatim')
    def test_nominatim_parses_first_result(self):
        with patch.object(geocoding, '_http_get_json',
                          return_value=[{'lat': '5.6037', 'lon': '-0.1870'}]):
            self.assertEqual(geocoding.geocode('Accra, Ghana'),
                             (Decimal('5.6037'), Decimal('-0.1870')))

    @override_settings(GEOCODER='nominatim')
    def test_empty_result_returns_none(self):
        with patch.object(geocoding, '_http_get_json', return_value=[]):
            self.assertIsNone(geocoding.geocode('Nowhere at all'))

    @override_settings(GEOCODER='none')
    def test_disabled_provider_returns_none(self):
        with patch.object(geocoding, '_http_get_json') as http:
            self.assertIsNone(geocoding.geocode('Accra, Ghana'))
            http.assert_not_called()

    @override_settings(GEOCODER='nominatim')
    def test_network_error_is_swallowed(self):
        with patch.object(geocoding, '_http_get_json', side_effect=OSError('boom')):
            self.assertIsNone(geocoding.geocode('Accra, Ghana'))

    @override_settings(GEOCODER='nominatim')
    def test_out_of_range_coords_rejected(self):
        with patch.object(geocoding, '_http_get_json',
                          return_value=[{'lat': '999', 'lon': '0'}]):
            self.assertIsNone(geocoding.geocode('Somewhere'))

    def test_empty_query_returns_none(self):
        self.assertIsNone(geocoding.geocode(''))

    @override_settings(GEOCODER='mapbox', MAPBOX_TOKEN='tok')
    def test_mapbox_parses_center_lng_lat(self):
        payload = {'features': [{'center': [-0.1870, 5.6037]}]}
        with patch.object(geocoding, '_http_get_json', return_value=payload):
            self.assertEqual(geocoding.geocode('Accra, Ghana'),
                             (Decimal('5.6037'), Decimal('-0.1870')))

    @override_settings(GEOCODER='mapbox', MAPBOX_TOKEN='')
    def test_mapbox_without_token_returns_none(self):
        with patch.object(geocoding, '_http_get_json') as http:
            self.assertIsNone(geocoding.geocode('Accra, Ghana'))
            http.assert_not_called()


class GeocodeListingHelperTests(TestCase):
    def _listing(self, **kw):
        # Unsaved instance — geocode with save=False avoids FK/DB setup.
        return Listing(city='Accra', country='Ghana', **kw)

    def test_fills_missing_coordinates(self):
        listing = self._listing()
        with patch.object(geocoding, 'geocode',
                          return_value=(Decimal('5.6'), Decimal('-0.2'))):
            self.assertTrue(geocoding.geocode_listing(listing, save=False))
        self.assertEqual(listing.latitude, Decimal('5.6'))
        self.assertEqual(listing.longitude, Decimal('-0.2'))

    def test_skips_when_coords_present(self):
        listing = self._listing(latitude=Decimal('1'), longitude=Decimal('2'))
        with patch.object(geocoding, 'geocode') as g:
            self.assertFalse(geocoding.geocode_listing(listing, save=False))
            g.assert_not_called()

    def test_force_re_geocodes(self):
        listing = self._listing(latitude=Decimal('1'), longitude=Decimal('2'))
        with patch.object(geocoding, 'geocode',
                          return_value=(Decimal('5.6'), Decimal('-0.2'))):
            self.assertTrue(geocoding.geocode_listing(listing, force=True, save=False))
        self.assertEqual(listing.latitude, Decimal('5.6'))

    def test_no_result_leaves_coords_untouched(self):
        listing = self._listing()
        with patch.object(geocoding, 'geocode', return_value=None):
            self.assertFalse(geocoding.geocode_listing(listing, save=False))
        self.assertIsNone(listing.latitude)


class GeocodeEventHelperTests(TestCase):
    def test_virtual_without_location_is_skipped(self):
        event = Event(is_virtual=True, city='', venue_name='')
        with patch.object(geocoding, 'geocode') as g:
            self.assertFalse(geocoding.geocode_event(event, save=False))
            g.assert_not_called()

    def test_physical_event_geocoded(self):
        event = Event(is_virtual=False, city='Lagos', country='Nigeria')
        with patch.object(geocoding, 'geocode',
                          return_value=(Decimal('6.5'), Decimal('3.4'))):
            self.assertTrue(geocoding.geocode_event(event, save=False))
        self.assertEqual(event.latitude, Decimal('6.5'))


class SerializerAutoGeocodeTests(TestCase):
    def test_geocodes_when_client_omits_coords(self):
        from apps.directory.serializers import ListingCreateUpdateSerializer
        ser = ListingCreateUpdateSerializer()
        ser.initial_data = {'city': 'Accra', 'country': 'Ghana'}
        listing = Listing(city='Accra', country='Ghana')
        with patch.object(geocoding, 'geocode',
                          return_value=(Decimal('5.6'), Decimal('-0.2'))):
            ser._maybe_geocode(listing)
        self.assertEqual(listing.latitude, Decimal('5.6'))

    def test_respects_client_supplied_coords(self):
        from apps.directory.serializers import ListingCreateUpdateSerializer
        ser = ListingCreateUpdateSerializer()
        ser.initial_data = {'latitude': '1.0', 'longitude': '2.0'}
        listing = Listing(city='Accra', country='Ghana',
                          latitude=Decimal('1.0'), longitude=Decimal('2.0'))
        with patch.object(geocoding, 'geocode') as g:
            ser._maybe_geocode(listing)
            g.assert_not_called()
