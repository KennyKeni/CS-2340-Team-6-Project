from django.db import models
from django.utils import timezone
from account.models import Account


class JobPosting(models.Model):
    """Job posting model with geographic coordinates for map view"""
    owner = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='job_postings',
    )
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, default="")
    location = models.CharField(max_length=200, default="")

    street_address = models.CharField(max_length=200, blank=True, help_text="Street address")
    city = models.CharField(max_length=100, blank=True, help_text="City")
    state = models.CharField(max_length=100, blank=True, help_text="State/Province")
    zip_code = models.CharField(max_length=20, blank=True, help_text="ZIP/Postal code")
    country = models.CharField(max_length=100, blank=True, default="USA", help_text="Country")

    # 🌍 Added for User Story 7–9
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude for map display")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude for map display")

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


class JobSkill(models.Model):
    """Required skills for a job posting"""
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='required_skills')
    skill_name = models.CharField(max_length=100)
    importance_level = models.CharField(
        max_length=20,
        choices=[
            ('required', 'Required'),
            ('preferred', 'Preferred'),
            ('nice_to_have', 'Nice to Have'),
        ],
        default='required'
    )

    class Meta:
        unique_together = ['job', 'skill_name']

    def __str__(self):
        return f"{self.job.title} - {self.skill_name}"
