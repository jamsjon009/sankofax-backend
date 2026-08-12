from django.urls import path
from .views import AnalyticsSummaryView, AnalyticsTimeseriesView, AnalyticsExportView

urlpatterns = [
    path('analytics/summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),
    path('analytics/timeseries/', AnalyticsTimeseriesView.as_view(), name='analytics-timeseries'),
    path('analytics/export/', AnalyticsExportView.as_view(), name='analytics-export'),
]
