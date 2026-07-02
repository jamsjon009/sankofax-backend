from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def root_redirect(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    return redirect('/admin/login/')


urlpatterns = [
    path('', root_redirect),
    path('favicon.ico', serve, {'path': 'favicon.ico', 'document_root': settings.BASE_DIR / 'static'}),
    path('admin/', admin.site.urls),

    # API
    path('api/', include([
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
