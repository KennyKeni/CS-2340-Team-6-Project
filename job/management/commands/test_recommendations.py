from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from applicant.models import Applicant

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the job recommendation system'

    def handle(self, *args, **options):
        self.stdout.write("Testing Job Recommendation System")
        self.stdout.write("=" * 50)
        
        try:
            user = User.objects.get(username='applicant1')
            applicant = user.applicant
            self.stdout.write(f"Applicant: {applicant.account.get_full_name()}")
            
            # Show applicant skills
            skills = applicant.skills.all()
            self.stdout.write(f"\nApplicant Skills ({skills.count()}):")
            for skill in skills:
                self.stdout.write(f"  - {skill.skill_name} ({skill.proficiency_level})")
            
            # Test recommendations with minimum 1 matching skill
            self.stdout.write(f"\n--- Recommendations with minimum 1 matching skill ---")
            recommendations = applicant.get_job_recommendations(min_matching_skills=1)
            
            self.stdout.write(f"Found {recommendations.count()} job recommendations")
            
            for job in recommendations[:3]:  # Show first 3
                job_skills = list(job.required_skills.values_list('skill_name', flat=True))
                applicant_skill_names = set(skills.values_list('skill_name', flat=True))
                matching_skills = set(job_skills).intersection(applicant_skill_names)
                
                self.stdout.write(f"  📋 {job.title} at {job.company}")
                self.stdout.write(f"     Required: {job_skills}")
                self.stdout.write(f"     Matches: {list(matching_skills)} ({len(matching_skills)} skills)")
                self.stdout.write("")
            
            # Test with different minimum requirements
            for min_skills in [2, 3, 4]:
                self.stdout.write(f"\n--- Recommendations with minimum {min_skills} matching skills ---")
                recommendations = applicant.get_job_recommendations(min_matching_skills=min_skills)
                self.stdout.write(f"Found {recommendations.count()} job recommendations")
            
            self.stdout.write(self.style.SUCCESS("✅ Job recommendation system is working correctly!"))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Test user 'applicant1' not found. Run create_recommendation_data first."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))