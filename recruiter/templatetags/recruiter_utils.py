from django import template
from recruiter.utils import is_recruiter as check_is_recruiter

register = template.Library()

@register.filter
def is_recruiter(user):
    """Template filter to check if user is a recruiter"""
    return check_is_recruiter(user)

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup a dictionary value by key"""
    return dictionary.get(key, [])