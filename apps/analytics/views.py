import csv
import json

from django.http import StreamingHttpResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from .permissions import HasAnalyticsAccess
from . import services


def _parse_days(request, default=30):
    raw = request.query_params.get('days', default)
    try:
        days = int(raw)
    except (TypeError, ValueError):
        raise ValidationError({'days': 'Must be an integer number of days.'})
    return max(1, min(days, 365))


def _companies_or_404(request):
    company_slug = request.query_params.get('company')
    companies = services.resolve_companies(request.user, company_slug)
    if company_slug and not companies:
        raise NotFound('No such business, or you do not have access to it.')
    return companies


class AnalyticsSummaryView(APIView):
    """GET /api/analytics/summary/?company=<slug>&days=30 — owner-scoped headline metrics."""
    permission_classes = [HasAnalyticsAccess]

    def get(self, request):
        companies = _companies_or_404(request)
        days = _parse_days(request)
        return Response(services.build_summary(companies, days=days))


class AnalyticsTimeseriesView(APIView):
    """GET /api/analytics/timeseries/?metric=orders&company=&days=30 — daily counts for charts."""
    permission_classes = [HasAnalyticsAccess]

    def get(self, request):
        metric = request.query_params.get('metric')
        if metric not in services.TIMESERIES_SOURCES:
            raise ValidationError({
                'metric': f'Choose one of: {", ".join(services.TIMESERIES_SOURCES)}.',
            })
        companies = _companies_or_404(request)
        days = _parse_days(request)
        return Response({
            'metric': metric,
            'window_days': days,
            'series': services.build_timeseries(companies, metric, days=days),
        })


class AnalyticsExportView(APIView):
    """
    GET /api/analytics/export/?dataset=orders&fmt=csv|json&company=
    Streams the owner's raw records for the dataset. (Uses `fmt`, not `format`,
    to avoid colliding with DRF's content-negotiation query parameter.)
    """
    permission_classes = [HasAnalyticsAccess]

    def get(self, request):
        dataset = request.query_params.get('dataset')
        if dataset not in services.EXPORT_DATASETS:
            raise ValidationError({
                'dataset': f'Choose one of: {", ".join(services.EXPORT_DATASETS)}.',
            })
        fmt = request.query_params.get('fmt', 'csv').lower()
        if fmt not in ('csv', 'json'):
            raise ValidationError({'fmt': 'Choose csv or json.'})

        companies = _companies_or_404(request)
        columns, rows = services.export_rows(companies, dataset)
        filename = f'sankofax-{dataset}.{fmt}'

        if fmt == 'json':
            payload = [
                {c: _jsonable(r.get(c)) for c in columns}
                for r in rows
            ]
            resp = HttpResponse(json.dumps(payload, indent=2), content_type='application/json')
            resp['Content-Disposition'] = f'attachment; filename="{filename}"'
            return resp

        # CSV — stream so large exports don't buffer in memory.
        resp = StreamingHttpResponse(
            _csv_stream(columns, rows), content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp


def _jsonable(value):
    from decimal import Decimal
    import datetime
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    return value


class _Echo:
    def write(self, value):
        return value


def _csv_stream(columns, rows):
    writer = csv.writer(_Echo())
    yield writer.writerow(columns)
    for r in rows:
        yield writer.writerow([_jsonable(r.get(c)) for c in columns])
