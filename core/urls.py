from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.index_view, name='index'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('projects/', include('projects.urls')),
    path('courses/', include('courses.urls')),

    # APIs para el registro interactivo
    path('api/check-username/', accounts_views.check_username_api, name='check_username_api'),
    path('api/verify-code/', accounts_views.verify_code_api, name='verify_code_api'),
    path('api/resend-code/', accounts_views.resend_code_api, name='resend_code_api'),

    # Rutas personalizadas de Recuperación de Contraseña
    path('reset_password/', accounts_views.reset_password_request_view, name='reset_password'),
    path('reset/<uidb64>/<token>/', accounts_views.reset_password_confirm_view, name='password_reset_confirm'),
]