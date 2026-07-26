from django.urls import path
from .views import SiteSettingView, PageDetailView, FAQListView, ContactView, AdminStatsView, TestimonialListView, TestimonialSubmitView, PublicStatsView

urlpatterns = [
    path('site-settings/', SiteSettingView.as_view(), name='site-settings'),
    path('pages/<slug:slug>/', PageDetailView.as_view(), name='page-detail'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('stats/', PublicStatsView.as_view(), name='public-stats'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('testimonials/', TestimonialListView.as_view(), name='testimonial-list'),
    path('testimonials/my/', TestimonialSubmitView.as_view(), name='testimonial-my'),
]