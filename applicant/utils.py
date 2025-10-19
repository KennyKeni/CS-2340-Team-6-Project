def get_user_role(user) -> str | None:
    if not user or not user.is_authenticated:
        return None

    if hasattr(user, 'applicant'):
        return 'applicant'
    elif hasattr(user, 'recruiter'):
        return 'recruiter'

    return None


def is_applicant(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    return hasattr(user, 'applicant')


def get_job_recommendations_for_user(user, min_matching_skills=1, limit=10):
    """
    Get job recommendations for a user based on their skills.
    
    Args:
        user: The user object
        min_matching_skills (int): Minimum number of matching skills required (configurable)
        limit (int): Maximum number of recommendations to return
    
    Returns:
        QuerySet: Recommended JobPosting objects
    """
    if not is_applicant(user):
        from job.models import JobPosting
        return JobPosting.objects.none()
    
    applicant = user.applicant
    recommendations = applicant.get_job_recommendations(min_matching_skills=min_matching_skills)
    
    return recommendations[:limit] if limit else recommendations
