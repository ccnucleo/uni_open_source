from django.contrib import admin
from .models import Project, Tag, Technology


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "owner", "is_public", "created_at")
	list_filter = ("is_public", "created_at")
	search_fields = ("title", "summary", "owner__username", "owner__email")

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "icon")
    search_fields = ("name",)
