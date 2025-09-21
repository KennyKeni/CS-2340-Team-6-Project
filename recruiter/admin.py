from django.contrib import admin
from .models import JobPosting

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "updated_at")
    search_fields = ("title", "summary", "skills_required", "owner__username")
    list_filter = ("created_at",)