def get_user_role(user) -> str | None:
    """
    Returns a simple role string if discoverable.
    We assume your DB has a tag per user (e.g., account.profile.role or a Group).
    This is defensive: it won't crash if the related model doesn't exist yet.
    """
    if not user or not user.is_authenticated:
        return None

    # Try a custom Account model relationship, if present
    try:
        role = getattr(getattr(user, "account", None), "role", None)
        if role:
            return str(role).lower()
    except Exception:
        pass

    # Fallback: Django Group named "recruiter"
    try:
        if user.groups.filter(name__iexact="recruiter").exists():
            return "recruiter"
    except Exception:
        pass

    return None


def is_recruiter(user) -> bool:
    return get_user_role(user) == "recruiter"
