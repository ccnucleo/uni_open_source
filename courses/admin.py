from django.contrib import admin
from .models import Course, Tag

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # Esto hará que en el panel veas una tabla con estos datos
    list_display = ('title', 'category', 'level', 'resource_type', 'is_published')
    # Podrás filtrar por estos campos a la derecha
    list_filter = ('category', 'level', 'resource_type', 'has_certification')
    search_fields = ('title', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)