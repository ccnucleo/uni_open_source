from django.contrib import admin
from .models import Profile, UnverifiedUser, Technology, Interest


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'contact_email', 'linkedin', 'github')
    search_fields = ('user__username', 'user__email', 'contact_email')


@admin.register(UnverifiedUser)
class UnverifiedUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'verification_code', 'created_at')
    search_fields = ('username', 'email', 'verification_code')
    list_filter = ('created_at',)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
