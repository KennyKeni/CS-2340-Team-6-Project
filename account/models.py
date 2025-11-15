# account/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Includes address, profile, and commute preference fields.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    profile_picture = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # Address fields
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)

    # Geographic coordinates (for map visualization)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # 🚗 Commute preferences (new)
    COMMUTE_CHOICES = [
        ('driving', 'Driving 🚗'),
        ('transit', 'Public Transit 🚆'),
        ('walking', 'Walking 🚶'),
        ('bicycling', 'Bicycling 🚴'),
    ]

    preferred_commute_radius = models.FloatField(
        default=25,
        help_text="Preferred commuting distance in miles."
    )

    preferred_commute_mode = models.CharField(
        max_length=20,
        choices=COMMUTE_CHOICES,
        default='driving',
        help_text="Preferred mode of transportation."
    )

    preferred_commute_time = models.IntegerField(
        default=30,
        help_text="Preferred maximum commute time in minutes."
    )

    def __str__(self):
        """String representation of the user."""
        return self.username
