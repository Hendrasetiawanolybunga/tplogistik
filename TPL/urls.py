
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from core.admin import admin_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('kurir/', admin_site.urls),  
    path('', include('core.urls')), 
]
static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)