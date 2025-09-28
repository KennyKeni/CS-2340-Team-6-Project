from django.db import models
from django.utils import timezone
from account.models import Account


class JobPosting(models.Model):
    """Job posting model"""
    owner = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='job_postings',
    )
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, default="")
    location = models.CharField(max_length=200, default="")
    job_type = models.CharField(
        max_length=50,
        choices=[
            ('full-time', 'Full Time'),
            ('part-time', 'Part Time'),
            ('contract', 'Contract'),
            ('internship', 'Internship'),
            ('remote', 'Remote'),
        ],
        default='full-time'
    )
    description = models.TextField(max_length=2000, help_text="Job description and summary.", default="")
    requirements = models.TextField(blank=True, help_text="Job requirements.")
    benefits = models.TextField(blank=True, help_text="Benefits and perks.")
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    visa_sponsorship = models.BooleanField(default=False, help_text="Visa sponsorship available?")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    application_deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.owner.username})"


class JobApplication(models.Model):
    """Job application model with personalized notes"""
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='job_applications')
    applicant = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='job_applications',
# Note: limit_choices_to removed as user_type field no longer exists
    )
    personalized_note = models.TextField(
        blank=True,
        help_text="Add a personalized note to make your application stand out"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('hired', 'Hired'),
        ],
        default='pending'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.get_full_name()} applied to {self.job.title}"
