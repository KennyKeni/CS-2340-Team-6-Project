from django import template
from applicant.utils import is_applicant as check_is_applicant

register = template.Library()

@register.filter
def is_applicant(user):
    """Template filter to check if user is an applicant"""
    return check_is_applicant(user)


@register.filter
def has_skill(applicant_skills, skill_name):
    """Check if an applicant has a particular skill"""
    if not applicant_skills:
        return False
    return applicant_skills.filter(skill_name=skill_name).exists()


@register.filter
def get_skill_names(skills):
    """Get a list of skill names from a skills queryset"""
    return list(skills.values_list('skill_name', flat=True))


@register.filter
def get_privacy_setting(applicant, setting_name):
    """Safely get a privacy setting value with a default of True if privacy settings don't exist"""
    try:
        if hasattr(applicant, 'privacy_settings') and applicant.privacy_settings:
            return getattr(applicant.privacy_settings, setting_name, True)
    except:
        pass
    return True  # Default to showing information if no privacy settings exist