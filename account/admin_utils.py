from django.db import transaction

from applicant.models import Applicant
from recruiter.models import Recruiter


def change_user_role(user, new_role):
    if new_role not in ['applicant', 'recruiter']:
        return False, f"Invalid role: {new_role}. Must be 'applicant' or 'recruiter'."

    try:
        with transaction.atomic():
            if hasattr(user, 'applicant'):
                user.applicant.delete()
            if hasattr(user, 'recruiter'):
                user.recruiter.delete()

            if new_role == 'applicant':
                Applicant.objects.create(account=user, headline="")

            elif new_role == 'recruiter':
                Recruiter.objects.create(account=user, company="", position="")

            return True, f"Successfully changed {user.username}'s role to {new_role}"

    except Exception as e:
        return False, f"Error changing role: {str(e)}"


def get_user_role(user):
    if hasattr(user, 'applicant'):
        return 'applicant'
    elif hasattr(user, 'recruiter'):
        return 'recruiter'
    else:
        return 'no_role'


def ban_users(users):
    count = 0
    for user in users:
        if user.is_active:
            user.is_active = False
            user.save()
            count += 1
    return count


def unban_users(users):
    count = 0
    for user in users:
        if not user.is_active:
            user.is_active = True
            user.save()
            count += 1
    return count
