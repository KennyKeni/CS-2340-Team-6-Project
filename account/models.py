import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class UserType(models.TextChoices):
    APPLICANT = "applicant", "Applicant"
    RECRUITER = "recruiter", "Recruiter"


class Account(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    profile_picture = models.CharField(max_length=255, blank=True, null=True)  # Link

    # Address
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
