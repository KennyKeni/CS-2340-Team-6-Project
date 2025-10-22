from django.contrib import admin
from .models import Recruiter, CandidateEmail, Notification, Message, SavedSearch


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('account', 'company', 'position', 'get_email')
    search_fields = ('account__username', 'account__email', 'company', 'position')

    def get_email(self, obj):
        return obj.account.email
    get_email.short_description = 'Email'


@admin.register(CandidateEmail)
class CandidateEmailAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'is_sent', 'sent_at', 'related_job')
    list_filter = ('is_sent', 'sent_at', 'related_job')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'body')
    readonly_fields = ('sent_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'recipient', 'related_job')