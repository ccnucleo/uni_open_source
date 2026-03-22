from django.contrib import admin
from django.urls import path, include # Asegúrate de importar 'include'
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')), # Esto conecta con tu app
    path('api/check-username/', views.check_username_api, name='check_username_api'),
    path('api/verify-code/', views.verify_code_api, name='verify_code_api'),
    path('api/resend-code/', views.resend_code_api, name='resend_code_api'),
]