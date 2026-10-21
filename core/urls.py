from django.contrib import admin
from django.urls import path, include, re_path
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),

    # Favicon (evita el 404 en /favicon.ico)
    path('favicon.ico', RedirectView.as_view(url='/static/web/favicon.ico', permanent=True)),
    
    # La página de inicio (raíz de la web)
    path('', accounts_views.index_view, name='index'),
    
   # Centro de Control (Ajustes)
    path('ajustes/', accounts_views.ajustes_view, name='ajustes'),

    # Páginas estáticas / institucionales
    path('quienes-somos/', accounts_views.quienes_somos_view, name='quienes_somos'),
    path('terminos/', accounts_views.terminos_view, name='terminos'),
    path('privacidad/', accounts_views.privacidad_view, name='privacidad'),
    
    # Conexiones limpias a las sub-aplicaciones
    path('accounts/', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('courses/', include('courses.urls')),
    path('empleos/', include('jobs.urls', namespace='jobs')),
    path('comunidad/', include('community.urls')),

    # ARCHIVOS MULTIMEDIA (Permite servir avatares y multimedia de manera persistente en dev y prod)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]