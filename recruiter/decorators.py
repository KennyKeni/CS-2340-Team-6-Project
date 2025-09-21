from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from .utils import is_recruiter


def recruiter_required(view_func):
    """Allow access only to authenticated users tagged as recruiters."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to continue.")
            return redirect(getattr(settings, "LOGIN_URL", "/admin/login/"))
        if not is_recruiter(request.user):
            messages.error(request, "You must be a recruiter to access this page.")
            return redirect("/")
        return view_func(request, *args, **kwargs)
    return _wrapped

