import uuid

from django.conf import settings
from django.db import models

from account.models import Account


class ProfilePrivacySettings(models.Model):
    """Privacy settings for applicant profiles - controls what recruiters can see"""
    applicant = models.OneToOneField(
        'Applicant',
        on_delete=models.CASCADE,
        related_name='privacy_settings',
        primary_key=True,
    )
    # Contact Information
    show_email = models.BooleanField(default=True, help_text="Allow recruiters to see your email")
    show_phone = models.BooleanField(default=True, help_text="Allow recruiters to see your phone number")
    show_location = models.BooleanField(default=True, help_text="Allow recruiters to see your location (city, state, country)")
    
    # Professional Information
    show_resume = models.BooleanField(default=True, help_text="Allow recruiters to see your resume")
    show_headline = models.BooleanField(default=True, help_text="Allow recruiters to see your professional headline")
    show_skills = models.BooleanField(default=True, help_text="Allow recruiters to see your skills")
    show_work_experience = models.BooleanField(default=True, help_text="Allow recruiters to see your work experience")
    show_education = models.BooleanField(default=True, help_text="Allow recruiters to see your education")
    show_links = models.BooleanField(default=True, help_text="Allow recruiters to see your portfolio/social links")
    
    # Detailed Settings
    show_gpa = models.BooleanField(default=True, help_text="Allow recruiters to see your GPA")
    show_current_employment = models.BooleanField(default=True, help_text="Allow recruiters to see your current job status")
    show_current_education = models.BooleanField(default=True, help_text="Allow recruiters to see your current education status")
    
    # Overall Visibility
    visible_to_recruiters = models.BooleanField(default=True, help_text="Make profile visible in recruiter searches")
    
    def __str__(self):
        return f"Privacy Settings for {self.applicant.account.get_full_name()}"


class Applicant(models.Model):
    account = models.OneToOneField(
        primary_key=True,
        to=Account,
        on_delete=models.CASCADE,
        related_name="applicant",
    )
    headline = models.CharField(max_length=500, blank=True)

    # TODO Include fields for resume etc, but files should be managed by an s3 bucket
    resume = models.CharField(max_length=255, blank=True, null=True)  # Link

    def get_or_create_privacy_settings(self):
        """Get or create privacy settings for this applicant"""
        settings, created = ProfilePrivacySettings.objects.get_or_create(applicant=self)
        return settings

    def get_job_recommendations(self, min_matching_skills=1):
        """
        Get job recommendations based on matching skills.
        
        Args:
            min_matching_skills (int): Minimum number of matching skills required
        
        Returns:
            QuerySet: JobPosting objects that match the criteria
        """
        from job.models import JobPosting, JobSkill
        from django.db.models import Count, Q
        
        # Get all skill names of this applicant
        applicant_skill_names = self.skills.values_list('skill_name', flat=True)
        
        if not applicant_skill_names:
            return JobPosting.objects.none()
        
        # Find jobs that have at least min_matching_skills in common
        recommended_jobs = JobPosting.objects.filter(
            is_active=True,
            required_skills__skill_name__in=applicant_skill_names
        ).annotate(
            matching_skills_count=Count('required_skills__skill_name', distinct=True)
        ).filter(
            matching_skills_count__gte=min_matching_skills
        ).order_by('-matching_skills_count', '-created_at')
        
        # Exclude jobs the applicant has already applied to
        applied_job_ids = self.account.job_applications.values_list('job_id', flat=True)
        recommended_jobs = recommended_jobs.exclude(id__in=applied_job_ids)
        
        return recommended_jobs

    def __str__(self):
        return f"{self.account.get_full_name()} - Applicant"


class WorkExperience(models.Model):
    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name="work_experiences"
    )
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-start_date"]


class Education(models.Model):
    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name="education"
    )
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-start_date"]


class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("expert", "Expert"),
    ]

    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name="skills"
    )
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.CharField(
        max_length=20, choices=PROFICIENCY_CHOICES, default="intermediate"
    )
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ["applicant", "skill_name"]


class Link(models.Model):
    PLATFORM_CHOICES = [
        ("linkedin", "LinkedIn"),
        ("github", "GitHub"),
        ("portfolio", "Portfolio Website"),
        ("personal", "Personal Website"),
        ("twitter", "Twitter"),
        ("other", "Other"),
    ]

    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name="links"
    )
    url = models.URLField()
    platform = models.CharField(
        max_length=20, choices=PLATFORM_CHOICES, default="other"
    )
    description = models.CharField(max_length=200, blank=True)


class ApplicationStatus(models.TextChoices):
    APPLIED = "applied", "Applied"
    REVIEW = "review", "Review"
    INTERVIEW = "interview", "Interview"
    OFFER = "offer", "Offer"
    CLOSED = "closed", "Closed"


class Application(models.Model):
    """A job application made by a user (applicant) to a JobPosting."""
    STATUS_FLOW = [
        ApplicationStatus.APPLIED,
        ApplicationStatus.REVIEW,
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.OFFER,
        ApplicationStatus.CLOSED,
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job = models.ForeignKey(
        "job.JobPosting",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=16,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED,
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = (("applicant", "job"),)  # one application per job per user

    def __str__(self) -> str:
        return f"{self.applicant.username} → {self.job.title} [{self.get_status_display()}]" #type: ignore

    @property
    def step(self) -> int:
        """1-based step position to drive the stepper UI in templates."""
        for i, s in enumerate(self.STATUS_FLOW, start=1):
            if self.status == s:
                return i
        return 1
