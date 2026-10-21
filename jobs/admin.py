from django.contrib import admin
from .models import JobListing, JobBookmark, JobSyncAuditLog

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ("title", "company_name", "portal", "modality", "seniority", "country", "status", "published_at")
    list_filter = ("portal", "modality", "seniority", "contract_type", "status", "careers", "country")
    search_fields = ("title", "company_name", "description", "city", "external_id")
    filter_horizontal = ("careers", "tags")
    prepopulated_fields = {"slug": ("company_name", "title")}
    readonly_fields = ("content_hash", "views_count", "created_at", "updated_at")

@admin.register(JobBookmark)
class JobBookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "job__title", "job__company_name")

@admin.register(JobSyncAuditLog)
class JobSyncAuditLogAdmin(admin.ModelAdmin):
    list_display = ("portal", "status", "jobs_fetched", "jobs_created", "jobs_updated", "jobs_unchanged", "errors_count", "duration_seconds", "executed_at")
    list_filter = ("status", "portal", "executed_at")
    readonly_fields = ("executed_at",)
