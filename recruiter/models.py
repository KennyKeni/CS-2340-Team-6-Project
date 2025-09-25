from django.conf import settings
from django.db import models
import uuid
from account.models import Account


class JobPosting(models.Model):
    """A simple job posting owned by a recruiter."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_postings",
    )
    title = models.CharField(max_length=200)
    summary = models.TextField(max_length=2000, help_text="Short role summary.")
    responsibilities = models.TextField(
        help_text="List responsibilities (one per line).",
        blank=True,
    )
    salary = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: $80k–$100k or $45/hr",
    )
    work_hours = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: Full-time, 40hrs/wk, M–F",
    )
    skills_required = models.TextField(
        help_text="List skills (comma- or line-separated).",
        blank=True,
    )
    location = models.CharField(max_length=255, blank=True)
    remote = models.BooleanField(default=False, help_text="Is this job remote?")
    visa_sponsorship = models.BooleanField(default=False, help_text="Visa sponsorship available?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.owner.username})"


class Recruiter(models.Model):
    account = models.OneToOneField(
        primary_key=True,
        to=Account,
        on_delete=models.CASCADE,
        related_name="recruiter",
    )
    company = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=200, blank=True)
