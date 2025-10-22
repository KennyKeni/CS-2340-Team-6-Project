from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Q
from django.utils import timezone

from .models import Notification, SavedSearch
from applicant.models import Applicant, Skill


@receiver(post_save, sender=Applicant)
def notify_saved_searches_on_candidate_update(sender, instance, created, **kwargs):
    """
    When a new candidate is created or updated, check all saved searches
    and notify recruiters if the candidate matches their criteria.
    """
    if not created:  # Only notify for new candidates or significant updates
        return
    
    # Get all active saved searches
    saved_searches = SavedSearch.objects.filter(is_active=True)
    
    for search in saved_searches:
        # Check if candidate matches search criteria
        if matches_saved_search(instance, search):
            # Create notification for the recruiter
            candidate_name = instance.account.get_full_name() or instance.account.username
            Notification.objects.create(
                recipient=search.recruiter,
                notification_type='saved_search_match',
                title=f'New candidate "{candidate_name}" matches "{search.name}"',
                message=f'Candidate {candidate_name} has been found that matches your saved search criteria for "{search.name}".',
                related_job=None  # Could be enhanced to relate to specific jobs
            )
            
            # Update last notification sent time
            search.last_notification_sent = timezone.now()
            search.save(update_fields=['last_notification_sent'])


@receiver(post_save, sender=Skill)
def notify_saved_searches_on_skill_update(sender, instance, created, **kwargs):
    """
    When a new skill is added to a candidate, check if it matches saved searches.
    """
    if not created:
        return
        
    candidate = instance.applicant
    
    # Get all active saved searches that include this skill
    # Using Python-side filtering for SQLite compatibility
    all_searches = SavedSearch.objects.filter(is_active=True)
    saved_searches = [
        search for search in all_searches
        if instance.skill_name in search.skills
    ]
    
    for search in saved_searches:
        # Check if candidate now matches search criteria
        if matches_saved_search(candidate, search):
            # Create notification for the recruiter
            candidate_name = candidate.account.get_full_name() or candidate.account.username
            Notification.objects.create(
                recipient=search.recruiter,
                notification_type='saved_search_match',
                title=f'Candidate "{candidate_name}" updated - matches "{search.name}"',
                message=f'Candidate {candidate_name} has updated their profile and now matches your saved search criteria for "{search.name}".',
                related_job=None
            )
            
            # Update last notification sent time
            search.last_notification_sent = timezone.now()
            search.save(update_fields=['last_notification_sent'])


def matches_saved_search(candidate, search):
    """
    Check if a candidate matches the criteria in a saved search.
    """
    # Check skills match
    if search.skills:
        candidate_skills = candidate.skills.values_list('skill_name', flat=True)
        if not any(skill in candidate_skills for skill in search.skills):
            return False
    
    # Check location match
    if search.location:
        location_match = False
        if search.location.lower() in candidate.account.city.lower():
            location_match = True
        elif search.location.lower() in candidate.account.state.lower():
            location_match = True
        elif search.location.lower() in candidate.account.country.lower():
            location_match = True
        
        if not location_match:
            return False
    
    # Check experience match (if specified)
    if search.min_experience or search.max_experience:
        # Calculate total experience from work experiences
        total_experience = 0
        for exp in candidate.work_experiences.all():
            if exp.end_date:
                duration = exp.end_date - exp.start_date
                total_experience += duration.days / 365.25
            elif exp.is_current:
                duration = timezone.now().date() - exp.start_date
                total_experience += duration.days / 365.25
        
        if search.min_experience and total_experience < search.min_experience:
            return False
        
        if search.max_experience and total_experience > search.max_experience:
            return False
    
    # Check education level match
    if search.education_level:
        education_match = False
        for edu in candidate.education.all():
            if search.education_level.lower() in edu.degree.lower():
                education_match = True
                break
        
        if not education_match:
            return False
    
    # If we get here, the candidate matches the search criteria
    return True
