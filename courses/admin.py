from django.contrib import admin
from .models import Course, Category, Tag, Career, SyncAuditLog


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'order')
    search_fields = ('name', 'code')
    list_editable = ('order',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'platform', 'provider_name', 'category', 'level', 'credential_type', 'is_published', 'created_at')
    list_filter = ('platform', 'careers', 'credential_type', 'is_published', 'category', 'level', 'language')
    search_fields = ('title', 'description', 'short_description', 'instructor_name', 'external_id')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('careers', 'tags')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(SyncAuditLog)
class SyncAuditLogAdmin(admin.ModelAdmin):
    list_display = ('executed_at', 'platform', 'status', 'courses_fetched', 'courses_created', 'courses_updated', 'errors_count', 'duration_seconds')
    list_filter = ('status', 'platform', 'executed_at')
    search_fields = ('platform', 'details')
    readonly_fields = ('executed_at',)