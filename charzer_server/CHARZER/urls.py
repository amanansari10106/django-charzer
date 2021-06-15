from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='home'),
    path('<int:charger_id>', views.detail, name='detail'),
    path('api-auth/', include('rest_framework.urls')),
    path('customer/', include('customer.urls')),
    path('host/', include('Host.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
