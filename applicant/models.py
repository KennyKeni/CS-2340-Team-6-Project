import uuid

from django.db import models

from account.models import Account


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
