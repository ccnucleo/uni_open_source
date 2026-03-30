from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.projects_page, name="list"),
    path("api/projects/", views.projects_collection_api, name="api_list_create"),
    path("api/projects/<int:project_id>/", views.projects_item_api, name="api_detail"),
    path("<int:project_id>/", views.project_detail_page, name="detail"),
]
