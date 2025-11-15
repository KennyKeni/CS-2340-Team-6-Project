from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Account
from .utils import geocode_applicant_address


@receiver(pre_save, sender=Account)
def geocode_account_address(sender, instance, **kwargs):
    """
    Automatically geocode the account's address when it changes.

    This signal fires before saving an Account and updates the latitude/longitude
    fields based on the address. For new accounts, it always geocodes.
    For existing accounts, it only geocodes if address fields have changed.
    """
    # Check if this is a new account or if address fields have changed
    address_changed = False

    if instance.pk:
        # This is an existing account - check if address changed
        try:
            old_instance = Account.objects.get(pk=instance.pk)
            address_fields = ['street_address', 'city', 'state', 'zip_code', 'country']

            for field in address_fields:
                old_value = getattr(old_instance, field, None)
                new_value = getattr(instance, field, None)
                if old_value != new_value:
                    address_changed = True
                    break
        except Account.DoesNotExist:
            # Shouldn't happen, but treat as new account
            address_changed = True
    else:
        # New account - always geocode
        address_changed = True

    # Only geocode if address changed
    if address_changed:
        # Always geocode with exact address for the Account model
        # Privacy is handled at the view/template layer, not in the model
        latitude, longitude = geocode_applicant_address(
            street_address=instance.street_address or "",
            city=instance.city or "",
            state=instance.state or "",
            zip_code=instance.zip_code or "",
            country=instance.country or "USA",
            use_exact=True  # Always use exact for storage; privacy filter at display time
        )

        instance.latitude = latitude
        instance.longitude = longitude
