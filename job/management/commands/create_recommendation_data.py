from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from job.models import JobPosting, JobSkill
from applicant.models import Applicant, Skill as ApplicantSkill
from recruiter.models import Recruiter

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample job recommendations data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data for job recommendations...'))
        
        # Create sample users if they don't exist
        recruiter_user, created = User.objects.get_or_create(
            username='recruiter1',
            defaults={
                'email': 'recruiter1@example.com',
                'first_name': 'Jane',
                'last_name': 'Recruiter',
            }
        )
        
        applicant_user, created = User.objects.get_or_create(
            username='applicant1',
            defaults={
                'email': 'applicant1@example.com',
                'first_name': 'John',
                'last_name': 'Developer',
            }
        )
        
        # Create recruiter and applicant profiles
        recruiter, created = Recruiter.objects.get_or_create(account=recruiter_user)
        applicant, created = Applicant.objects.get_or_create(account=applicant_user)
        
        # Add skills to the applicant
        applicant_skills = [
            {'skill_name': 'Python', 'proficiency_level': 'advanced'},
            {'skill_name': 'JavaScript', 'proficiency_level': 'intermediate'},
            {'skill_name': 'React', 'proficiency_level': 'intermediate'},
            {'skill_name': 'Django', 'proficiency_level': 'advanced'},
            {'skill_name': 'SQL', 'proficiency_level': 'intermediate'},
        ]
        
        for skill_data in applicant_skills:
            ApplicantSkill.objects.get_or_create(
                applicant=applicant,
                skill_name=skill_data['skill_name'],
                defaults={'proficiency_level': skill_data['proficiency_level']}
            )
        
        # Create sample job postings with required skills
        jobs_data = [
            {
                'title': 'Python Developer',
                'company': 'Tech Corp',
                'location': 'San Francisco, CA',
                'description': 'Looking for an experienced Python developer to join our team.',
                'skills': ['Python', 'Django', 'SQL']
            },
            {
                'title': 'Full Stack Developer',
                'company': 'StartupXYZ',
                'location': 'New York, NY',
                'description': 'Full stack developer position with modern technologies.',
                'skills': ['JavaScript', 'React', 'Python', 'SQL']
            },
            {
                'title': 'Frontend Developer',
                'company': 'Design Studio',
                'location': 'Austin, TX',
                'description': 'Frontend developer specializing in React applications.',
                'skills': ['JavaScript', 'React', 'CSS', 'HTML']
            },
            {
                'title': 'Backend Engineer',
                'company': 'Data Solutions',
                'location': 'Seattle, WA',
                'description': 'Backend engineer for scalable web applications.',
                'skills': ['Python', 'Django', 'PostgreSQL', 'Redis']
            },
            {
                'title': 'Software Engineer',
                'company': 'Enterprise Corp',
                'location': 'Chicago, IL',
                'description': 'Software engineer for enterprise applications.',
                'skills': ['Java', 'Spring', 'SQL', 'AWS']
            },
            {
                'title': 'Web Developer',
                'company': 'Creative Agency',
                'location': 'Los Angeles, CA',
                'description': 'Web developer for client projects.',
                'skills': ['JavaScript', 'HTML', 'CSS', 'WordPress']
            }
        ]
        
        for job_data in jobs_data:
            # Create or get the job posting
            job, created = JobPosting.objects.get_or_create(
                title=job_data['title'],
                owner=recruiter_user,
                defaults={
                    'company': job_data['company'],
                    'location': job_data['location'],
                    'description': job_data['description'],
                    'salary_min': 70000,
                    'salary_max': 120000,
                }
            )
            
            # Add required skills to the job
            for skill_name in job_data['skills']:
                JobSkill.objects.get_or_create(
                    job=job,
                    skill_name=skill_name,
                    defaults={'importance_level': 'required'}
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- Applicant with {len(applicant_skills)} skills\n'
                f'- {len(jobs_data)} job postings with required skills\n'
                f'- Ready to test job recommendations!'
            )
        )