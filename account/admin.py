from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from utils.export import export_users_csv

from .admin_utils import change_user_role, get_user_role, ban_users, unban_users

User = get_user_model()


@admin.action(description="Export all selected users to CSV")
def export_users_as_csv(modeladmin, request, queryset):
    return export_users_csv(queryset, role_filter='all')


@admin.action(description="Export selected users (Applicants only) to CSV")
def export_applicants_as_csv(modeladmin, request, queryset):
    applicants = queryset.filter(applicant__isnull=False)
    return export_users_csv(applicants, role_filter='applicant')


@admin.action(description="Export selected users (Recruiters only) to CSV")
def export_recruiters_as_csv(modeladmin, request, queryset):
    recruiters = queryset.filter(recruiter__isnull=False)
    return export_users_csv(recruiters, role_filter='recruiter')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'groups', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    actions = [
        export_users_as_csv,
        export_applicants_as_csv,
        export_recruiters_as_csv,
        'change_to_applicant',
        'change_to_recruiter',
        'ban_selected_users',
        'unban_selected_users',
    ]

    def get_role(self, obj):
        role = get_user_role(obj)
        return role.replace('_', ' ').title()
    get_role.short_description = 'Role'

    @admin.action(description='Change role to Applicant')
    def change_to_applicant(self, request, queryset):
        success_count = 0
        for user in queryset:
            success, message = change_user_role(user, 'applicant')
            if success:
                success_count += 1
        self.message_user(request, f'Successfully changed {success_count} user(s) to Applicant role.')

    @admin.action(description='Change role to Recruiter')
    def change_to_recruiter(self, request, queryset):
        success_count = 0
        for user in queryset:
            success, message = change_user_role(user, 'recruiter')
            if success:
                success_count += 1
        self.message_user(request, f'Successfully changed {success_count} user(s) to Recruiter role.')

    @admin.action(description='Ban selected users')
    def ban_selected_users(self, request, queryset):
        count = ban_users(queryset)
        self.message_user(request, f'Successfully banned {count} user(s).')

    @admin.action(description='Unban selected users')
    def unban_selected_users(self, request, queryset):
        count = unban_users(queryset)
        self.message_user(request, f'Successfully unbanned {count} user(s).')
