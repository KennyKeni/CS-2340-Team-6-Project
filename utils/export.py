import csv
from collections.abc import Iterable
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone

UTF8_BOM = "\ufeff"
CSV_CONTENT_TYPE = "text/csv; charset=utf-8-sig"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
LIST_DELIMITER = "; "
ACTIVE_APPLICATION_STATUSES = {
    "pending",
    "reviewed",
    "shortlisted",
    "applied",
    "review",
    "interview",
    "offer",
}


def _timestamped_filename(prefix: str) -> str:
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.csv"


def _create_csv_response(filename: str) -> HttpResponse:
    response = HttpResponse(content_type=CSV_CONTENT_TYPE)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(UTF8_BOM)
    return response


def _format_datetime(value) -> str:
    if not value:
        return ""
    try:
        value = timezone.localtime(value)
    except (ValueError, TypeError, AttributeError):
        pass
    return value.strftime(DATETIME_FORMAT) if hasattr(value, "strftime") else _clean_text(value)


def _clean_text(value) -> str:
    if value is None:
        return ""
    text = str(value)
    return " ".join(text.replace("\r", " ").replace("\n", " ").split())


def _boolean_display(value) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return ""


def _list_to_string(values: Iterable) -> str:
    cleaned = [_clean_text(val) for val in values if val not in (None, "")]
    return LIST_DELIMITER.join(filter(None, cleaned))


def _truncate(value: str, length: int = 200) -> str:
    text = _clean_text(value)
    if not text or len(text) <= length:
        return text
    return text[: length - 3] + "..."


def _safe_related_object(obj, attr: str):
    try:
        return getattr(obj, attr)
    except (AttributeError, ObjectDoesNotExist):
        return None


def _related_items(obj, attr: str) -> list:
    if obj is None:
        return []
    manager = getattr(obj, attr, None)
    if manager is None:
        return []
    all_attr = getattr(manager, "all", None)
    if callable(all_attr):
        return list(all_attr())
    try:
        return list(manager)
    except TypeError:
        return []


def _skills_by_importance(job) -> dict:
    groups = {"required": [], "preferred": [], "nice_to_have": []}
    for skill in _related_items(job, "required_skills"):
        importance = getattr(skill, "importance_level", "required") or "required"
        bucket = groups.get(importance, groups["required"])
        bucket.append(_clean_text(getattr(skill, "skill_name", "")))
    for importance in groups:
        groups[importance] = [name for name in groups[importance] if name]
    return groups


def _job_application_sets(job) -> list:
    applications = []
    applications.extend(_related_items(job, "job_applications"))
    applications.extend(_related_items(job, "applications"))
    return applications


def _count_active_applications(job) -> tuple[int, int]:
    total = 0
    active = 0
    for application in _job_application_sets(job):
        total += 1
        status = getattr(application, "status", "") or ""
        normalized = status.lower()
        if normalized in ACTIVE_APPLICATION_STATUSES:
            active += 1
    return total, active


def _owner_username(job) -> str:
    owner = getattr(job, "owner", None)
    return _clean_text(getattr(owner, "username", "")) if owner else ""


def _owner_email(job) -> str:
    owner = getattr(job, "owner", None)
    return _clean_text(getattr(owner, "email", "")) if owner else ""


def _job_location_full(job) -> str:
    if not job:
        return ""
    return _list_to_string(
        [
            getattr(job, "street_address", ""),
            getattr(job, "city", ""),
            getattr(job, "state", ""),
            getattr(job, "zip_code", ""),
            getattr(job, "country", ""),
        ]
    )


def export_job_postings_csv(queryset):
    """Export JobPosting rows with related information flattened."""
    queryset = queryset.select_related("owner").prefetch_related(
        "required_skills",
        "job_applications",
        "applications",
    )

    filename = _timestamped_filename("job_postings_export")
    response = _create_csv_response(filename)
    fieldnames = [
        "id",
        "title",
        "company",
        "location",
        "city",
        "state",
        "country",
        "job_type",
        "salary_min",
        "salary_max",
        "salary_currency",
        "visa_sponsorship",
        "is_active",
        "created_at",
        "updated_at",
        "application_deadline",
        "owner_username",
        "owner_email",
        "required_skills",
        "preferred_skills",
        "nice_to_have_skills",
        "total_applications",
        "active_applications",
    ]

    writer = csv.DictWriter(response, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    for job in queryset:
        skills = _skills_by_importance(job)
        total_apps, active_apps = _count_active_applications(job)
        location_full = _job_location_full(job)

        row = {
            "id": getattr(job, "id", ""),
            "title": _clean_text(getattr(job, "title", "")),
            "company": _clean_text(getattr(job, "company", "")),
            "location": location_full or _clean_text(getattr(job, "location", "")),
            "city": _clean_text(getattr(job, "city", "")),
            "state": _clean_text(getattr(job, "state", "")),
            "country": _clean_text(getattr(job, "country", "")),
            "job_type": _clean_text(getattr(job, "job_type", "")),
            "salary_min": _clean_text(getattr(job, "salary_min", "")),
            "salary_max": _clean_text(getattr(job, "salary_max", "")),
            "salary_currency": _clean_text(getattr(job, "salary_currency", "")),
            "visa_sponsorship": _boolean_display(getattr(job, "visa_sponsorship", None)),
            "is_active": _boolean_display(getattr(job, "is_active", None)),
            "created_at": _format_datetime(getattr(job, "created_at", None)),
            "updated_at": _format_datetime(getattr(job, "updated_at", None)),
            "application_deadline": _format_datetime(getattr(job, "application_deadline", None)),
            "owner_username": _owner_username(job),
            "owner_email": _owner_email(job),
            "required_skills": _list_to_string(skills["required"]),
            "preferred_skills": _list_to_string(skills["preferred"]),
            "nice_to_have_skills": _list_to_string(skills["nice_to_have"]),
            "total_applications": total_apps,
            "active_applications": active_apps,
        }
        writer.writerow(row)

    return response


def _applicant_profile(user):
    return _safe_related_object(user, "applicant") if user else None


def _applicant_skills(profile) -> list[str]:
    return [
        _clean_text(getattr(skill, "skill_name", ""))
        for skill in _related_items(profile, "skills")
        if getattr(skill, "skill_name", "")
    ]


def _applicant_resume(profile) -> str:
    return _clean_text(getattr(profile, "resume", "")) if profile else ""


def _applicant_headline(profile) -> str:
    return _clean_text(getattr(profile, "headline", "")) if profile else ""


def _applicant_location(user, attr: str) -> str:
    return _clean_text(getattr(user, attr, "")) if user else ""


def _user_display_name(user) -> str:
    if not user:
        return ""
    full_name_callable = getattr(user, "get_full_name", None)
    if callable(full_name_callable):
        name = full_name_callable()
        if name:
            return name
    return getattr(user, "username", "") or getattr(user, "email", "")


def _application_cover_letter(application) -> str:
    if hasattr(application, "personalized_note"):
        return _clean_text(getattr(application, "personalized_note", ""))
    return _clean_text(getattr(application, "note", ""))


def export_applications_csv(queryset):
    """Export Application/JobApplication records with applicant/job details."""
    queryset = queryset.select_related(
        "job",
        "applicant",
        "applicant__applicant",
    ).prefetch_related(
        "job__required_skills",
        "applicant__applicant__skills",
    )

    filename = _timestamped_filename("applications_export")
    response = _create_csv_response(filename)
    fieldnames = [
        "application_id",
        "status",
        "applied_at",
        "updated_at",
        "job_title",
        "company",
        "job_location",
        "applicant_name",
        "applicant_email",
        "applicant_phone",
        "applicant_headline",
        "applicant_city",
        "applicant_state",
        "applicant_skills",
        "cover_letter_preview",
        "resume_url",
    ]

    writer = csv.DictWriter(response, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    for application in queryset:
        job = getattr(application, "job", None)
        applicant_user = getattr(application, "applicant", None)
        applicant_profile = _applicant_profile(applicant_user)

        status_display = getattr(application, "get_status_display", None)
        status_value = status_display() if callable(status_display) else getattr(application, "status", "")

        applied_timestamp = getattr(application, "applied_at", None) or getattr(application, "created_at", None)

        cover_letter = _application_cover_letter(application)

        row = {
            "application_id": getattr(application, "id", ""),
            "status": _clean_text(status_value),
            "applied_at": _format_datetime(applied_timestamp),
            "updated_at": _format_datetime(getattr(application, "updated_at", None)),
            "job_title": _clean_text(getattr(job, "title", "")),
            "company": _clean_text(getattr(job, "company", "")),
            "job_location": _job_location_full(job) or _clean_text(getattr(job, "location", "")),
            "applicant_name": _clean_text(_user_display_name(applicant_user)),
            "applicant_email": _clean_text(getattr(applicant_user, "email", "")),
            "applicant_phone": _clean_text(getattr(applicant_user, "phone_number", "")),
            "applicant_headline": _applicant_headline(applicant_profile),
            "applicant_city": _applicant_location(applicant_user, "city"),
            "applicant_state": _applicant_location(applicant_user, "state"),
            "applicant_skills": _list_to_string(_applicant_skills(applicant_profile)),
            "cover_letter_preview": _truncate(cover_letter, 200),
            "resume_url": _applicant_resume(applicant_profile),
        }
        writer.writerow(row)

    return response


def _determine_role(user) -> str:
    applicant_profile = _safe_related_object(user, "applicant")
    recruiter_profile = _safe_related_object(user, "recruiter")
    has_applicant = applicant_profile is not None
    has_recruiter = recruiter_profile is not None
    if has_applicant and has_recruiter:
        return "Both"
    if has_applicant:
        return "Applicant"
    if has_recruiter:
        return "Recruiter"
    return "None"


def _profile_visible(profile) -> str:
    privacy = getattr(profile, "privacy_settings", None)
    visible = getattr(privacy, "visible_to_recruiters", None)
    return _boolean_display(visible)


def _applicant_years_of_experience(profile) -> str:
    total = 0
    found = False
    for skill in _related_items(profile, "skills"):
        years = getattr(skill, "years_of_experience", None)
        if years is not None:
            found = True
            total += years
    return str(total) if found else ""


def _applicant_education_level(profile) -> str:
    education_entries = _related_items(profile, "education")
    if not education_entries:
        return ""
    top_entry = education_entries[0]
    return _clean_text(getattr(top_entry, "degree", ""))


def _recruiter_company(user) -> str:
    recruiter = _safe_related_object(user, "recruiter")
    return _clean_text(getattr(recruiter, "company", "")) if recruiter else ""


def export_users_csv(queryset, role_filter: Optional[str] = None):
    """Export users with optional role scoping."""
    queryset = queryset.annotate(
        total_jobs_posted=Count("job_postings", distinct=True),
        active_jobs=Count("job_postings", filter=Q(job_postings__is_active=True), distinct=True),
        total_emails=Count("sent_emails", distinct=True),
        total_messages=Count("sent_messages", distinct=True),
    ).select_related(
        "applicant",
        "recruiter",
    ).prefetch_related(
        "applicant__skills",
        "applicant__education",
        "applicant__privacy_settings",
    )

    role_scope = role_filter or "all"
    filename = _timestamped_filename(f"users_export_{role_scope}")
    response = _create_csv_response(filename)

    base_fields = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "date_joined",
        "last_login",
        "role",
        "city",
        "state",
        "country",
    ]
    applicant_fields = [
        "headline",
        "bio",
        "skills",
        "years_of_experience",
        "education_level",
        "profile_visible_to_recruiters",
    ]
    recruiter_fields = [
        "recruiter_company",
        "total_jobs_posted",
        "active_jobs",
        "total_emails_sent",
        "total_messages_sent",
    ]

    fieldnames = base_fields[:]
    if role_scope in {"applicant", "all"}:
        fieldnames += applicant_fields
    if role_scope in {"recruiter", "all"}:
        fieldnames += recruiter_fields

    writer = csv.DictWriter(response, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    for user in queryset:
        applicant_profile = _applicant_profile(user)
        base_row = {
            "id": getattr(user, "id", ""),
            "username": _clean_text(getattr(user, "username", "")),
            "email": _clean_text(getattr(user, "email", "")),
            "first_name": _clean_text(getattr(user, "first_name", "")),
            "last_name": _clean_text(getattr(user, "last_name", "")),
            "is_active": _boolean_display(getattr(user, "is_active", None)),
            "date_joined": _format_datetime(getattr(user, "date_joined", None)),
            "last_login": _format_datetime(getattr(user, "last_login", None)),
            "role": _determine_role(user),
            "city": _clean_text(getattr(user, "city", "")),
            "state": _clean_text(getattr(user, "state", "")),
            "country": _clean_text(getattr(user, "country", "")),
        }

        if role_scope in {"applicant", "all"}:
            bio_value = _clean_text(getattr(user, "bio", "")) or _applicant_headline(applicant_profile)
            applicant_row = {
                "headline": _applicant_headline(applicant_profile),
                "bio": bio_value,
                "skills": _list_to_string(_applicant_skills(applicant_profile)),
                "years_of_experience": _applicant_years_of_experience(applicant_profile),
                "education_level": _applicant_education_level(applicant_profile),
                "profile_visible_to_recruiters": _profile_visible(applicant_profile),
            }
            base_row.update(applicant_row)

        if role_scope in {"recruiter", "all"}:
            recruiter_row = {
                "recruiter_company": _recruiter_company(user),
                "total_jobs_posted": getattr(user, "total_jobs_posted", 0),
                "active_jobs": getattr(user, "active_jobs", 0),
                "total_emails_sent": getattr(user, "total_emails", 0),
                "total_messages_sent": getattr(user, "total_messages", 0),
            }
            base_row.update(recruiter_row)

        writer.writerow(base_row)

    return response
