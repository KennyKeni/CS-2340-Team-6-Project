from django.contrib import admin
from .models import Recruiter, Notification, Message, SavedSearch


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('account', 'company', 'position', 'get_email')
    search_fields = ('account__username', 'account__email', 'company', 'position')

    def get_email(self, obj):
        return obj.account.email
    get_email.short_description = 'Email'

