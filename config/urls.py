from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.accounts.urls')),
        path('', include('apps.profiles.urls')),
        path('', include('apps.directory.urls')),
        path('', include('apps.reviews.urls')),
        path('', include('apps.subscriptions.urls')),
        path('', include('apps.events.urls')),
        path('', include('apps.marketplace.urls')),
        path('', include('apps.crm.urls')),
        path('', include('apps.newsletter.urls')),
        path('', include('apps.core.urls')),
    ])),

    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
