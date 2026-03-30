from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "category", "level", "owner", "is_published", "created_at")
	list_filter = ("category", "level", "is_published", "created_at")
	search_fields = ("title", "short_description", "owner__username", "owner__email")
