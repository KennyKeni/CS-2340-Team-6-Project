from django.core.management.base import BaseCommand
from account.models import Account
from account.utils import geocode_applicant_address


class Command(BaseCommand):
    help = 'Geocode all account addresses that do not have coordinates yet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-geocode all accounts, even those with existing coordinates',
        )

    def handle(self, *args, **options):
        force = options['force']

        if force:
            accounts = Account.objects.all()
            self.stdout.write('Geocoding ALL accounts (force mode)...')
        else:
            accounts = Account.objects.filter(latitude__isnull=True)
            self.stdout.write('Geocoding accounts without coordinates...')

        total = accounts.count()
        self.stdout.write(f'Found {total} accounts to geocode')

        success_count = 0
        failed_count = 0

        for account in accounts:
            # Check if account has required address fields
            if not account.city or not account.state:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping {account.username}: Missing city or state'
                    )
                )
                failed_count += 1
                continue

            # Geocode the address
            latitude, longitude = geocode_applicant_address(
                street_address=account.street_address or "",
                city=account.city or "",
                state=account.state or "",
                zip_code=account.zip_code or "",
                country=account.country or "USA",
                use_exact=True
            )

            if latitude and longitude:
                account.latitude = latitude
                account.longitude = longitude
                account.save(update_fields=['latitude', 'longitude'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Geocoded {account.username}: ({latitude}, {longitude})'
                    )
                )
                success_count += 1
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to geocode {account.username}'
                    )
                )
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {success_count} successful, {failed_count} failed out of {total} total'
            )
        )
