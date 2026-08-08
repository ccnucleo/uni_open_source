from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # Vista principal (Catálogo)
    path("", views.courses_page, name="list"),
    
    # API endpoints
    path("api/courses/", views.courses_collection_api, name="api_list_create"),
    path("api/courses/<int:course_id>/", views.courses_item_api, name="api_detail"),
    
    # Vista de Detalle (Actualizada para usar SLUG en vez de ID)
    path("<slug:course_slug>/", views.course_detail_page, name="detail"),
]