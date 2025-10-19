from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from recruiter.models import Recruiter
from applicant.models import Applicant, WorkExperience, Education, Skill, Link
from job.models import JobPosting, JobApplication, JobSkill

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with comprehensive dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate dummy data...'))

        # Create recruiters
        recruiters = self.create_recruiters()

        # Create applicants with complete profiles
        applicants = self.create_applicants()

        # Create job postings with skills
        jobs = self.create_jobs(recruiters)

        # Create some job applications
        self.create_applications(applicants, jobs)

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Successfully populated dummy data!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('\nLOGIN CREDENTIALS:'))
        self.stdout.write(self.style.SUCCESS('\nRECRUITERS:'))
        self.stdout.write('  Username: recruiter1    Password: password123')
        self.stdout.write('  Username: recruiter_jane    Password: password123')
        self.stdout.write(self.style.SUCCESS('\nAPPLICANTS:'))
        self.stdout.write('  Username: john_dev    Password: password123')
        self.stdout.write('  Username: sarah_eng    Password: password123')
        self.stdout.write('  Username: mike_prog    Password: password123')
        self.stdout.write('  Username: alice_designer    Password: password123')
        self.stdout.write('  Username: bob_data    Password: password123')
        self.stdout.write('  Username: kenny_applicant    Password: password123')
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))

    def create_recruiters(self):
        self.stdout.write('Creating recruiters...')
        recruiters = []

        recruiter_data = [
            {
                'username': 'recruiter1',
                'email': 'recruiter@techcorp.com',
                'first_name': 'John',
                'last_name': 'Recruiter',
                'company': 'TechCorp Solutions',
                'position': 'Lead Recruiter',
                'address': {
                    'street_address': '100 Tech Drive',
                    'city': 'San Francisco',
                    'state': 'CA',
                    'country': 'United States',
                    'zip_code': '94105',
                }
            },
            {
                'username': 'recruiter_jane',
                'email': 'jane.recruiter@techcorp.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'company': 'TechCorp Solutions',
                'position': 'Senior Technical Recruiter',
                'address': {
                    'street_address': '123 Business Ave',
                    'city': 'San Francisco',
                    'state': 'CA',
                    'country': 'United States',
                    'zip_code': '94105',
                }
            },
        ]

        for data in recruiter_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_staff': True,
                    **data['address']
                }
            )

            if created:
                user.set_password('password123')
                user.save()

            recruiter, _ = Recruiter.objects.get_or_create(
                account=user,
                defaults={
                    'company': data['company'],
                    'position': data['position']
                }
            )
            recruiters.append(user)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(recruiters)} recruiters'))
        return recruiters

    def create_applicants(self):
        self.stdout.write('Creating applicants with profiles...')
        applicants = []

        applicants_data = [
            {
                'username': 'john_dev',
                'email': 'john.dev@example.com',
                'first_name': 'John',
                'last_name': 'Developer',
                'headline': 'Full-Stack Developer with 5+ years of experience in Python and React',
                'address': {
                    'street_address': '123 Main St',
                    'city': 'New York',
                    'state': 'NY',
                    'country': 'United States',
                    'zip_code': '10001',
                },
                'phone_number': '555-0101',
                'work_experiences': [
                    {
                        'company': 'Tech Innovations Inc',
                        'position': 'Senior Software Engineer',
                        'start_date': date(2020, 1, 1),
                        'end_date': None,
                        'is_current': True,
                        'description': 'Lead development of microservices architecture using Django and React',
                        'location': 'New York, NY',
                    },
                    {
                        'company': 'StartupXYZ',
                        'position': 'Software Developer',
                        'start_date': date(2018, 6, 1),
                        'end_date': date(2019, 12, 31),
                        'is_current': False,
                        'description': 'Developed full-stack web applications using Python and JavaScript',
                        'location': 'San Francisco, CA',
                    },
                ],
                'education': [
                    {
                        'institution': 'Georgia Institute of Technology',
                        'degree': 'Bachelor of Science',
                        'field_of_study': 'Computer Science',
                        'start_date': date(2014, 8, 1),
                        'end_date': date(2018, 5, 31),
                        'is_current': False,
                        'gpa': 3.75,
                    },
                ],
                'skills': [
                    {'skill_name': 'Python', 'proficiency_level': 'expert', 'years_of_experience': 5},
                    {'skill_name': 'Django', 'proficiency_level': 'expert', 'years_of_experience': 5},
                    {'skill_name': 'React', 'proficiency_level': 'advanced', 'years_of_experience': 4},
                    {'skill_name': 'PostgreSQL', 'proficiency_level': 'advanced', 'years_of_experience': 4},
                    {'skill_name': 'Docker', 'proficiency_level': 'intermediate', 'years_of_experience': 3},
                ],
                'links': [
                    {'url': 'https://github.com/johndev', 'platform': 'github'},
                    {'url': 'https://linkedin.com/in/johndev', 'platform': 'linkedin'},
                ],
            },
            {
                'username': 'sarah_eng',
                'email': 'sarah.eng@example.com',
                'first_name': 'Sarah',
                'last_name': 'Engineer',
                'headline': 'DevOps Engineer specializing in AWS and Kubernetes',
                'address': {
                    'street_address': '456 Oak Ave',
                    'city': 'Austin',
                    'state': 'TX',
                    'country': 'United States',
                    'zip_code': '78701',
                },
                'phone_number': '555-0102',
                'work_experiences': [
                    {
                        'company': 'CloudTech Inc',
                        'position': 'DevOps Engineer',
                        'start_date': date(2019, 3, 1),
                        'end_date': None,
                        'is_current': True,
                        'description': 'Manage AWS infrastructure and CI/CD pipelines',
                        'location': 'Austin, TX',
                    },
                ],
                'education': [
                    {
                        'institution': 'University of Texas at Austin',
                        'degree': 'Bachelor of Science',
                        'field_of_study': 'Computer Engineering',
                        'start_date': date(2015, 8, 1),
                        'end_date': date(2019, 5, 31),
                        'is_current': False,
                        'gpa': 3.60,
                    },
                ],
                'skills': [
                    {'skill_name': 'AWS', 'proficiency_level': 'expert', 'years_of_experience': 4},
                    {'skill_name': 'Kubernetes', 'proficiency_level': 'advanced', 'years_of_experience': 3},
                    {'skill_name': 'Docker', 'proficiency_level': 'expert', 'years_of_experience': 4},
                    {'skill_name': 'Terraform', 'proficiency_level': 'advanced', 'years_of_experience': 3},
                    {'skill_name': 'Python', 'proficiency_level': 'intermediate', 'years_of_experience': 3},
                ],
                'links': [
                    {'url': 'https://github.com/saraheng', 'platform': 'github'},
                ],
            },
            {
                'username': 'mike_prog',
                'email': 'mike.prog@example.com',
                'first_name': 'Mike',
                'last_name': 'Programmer',
                'headline': 'Frontend Developer passionate about user experience',
                'address': {
                    'street_address': '789 Pine St',
                    'city': 'Seattle',
                    'state': 'WA',
                    'country': 'United States',
                    'zip_code': '98101',
                },
                'phone_number': '555-0103',
                'work_experiences': [
                    {
                        'company': 'DesignCo',
                        'position': 'Frontend Developer',
                        'start_date': date(2021, 1, 1),
                        'end_date': None,
                        'is_current': True,
                        'description': 'Build responsive web applications with React and TypeScript',
                        'location': 'Seattle, WA',
                    },
                ],
                'education': [
                    {
                        'institution': 'University of Washington',
                        'degree': 'Bachelor of Arts',
                        'field_of_study': 'Information Systems',
                        'start_date': date(2017, 9, 1),
                        'end_date': date(2021, 6, 30),
                        'is_current': False,
                        'gpa': 3.50,
                    },
                ],
                'skills': [
                    {'skill_name': 'React', 'proficiency_level': 'expert', 'years_of_experience': 3},
                    {'skill_name': 'TypeScript', 'proficiency_level': 'advanced', 'years_of_experience': 3},
                    {'skill_name': 'CSS', 'proficiency_level': 'expert', 'years_of_experience': 4},
                    {'skill_name': 'JavaScript', 'proficiency_level': 'expert', 'years_of_experience': 4},
                ],
                'links': [
                    {'url': 'https://mikeportfolio.dev', 'platform': 'portfolio'},
                ],
            },
            {
                'username': 'alice_designer',
                'email': 'alice.designer@example.com',
                'first_name': 'Alice',
                'last_name': 'Designer',
                'headline': 'UX/UI Designer with frontend development skills',
                'address': {
                    'street_address': '321 Design Blvd',
                    'city': 'Los Angeles',
                    'state': 'CA',
                    'country': 'United States',
                    'zip_code': '90001',
                },
                'phone_number': '555-0104',
                'work_experiences': [
                    {
                        'company': 'Creative Agency',
                        'position': 'UX/UI Designer',
                        'start_date': date(2020, 6, 1),
                        'end_date': None,
                        'is_current': True,
                        'description': 'Design user interfaces and develop frontend components',
                        'location': 'Los Angeles, CA',
                    },
                ],
                'education': [
                    {
                        'institution': 'Art Center College of Design',
                        'degree': 'Bachelor of Fine Arts',
                        'field_of_study': 'Interaction Design',
                        'start_date': date(2016, 9, 1),
                        'end_date': date(2020, 5, 31),
                        'is_current': False,
                        'gpa': 3.80,
                    },
                ],
                'skills': [
                    {'skill_name': 'Figma', 'proficiency_level': 'expert', 'years_of_experience': 4},
                    {'skill_name': 'React', 'proficiency_level': 'intermediate', 'years_of_experience': 2},
                    {'skill_name': 'CSS', 'proficiency_level': 'advanced', 'years_of_experience': 4},
                    {'skill_name': 'HTML', 'proficiency_level': 'advanced', 'years_of_experience': 4},
                ],
                'links': [
                    {'url': 'https://alicedesigns.portfolio', 'platform': 'portfolio'},
                    {'url': 'https://linkedin.com/in/alicedesigner', 'platform': 'linkedin'},
                ],
            },
            {
                'username': 'bob_data',
                'email': 'bob.data@example.com',
                'first_name': 'Bob',
                'last_name': 'DataScientist',
                'headline': 'Data Scientist with expertise in machine learning and Python',
                'address': {
                    'street_address': '555 Data Lane',
                    'city': 'Boston',
                    'state': 'MA',
                    'country': 'United States',
                    'zip_code': '02101',
                },
                'phone_number': '555-0105',
                'work_experiences': [
                    {
                        'company': 'DataInsights Co',
                        'position': 'Senior Data Scientist',
                        'start_date': date(2019, 9, 1),
                        'end_date': None,
                        'is_current': True,
                        'description': 'Build machine learning models and analyze large datasets',
                        'location': 'Boston, MA',
                    },
                ],
                'education': [
                    {
                        'institution': 'MIT',
                        'degree': 'Master of Science',
                        'field_of_study': 'Data Science',
                        'start_date': date(2017, 9, 1),
                        'end_date': date(2019, 6, 30),
                        'is_current': False,
                        'gpa': 3.90,
                    },
                    {
                        'institution': 'University of California, Berkeley',
                        'degree': 'Bachelor of Science',
                        'field_of_study': 'Statistics',
                        'start_date': date(2013, 8, 1),
                        'end_date': date(2017, 5, 31),
                        'is_current': False,
                        'gpa': 3.85,
                    },
                ],
                'skills': [
                    {'skill_name': 'Python', 'proficiency_level': 'expert', 'years_of_experience': 6},
                    {'skill_name': 'Machine Learning', 'proficiency_level': 'expert', 'years_of_experience': 5},
                    {'skill_name': 'TensorFlow', 'proficiency_level': 'advanced', 'years_of_experience': 4},
                    {'skill_name': 'R', 'proficiency_level': 'advanced', 'years_of_experience': 5},
                    {'skill_name': 'SQL', 'proficiency_level': 'expert', 'years_of_experience': 6},
                ],
                'links': [
                    {'url': 'https://github.com/bobdata', 'platform': 'github'},
                    {'url': 'https://linkedin.com/in/bobdata', 'platform': 'linkedin'},
                ],
            },
            {
                'username': 'kenny_applicant',
                'email': 'linkenny717@gmail.com',
                'first_name': 'Kenny',
                'last_name': 'Lin',
                'headline': 'Software Engineer seeking new opportunities',
                'address': {
                    'street_address': '123 Tech Street',
                    'city': 'Atlanta',
                    'state': 'GA',
                    'country': 'United States',
                    'zip_code': '30332',
                },
                'phone_number': '555-0106',
                'work_experiences': [
                    {
                        'company': 'Tech Company',
                        'position': 'Software Engineer',
                        'start_date': date(2022, 1, 1),
                        'end_date': None,
                        'is_current': True,
                        'description': 'Developing web applications using modern technologies',
                        'location': 'Atlanta, GA',
                    },
                ],
                'education': [
                    {
                        'institution': 'Georgia Institute of Technology',
                        'degree': 'Bachelor of Science',
                        'field_of_study': 'Computer Science',
                        'start_date': date(2020, 8, 1),
                        'end_date': date(2024, 5, 31),
                        'is_current': False,
                        'gpa': 3.70,
                    },
                ],
                'skills': [
                    {'skill_name': 'Python', 'proficiency_level': 'advanced', 'years_of_experience': 3},
                    {'skill_name': 'Django', 'proficiency_level': 'intermediate', 'years_of_experience': 2},
                    {'skill_name': 'JavaScript', 'proficiency_level': 'advanced', 'years_of_experience': 3},
                    {'skill_name': 'React', 'proficiency_level': 'intermediate', 'years_of_experience': 2},
                ],
                'links': [
                    {'url': 'https://github.com/linkenny', 'platform': 'github'},
                ],
            },
        ]

        for data in applicants_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone_number': data.get('phone_number', ''),
                    **data['address']
                }
            )

            if created:
                user.set_password('password123')
                user.save()

            applicant, _ = Applicant.objects.get_or_create(
                account=user,
                defaults={'headline': data['headline']}
            )

            # Add work experiences
            for exp in data.get('work_experiences', []):
                WorkExperience.objects.get_or_create(
                    applicant=applicant,
                    company=exp['company'],
                    position=exp['position'],
                    defaults=exp
                )

            # Add education
            for edu in data.get('education', []):
                Education.objects.get_or_create(
                    applicant=applicant,
                    institution=edu['institution'],
                    degree=edu['degree'],
                    defaults=edu
                )

            # Add skills
            for skill in data.get('skills', []):
                Skill.objects.get_or_create(
                    applicant=applicant,
                    skill_name=skill['skill_name'],
                    defaults=skill
                )

            # Add links
            for link in data.get('links', []):
                Link.objects.get_or_create(
                    applicant=applicant,
                    url=link['url'],
                    defaults=link
                )

            applicants.append(user)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(applicants)} applicants with complete profiles'))
        return applicants

    def create_jobs(self, recruiters):
        self.stdout.write('Creating job postings with skills...')
        jobs = []

        if not recruiters:
            self.stdout.write(self.style.WARNING('  No recruiters available, skipping job creation'))
            return jobs

        recruiter = recruiters[0]

        jobs_data = [
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
                'skills': ['Python', 'Django', 'PostgreSQL', 'Docker', 'Redis'],
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
                'skills': ['React', 'TypeScript', 'JavaScript', 'CSS'],
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
                'skills': ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'Python'],
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
                'skills': ['Python', 'Machine Learning', 'TensorFlow', 'R', 'SQL'],
            },
            {
                'title': 'Full Stack Developer',
                'company': 'InnovateTech',
                'location': 'Seattle, WA',
                'job_type': 'full-time',
                'description': 'We are seeking a Full Stack Developer to work on our web applications. You will work with both frontend and backend technologies.',
                'requirements': '• 3+ years of full-stack development experience\n• Proficiency in React and Python/Django\n• Experience with PostgreSQL\n• Understanding of RESTful API design\n• Strong problem-solving skills',
                'benefits': '• Competitive salary and bonus\n• Comprehensive health benefits\n• Stock options\n• Flexible work arrangements\n• Professional development opportunities',
                'salary_min': 90000,
                'salary_max': 130000,
                'skills': ['Python', 'Django', 'React', 'PostgreSQL', 'JavaScript'],
            },
        ]

        for job_data in jobs_data:
            skills = job_data.pop('skills', [])
            job, created = JobPosting.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults={
                    'owner': recruiter,
                    **job_data
                }
            )

            if created:
                for skill_name in skills:
                    JobSkill.objects.create(
                        job=job,
                        skill_name=skill_name,
                        importance_level='required'
                    )

            jobs.append(job)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(jobs)} job postings with skills'))
        return jobs

    def create_applications(self, applicants, jobs):
        self.stdout.write('Creating job applications...')

        if not applicants or not jobs:
            self.stdout.write(self.style.WARNING('  No applicants or jobs available, skipping applications'))
            return

        applications_data = [
            {
                'applicant': applicants[0],
                'job': jobs[0],
                'personalized_note': 'I am very excited about this opportunity. My 5+ years of Python and Django experience align perfectly with your requirements.',
                'status': 'pending',
            },
            {
                'applicant': applicants[0],
                'job': jobs[4],
                'personalized_note': 'I have extensive experience with both frontend and backend development, making me a great fit for this full-stack role.',
                'status': 'reviewed',
            },
            {
                'applicant': applicants[1],
                'job': jobs[2],
                'personalized_note': 'With my DevOps expertise in AWS and Kubernetes, I believe I can contribute significantly to your infrastructure team.',
                'status': 'shortlisted',
            },
            {
                'applicant': applicants[2],
                'job': jobs[1],
                'personalized_note': 'I am passionate about creating beautiful user interfaces and have extensive React experience.',
                'status': 'pending',
            },
            {
                'applicant': applicants[4],
                'job': jobs[3],
                'personalized_note': 'My Master\'s degree from MIT and 5 years of ML experience make me an ideal candidate for this data scientist position.',
                'status': 'reviewed',
            },
        ]

        created_count = 0
        for app_data in applications_data:
            _, created = JobApplication.objects.get_or_create(
                applicant=app_data['applicant'],
                job=app_data['job'],
                defaults={
                    'personalized_note': app_data['personalized_note'],
                    'status': app_data['status'],
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} job applications'))
