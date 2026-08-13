from django.contrib import admin
from .models import Course, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'level', 'resource_type', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'level', 'resource_type', 'has_certification')
    search_fields = ('title', 'description', 'short_description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)