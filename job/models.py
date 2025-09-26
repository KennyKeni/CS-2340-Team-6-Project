from django.conf import settings
from django.db import models
from recruiter.models import JobPosting

# class Application(models.Model):
#     job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="job_applications", related_query_name="job_application")
#     applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_applications", related_query_name="job_application")
#     note = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=["job", "applicant"], name="unique_application_per_user_per_job"),
#         ]
#         ordering = ["-created_at"]
#
#     def __str__(self) -> str:
#         return f"{self.applicant} → {self.job}"