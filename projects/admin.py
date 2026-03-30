from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "owner", "is_public", "created_at")
	list_filter = ("is_public", "created_at")
	search_fields = ("title", "summary", "owner__username", "owner__email")
