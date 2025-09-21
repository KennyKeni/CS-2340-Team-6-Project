from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from applicant.models import Applicant, WorkExperience, Education, Skill, Link
from datetime import datetime


@require_http_methods(["GET"])
def applicant_search(request):
    # Get all applicants with related data
    applicants = (
        Applicant.objects.select_related("account")
        .prefetch_related("work_experiences", "education", "skills", "links")
        .all()
    )

    # Apply filters
    headline = request.GET.get("headline")
    if headline:
        applicants = applicants.filter(headline__icontains=headline)

    # Education filters
    institution = request.GET.get("institution")
    if institution:
        applicants = applicants.filter(education__institution__icontains=institution)

    degree = request.GET.get("degree")
    if degree:
        applicants = applicants.filter(education__degree__icontains=degree)

    field_of_study = request.GET.get("field_of_study")
    if field_of_study:
        applicants = applicants.filter(
            education__field_of_study__icontains=field_of_study
        )

    gpa_min = request.GET.get("gpa_min")
    if gpa_min:
        try:
            applicants = applicants.filter(education__gpa__gte=float(gpa_min))
        except (ValueError, TypeError):
            pass

    gpa_max = request.GET.get("gpa_max")
    if gpa_max:
        try:
            applicants = applicants.filter(education__gpa__lte=float(gpa_max))
        except (ValueError, TypeError):
            pass

    graduation_year = request.GET.get("graduation_year")
    if graduation_year:
        try:
            year = datetime.strptime(graduation_year, "%Y").date()
            applicants = applicants.filter(education__end_date__year=year.year)
        except ValueError:
            pass

    # Work experience filters
    company = request.GET.get("company")
    if company:
        applicants = applicants.filter(work_experiences__company__icontains=company)

    position = request.GET.get("position")
    if position:
        applicants = applicants.filter(work_experiences__position__icontains=position)

    # Skills filters
    skill = request.GET.get("skill")
    if skill:
        applicants = applicants.filter(skills__skill_name__icontains=skill)

    skill_level = request.GET.get("skill_level")
    if skill_level:
        applicants = applicants.filter(skills__proficiency_level=skill_level)

    # Account-level filters
    city = request.GET.get("city")
    if city:
        applicants = applicants.filter(account__city__icontains=city)

    state = request.GET.get("state")
    if state:
        applicants = applicants.filter(account__state__icontains=state)

    country = request.GET.get("country")
    if country:
        applicants = applicants.filter(account__country__icontains=country)

    username = request.GET.get("username")
    if username:
        applicants = applicants.filter(account__username__icontains=username)

    # Pagination
    limit = request.GET.get("limit", 20)
    offset = request.GET.get("offset", 0)

    try:
        limit = int(limit)
        offset = int(offset)
    except (ValueError, TypeError):
        limit = 20
        offset = 0

    # Ensure reasonable limits
    limit = min(max(1, limit), 100)  # Between 1 and 100
    offset = max(0, offset)

    total_count = applicants.count()
    applicants = applicants[offset : offset + limit]

    # Serialize data
    results = []
    for applicant in applicants:
        account = applicant.account

        # Work experiences
        work_experiences = []
        for exp in applicant.work_experiences.all():
            work_experiences.append(
                {
                    "id": exp.id,
                    "company": exp.company,
                    "position": exp.position,
                    "start_date": exp.start_date.isoformat(),
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "is_current": exp.is_current,
                    "description": exp.description,
                    "location": exp.location,
                }
            )

        # Education
        education = []
        for edu in applicant.education.all():
            education.append(
                {
                    "id": edu.id,
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "start_date": edu.start_date.isoformat(),
                    "end_date": edu.end_date.isoformat() if edu.end_date else None,
                    "is_current": edu.is_current,
                    "gpa": float(edu.gpa) if edu.gpa else None,
                }
            )

        # Skills
        skills = []
        for skill in applicant.skills.all():
            skills.append(
                {
                    "id": skill.id,
                    "skill_name": skill.skill_name,
                    "proficiency_level": skill.proficiency_level,
                    "years_of_experience": skill.years_of_experience,
                }
            )

        # Links
        links = []
        for link in applicant.links.all():
            links.append(
                {
                    "id": link.id,
                    "url": link.url,
                    "platform": link.platform,
                    "description": link.description,
                }
            )

        results.append(
            {
                "id": applicant.account.id,
                "username": account.username,
                "email": account.email,
                "phone_number": account.phone_number,
                "profile_picture": account.profile_picture,
                "street_address": account.street_address,
                "city": account.city,
                "state": account.state,
                "country": account.country,
                "zip_code": account.zip_code,
                "headline": applicant.headline,
                "resume": applicant.resume,
                "user_type": account.user_type,
                "work_experiences": work_experiences,
                "education": education,
                "skills": skills,
                "links": links,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "data": results,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_next": offset + limit < total_count,
                "has_previous": offset > 0,
            },
        },
        status=200,
    )
