from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # La página de inicio (raíz de la web)
    path('', accounts_views.index_view, name='index'),
    
    # Conexiones limpias a las sub-aplicaciones
    path('accounts/', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('courses/', include('courses.urls')),
    path('comunidad/', include('community.urls')),
]

# ==============================================================================
# ARCHIVOS MULTIMEDIA (Imágenes subidas por usuarios o administradores)
# ==============================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)