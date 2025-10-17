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
