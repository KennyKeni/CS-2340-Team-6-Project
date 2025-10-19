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


class CandidateEmail(models.Model):
    """Model to track emails sent from recruiters to candidates"""
    sender = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='sent_emails',
        help_text="Recruiter who sent the email"
    )
    recipient = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='received_emails',
        help_text="Candidate who received the email"
    )
    subject = models.CharField(max_length=500)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False, help_text="Whether email was successfully sent")
    error_message = models.TextField(blank=True, help_text="Error message if email failed to send")
    
    # Optional job reference
    related_job = models.ForeignKey(
        'job.JobPosting', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Job posting this email is related to"
    )
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Candidate Email"
        verbose_name_plural = "Candidate Emails"
    
    def __str__(self):
        return f"{self.sender.get_full_name()} → {self.recipient.get_full_name()}: {self.subject[:50]}"
