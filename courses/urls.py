from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.courses_page, name="list"),
    path("api/courses/", views.courses_collection_api, name="api_list_create"),
    path("api/courses/<int:course_id>/", views.courses_item_api, name="api_detail"),
    path("<int:course_id>/", views.course_detail_page, name="detail"),
]
