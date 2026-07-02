from django.urls import path
from .views import SiteSettingView, PageDetailView, FAQListView, ContactView

urlpatterns = [
    path('site-settings/', SiteSettingView.as_view(), name='site-settings'),
    path('pages/<slug:slug>/', PageDetailView.as_view(), name='page-detail'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('contact/', ContactView.as_view(), name='contact'),
]
