def get_user_role(user) -> str | None:
    if not user or not user.is_authenticated:
        return None

    if hasattr(user, 'recruiter'):
        return 'recruiter'
    elif hasattr(user, 'applicant'):
        return 'applicant'

    return None


def is_recruiter(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    return hasattr(user, 'recruiter')
