from django.contrib import admin

from utils.export import export_applications_csv

from .models import Application, Applicant, WorkExperience, Education, Skill, Link, ProfilePrivacySettings


@admin.action(description="Export selected applications to CSV")
def export_applications_as_csv(modeladmin, request, queryset):
    return export_applications_csv(queryset)


@admin.register(ProfilePrivacySettings)
class ProfilePrivacySettingsAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'visible_to_recruiters', 'show_email', 'show_phone', 'show_resume', 'show_gpa')
    list_filter = ('visible_to_recruiters', 'show_email', 'show_phone', 'show_resume')
    search_fields = ('applicant__account__username', 'applicant__account__email')


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('account', 'headline', 'get_email')
    search_fields = ('account__username', 'account__email', 'headline')

    def get_email(self, obj):
        return obj.account.email
    get_email.short_description = 'Email'


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class LinkInline(admin.TabularInline):
    model = Link
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "updated_at")
    list_filter = ("status", "updated_at")
    search_fields = ("job__title", "applicant__username")
    actions = [export_applications_as_csv]
