import uuid
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


