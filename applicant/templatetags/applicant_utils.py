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