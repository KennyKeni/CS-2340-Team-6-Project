from django.contrib import admin
from .models import Recruiter

@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('account', 'company', 'position')
    search_fields = ('account__username', 'company', 'position')

# JobPosting admin moved to job/admin.py