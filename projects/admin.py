from django.contrib import admin
from .models import Project, ProjectImage, Tag, Technology


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "is_public", "views_count", "created_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("title", "summary", "owner__username", "owner__email")
    inlines = [ProjectImageInline]


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "image", "order")
    list_filter = ("project",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "icon")
    search_fields = ("name",)
