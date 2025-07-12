from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from backend_main.settings import MOUNT_OPENAPI_ROUTES


urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('auth/', include('authentication.urls')),
    path('activities/', include('activities.urls')),
    path('payments/', include('payments.urls')),
]

openapi_urlpatterns = [
    path('docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if MOUNT_OPENAPI_ROUTES:
    urlpatterns += openapi_urlpatterns
