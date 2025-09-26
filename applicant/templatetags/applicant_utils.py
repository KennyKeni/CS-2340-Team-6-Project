from django import template
from applicant.utils import is_applicant as check_is_applicant

register = template.Library()

@register.filter
def is_applicant(user):
    """Template filter to check if user is an applicant"""
    return check_is_applicant(user)