from django.contrib import admin
from .models import Recruiter, Notification, Message, SavedSearch, CandidateEmail


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('account', 'company', 'position', 'get_email')
    search_fields = ('account__username', 'account__email', 'company', 'position')

    def get_email(self, obj):
        return obj.account.email
    get_email.short_description = 'Email'


@admin.register(CandidateEmail)
class CandidateEmailAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'related_job', 'is_sent', 'sent_at')
    list_filter = ('is_sent', 'sent_at')
    search_fields = ('sender__username', 'sender__email', 'recipient__username', 'recipient__email', 'subject', 'body')
    readonly_fields = ('sent_at',)
    date_hierarchy = 'sent_at'

