from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recruiter.models import Recruiter
from applicant.models import Applicant

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample recruiter and applicant data for email testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data for email testing...'))
        
        # Create sample recruiter if it doesn't exist
        recruiter_user, created = User.objects.get_or_create(
            username='recruiter_jane',
            defaults={
                'email': 'jane.recruiter@techcorp.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'street_address': '123 Business Ave',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'United States',
                'zip_code': '94105',
            }
        )
        
        if created:
            recruiter_user.set_password('password123')
            recruiter_user.save()
        
        # Create recruiter profile
        recruiter, created = Recruiter.objects.get_or_create(
            account=recruiter_user,
            defaults={
                'company': 'TechCorp Solutions',
                'position': 'Senior Technical Recruiter'
            }
        )
        
        # Create additional sample applicants if they don't exist
        applicants_data = [
            {
                'username': 'john_dev',
                'email': 'john.dev@example.com',
                'first_name': 'John',
                'last_name': 'Developer',
                'city': 'New York',
                'state': 'NY',
            },
            {
                'username': 'sarah_eng',
                'email': 'sarah.eng@example.com', 
                'first_name': 'Sarah',
                'last_name': 'Engineer',
                'city': 'Austin',
                'state': 'TX',
            },
            {
                'username': 'mike_prog',
                'email': 'mike.prog@example.com',
                'first_name': 'Mike',
                'last_name': 'Programmer',
                'city': 'Seattle',
                'state': 'WA',
            }
        ]
        
        created_count = 0
        for applicant_data in applicants_data:
            user, created = User.objects.get_or_create(
                username=applicant_data['username'],
                defaults={
                    'email': applicant_data['email'],
                    'first_name': applicant_data['first_name'],
                    'last_name': applicant_data['last_name'],
                    'street_address': '123 Main St',
                    'city': applicant_data['city'],
                    'state': applicant_data['state'],
                    'country': 'United States',
                    'zip_code': '12345',
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                created_count += 1
                
                # Create applicant profile
                applicant, _ = Applicant.objects.get_or_create(
                    account=user,
                    defaults={
                        'headline': f'Experienced {applicant_data["last_name"]} looking for opportunities'
                    }
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- Recruiter: {recruiter.account.get_full_name()} at {recruiter.company}\n'
                f'- Created {created_count} new applicant accounts\n'
                f'- Ready to test email functionality!\n'
                f'\nLogin as recruiter:\n'
                f'  Username: recruiter_jane\n'
                f'  Password: password123\n'
            )
        )