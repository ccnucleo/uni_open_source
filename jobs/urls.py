from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.jobs_page, name='list'),
    path('detalle/<slug:job_slug>/', views.job_detail_page, name='detail'),
    path('api/bookmark/<int:job_id>/', views.toggle_bookmark_api, name='toggle_bookmark'),
    path('api/', views.jobs_collection_api, name='api_list'),
]
