from django.core.management.base import BaseCommand
from account.models import Account
from job.utils import geocode_address


class Command(BaseCommand):
    help = 'Geocode addresses for all users who have an address but no lat/lng coordinates'

    def handle(self, *args, **options):
        users_without_coords = Account.objects.filter(
            street_address__isnull=False,
            city__isnull=False,
            state__isnull=False,
        ).filter(
            latitude__isnull=True
        ) | Account.objects.filter(
            longitude__isnull=True
        )

        total = users_without_coords.count()
        self.stdout.write(f"Found {total} users without coordinates")

        updated = 0
        failed = 0

        for user in users_without_coords:
            self.stdout.write(f"Geocoding address for {user.username}...")

            latitude, longitude = geocode_address(
                street_address=user.street_address or '',
                city=user.city or '',
                state=user.state or '',
                zip_code=user.zip_code or '',
                country=user.country or 'USA'
            )

            if latitude and longitude:
                user.latitude = latitude
                user.longitude = longitude
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Updated {user.username}: ({latitude}, {longitude})"
                    )
                )
                updated += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ✗ Failed to geocode address for {user.username}"
                    )
                )
                failed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nComplete! Updated {updated} users, {failed} failed"
            )
        )
