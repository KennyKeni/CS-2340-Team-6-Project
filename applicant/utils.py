def get_user_role(user) -> str | None:
    """
    Return the user's role tag, if available.
    Tries a hypothetical Account model (user.account.role), else falls back to Group.
    """
    if not user or not user.is_authenticated:
        return None

    # Try a profile-like relation: user.account.role
    try:
        role = getattr(getattr(user, "account", None), "role", None)
        if role:
            return str(role).lower()
    except Exception:
        pass

    # Fallback to Groups
    try:
        if user.groups.filter(name__iexact="recruiter").exists():
            return "recruiter"
        if user.groups.filter(name__iexact="applicant").exists():
            return "applicant"
        if user.groups.filter(name__iexact="job_seeker").exists():
            return "job_seeker"
    except Exception:
        pass

    return None


def is_applicant(user) -> bool:
    """Allow if the user is authenticated and tagged as an applicant."""
    if not user or not user.is_authenticated:
        return False

    # If you later add a profile like user.account.role, this keeps working:
    role = getattr(getattr(user, "account", None), "role", None)
    if role and str(role).lower() in {"applicant", "job_seeker", "jobseeker"}:
        return True

    # Group-based check (works even if the user is ALSO a recruiter)
    return user.groups.filter(name__in=["applicant", "job_seeker", "jobseeker"]).exists()
