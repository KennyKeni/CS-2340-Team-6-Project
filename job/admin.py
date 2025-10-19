from django.contrib import admin
from .models import JobPosting, JobApplication, JobSkill


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 3


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'owner', 'job_type', 'is_active', 'created_at')
    list_filter = ('job_type', 'is_active', 'created_at')
    search_fields = ('title', 'company', 'location', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [JobSkillInline]


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'job', 'importance_level')
    list_filter = ('importance_level',)
    search_fields = ('skill_name', 'job__title')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant__username', 'job__title', 'job__company')
    readonly_fields = ('applied_at', 'updated_at')