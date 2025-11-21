from django.db import models
from django.db.models import Q
from django.utils import timezone
from account.models import Account


class JobPosting(models.Model):
    """Job posting model with geographic coordinates for map view"""
    owner = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='job_postings',
    )
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, default="")
    location = models.CharField(max_length=200, default="")

    street_address = models.CharField(max_length=200, blank=True, help_text="Street address")
    city = models.CharField(max_length=100, blank=True, help_text="City")
    state = models.CharField(max_length=100, blank=True, help_text="State/Province")
    zip_code = models.CharField(max_length=20, blank=True, help_text="ZIP/Postal code")
    country = models.CharField(max_length=100, blank=True, default="USA", help_text="Country")

    # 🌍 Added for User Story 7–9
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude for map display")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude for map display")

    job_type = models.CharField(
        max_length=50,
        choices=[
            ('full-time', 'Full Time'),
            ('part-time', 'Part Time'),
            ('contract', 'Contract'),
            ('internship', 'Internship'),
            ('remote', 'Remote'),
        ],
        default='full-time'
    )
    description = models.TextField(max_length=2000, help_text="Job description and summary.", default="")
    requirements = models.TextField(blank=True, help_text="Job requirements.")
    benefits = models.TextField(blank=True, help_text="Benefits and perks.")
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    visa_sponsorship = models.BooleanField(default=False, help_text="Visa sponsorship available?")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    application_deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def get_candidate_recommendations(self, min_matching_skills=1, include_applied=True):
        """
        Get candidate recommendations based on matching skills.
        
        Args:
            min_matching_skills (int): Minimum number of matching skills required
            include_applied (bool): Whether to include candidates who have already applied
        
        Returns:
            QuerySet: Applicant objects with annotations (total_match_score, has_applied, matching_skills)
        """
        from applicant.models import Applicant, Skill, ProfilePrivacySettings
        from applicant.models import Application
        
        # Get all job skills for this job
        job_skills = self.required_skills.all()
        
        if not job_skills.exists():
            return Applicant.objects.none()
        
        # Get skill names by importance level
        required_skill_names = list(job_skills.filter(importance_level='required').values_list('skill_name', flat=True))
        preferred_skill_names = list(job_skills.filter(importance_level='preferred').values_list('skill_name', flat=True))
        nice_to_have_skill_names = list(job_skills.filter(importance_level='nice_to_have').values_list('skill_name', flat=True))
        
        all_job_skill_names = required_skill_names + preferred_skill_names + nice_to_have_skill_names
        
        if not all_job_skill_names:
            return Applicant.objects.none()
        
        # Start with applicants who have at least one matching skill and are visible to recruiters
        applicants = Applicant.objects.filter(
            Q(privacy_settings__visible_to_recruiters=True) | Q(privacy_settings__isnull=True),
            skills__skill_name__in=all_job_skill_names
        ).select_related('account', 'privacy_settings').prefetch_related('skills').distinct()
        
        # Calculate match score for each applicant
        # We'll use annotations to calculate the weighted score
        applicants_with_scores = []
        
        for applicant in applicants:
            # Get applicant's skill names
            applicant_skill_names = set(applicant.skills.values_list('skill_name', flat=True))
            
            # Calculate weighted score
            match_score = 0
            matching_skills = []
            
            # Count required skills (3 points each)
            for skill_name in required_skill_names:
                if skill_name in applicant_skill_names:
                    match_score += 3
                    matching_skills.append({'name': skill_name, 'level': 'required'})
            
            # Count preferred skills (2 points each)
            for skill_name in preferred_skill_names:
                if skill_name in applicant_skill_names:
                    match_score += 2
                    matching_skills.append({'name': skill_name, 'level': 'preferred'})
            
            # Count nice-to-have skills (1 point each)
            for skill_name in nice_to_have_skill_names:
                if skill_name in applicant_skill_names:
                    match_score += 1
                    matching_skills.append({'name': skill_name, 'level': 'nice_to_have'})
            
            # Check if minimum matching skills requirement is met
            if len(matching_skills) < min_matching_skills:
                continue
            
            # Check if applicant has already applied
            has_applied = Application.objects.filter(
                job=self,
                applicant=applicant.account
            ).exists()
            
            # Store the score and matching skills as attributes
            applicant.total_match_score = match_score
            applicant.has_applied = has_applied
            applicant.matching_skills = matching_skills
            
            applicants_with_scores.append(applicant)
        
        # Filter out applied candidates if include_applied is False
        if not include_applied:
            applicants_with_scores = [a for a in applicants_with_scores if not a.has_applied]
        
        # Sort by match score DESC, then by account creation date
        applicants_with_scores.sort(
            key=lambda x: (-x.total_match_score, x.account.date_joined)
        )
        
        return applicants_with_scores

    def __str__(self):
        return f"{self.title} ({self.owner.username})"


class JobApplication(models.Model):
    """Job application model with personalized notes"""
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='job_applications')
    applicant = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='job_applications',
    )
    personalized_note = models.TextField(
        blank=True,
        help_text="Add a personalized note to make your application stand out"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('hired', 'Hired'),
        ],
        default='pending'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.get_full_name()} applied to {self.job.title}"


class JobSkill(models.Model):
    """Required skills for a job posting"""
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='required_skills')
    skill_name = models.CharField(max_length=100)
    importance_level = models.CharField(
        max_length=20,
        choices=[
            ('required', 'Required'),
            ('preferred', 'Preferred'),
            ('nice_to_have', 'Nice to Have'),
        ],
        default='required'
    )

    class Meta:
        unique_together = ['job', 'skill_name']

    def __str__(self):
        return f"{self.job.title} - {self.skill_name}"
