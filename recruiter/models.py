import uuid

from django.conf import settings
from django.db import models

from account.models import Account


class Recruiter(models.Model):
    account = models.OneToOneField(
        primary_key=True,
        to=Account,
        on_delete=models.CASCADE,
        related_name="recruiter",
    )
    company = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.account.get_full_name()} - {self.company}"


class Notification(models.Model):
    """Model for platform notifications"""
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('saved_search_match', 'Saved Search Match'),
        ('application_update', 'Application Update'),
        ('job_match', 'Job Match'),
        ('system', 'System Notification'),
    ]
    
    recipient = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional references
    related_job = models.ForeignKey(
        'job.JobPosting',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    related_application = models.ForeignKey(
        'applicant.Application',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    related_message = models.ForeignKey(
        'recruiter.Message',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username}: {self.title}"


class Message(models.Model):
    """Model for direct messaging between recruiters and candidates"""
    sender = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional job reference
    related_job = models.ForeignKey(
        'job.JobPosting',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.subject[:50]}"


class SavedSearch(models.Model):
    """Model for saved candidate searches"""
    recruiter = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )
    name = models.CharField(max_length=100, help_text="Name for this saved search")
    
    # Search criteria
    skills = models.JSONField(default=list, help_text="List of required skills")
    location = models.CharField(max_length=200, blank=True)
    min_experience = models.PositiveIntegerField(null=True, blank=True)
    max_experience = models.PositiveIntegerField(null=True, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    job_types = models.JSONField(default=list, help_text="List of preferred job types")
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_notification_sent = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recruiter.username}: {self.name}"