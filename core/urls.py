from django.contrib import admin
from django.urls import path, include
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')), # Esto conecta con tu app principal
    
    # APIs para el registro interactivo
    path('api/check-username/', views.check_username_api, name='check_username_api'),
    path('api/verify-code/', views.verify_code_api, name='verify_code_api'),
    path('api/resend-code/', views.resend_code_api, name='resend_code_api'),
    
    # Rutas personalizadas de Recuperación de Contraseña
    path('reset_password/', views.reset_password_request_view, name='reset_password'),
    path('reset/<uidb64>/<token>/', views.reset_password_confirm_view, name='password_reset_confirm'),
]