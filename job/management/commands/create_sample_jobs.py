from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from job.models import JobPosting
from django.contrib.auth.models import Group

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample job postings for testing'

    def handle(self, *args, **options):
        # Get or create a recruiter user
        recruiter, created = User.objects.get_or_create(
            username='recruiter1',
            defaults={
                'email': 'recruiter@techcorp.com',
                'first_name': 'John',
                'last_name': 'Recruiter',
# User will be added to recruiter group below
                'is_staff': True
            }
        )
        
        if created:
            recruiter.set_password('password123')
            recruiter.save()
            # Add user to recruiter group
            recruiter_group, _ = Group.objects.get_or_create(name='recruiter')
            recruiter.groups.add(recruiter_group)
            self.stdout.write(self.style.SUCCESS('Created recruiter user'))

        # Sample jobs data
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'company': 'TechCorp Solutions',
                'location': 'San Francisco, CA',
                'job_type': 'full-time',
                'description': 'We are looking for a Senior Python Developer to join our growing team. You will be responsible for developing and maintaining our core backend services using Django, FastAPI, and modern Python frameworks.',
                'requirements': '• 5+ years of Python development experience\n• Strong knowledge of Django and FastAPI\n• Experience with PostgreSQL and Redis\n• Familiarity with Docker and Kubernetes\n• Bachelor\'s degree in Computer Science or related field',
                'benefits': '• Competitive salary and equity\n• Health, dental, and vision insurance\n• Flexible work arrangements\n• Professional development budget\n• 401(k) matching',
                'salary_min': 120000,
                'salary_max': 160000,
            },
            {
                'title': 'Frontend React Developer',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'job_type': 'full-time',
                'description': 'Join our dynamic startup as a Frontend React Developer. You will work on building beautiful, responsive user interfaces for our web applications.',
                'requirements': '• 3+ years of React.js experience\n• Proficiency in TypeScript\n• Experience with modern CSS frameworks\n• Knowledge of state management (Redux, Zustand)\n• Understanding of RESTful APIs',
                'benefits': '• Remote work flexibility\n• Stock options\n• Health insurance\n• Learning and development opportunities',
                'salary_min': 80000,
                'salary_max': 120000,
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudTech Inc',
                'location': 'Austin, TX',
                'job_type': 'full-time',
                'description': 'We need a DevOps Engineer to help us scale our infrastructure and improve our deployment processes. You will work with AWS, Docker, and Kubernetes.',
                'requirements': '• 4+ years of DevOps experience\n• Strong AWS knowledge\n• Experience with Docker and Kubernetes\n• CI/CD pipeline experience\n• Infrastructure as Code (Terraform)',
                'benefits': '• Competitive salary\n• Comprehensive benefits package\n• Flexible PTO\n• Gym membership\n• Professional development',
                'salary_min': 100000,
                'salary_max': 140000,
            },
            {
                'title': 'Data Scientist',
                'company': 'DataInsights Co',
                'location': 'New York, NY',
                'job_type': 'full-time',
                'description': 'Join our data science team to build machine learning models and extract insights from large datasets. You will work with Python, R, and modern ML frameworks.',
                'requirements': '• PhD or Master\'s in Data Science, Statistics, or related field\n• 3+ years of machine learning experience\n• Proficiency in Python and R\n• Experience with TensorFlow or PyTorch\n• Strong statistical background',
                'benefits': '• Excellent compensation package\n• Health and dental insurance\n• Flexible work schedule\n• Research and conference budget\n• 401(k) with company matching',
                'salary_min': 110000,
                'salary_max': 150000,
            },
            {
                'title': 'Product Manager',
                'company': 'InnovateTech',
                'location': 'Seattle, WA',
                'job_type': 'full-time',
                'description': 'Lead product development for our flagship software platform. You will work closely with engineering, design, and business teams to deliver exceptional user experiences.',
                'requirements': '• 5+ years of product management experience\n• Technical background preferred\n• Experience with agile methodologies\n• Strong analytical and communication skills\n• MBA or equivalent experience',
                'benefits': '• Competitive salary and bonus\n• Comprehensive health benefits\n• Stock options\n• Flexible work arrangements\n• Professional development opportunities',
                'salary_min': 130000,
                'salary_max': 180000,
            }
        ]

        created_count = 0
        for job_data in sample_jobs:
            job, created = JobPosting.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults={
                    'owner': recruiter,
                    'location': job_data['location'],
                    'job_type': job_data['job_type'],
                    'description': job_data['description'],
                    'requirements': job_data['requirements'],
                    'benefits': job_data['benefits'],
                    'salary_min': job_data['salary_min'],
                    'salary_max': job_data['salary_max'],
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample jobs')
        )
