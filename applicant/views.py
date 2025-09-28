from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model

from .decorators import applicant_required
from .models import Applicant, Application, Education, Link, Skill, WorkExperience
from applicant.utils import is_applicant

User = get_user_model()


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
                "user_type": 'applicant' if is_applicant(account) else 'recruiter' if hasattr(account, 'recruiter') else '',
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


@applicant_required
def my_applications(request):
    apps = (
        Application.objects
        .select_related("job")
        .filter(applicant=request.user)
        .order_by("-updated_at")
    )
    steps = [
        ("applied", "Applied"),
        ("review", "Review"),
        ("interview", "Interview"),
        ("offer", "Offer"),
        ("closed", "Closed"),
    ]
    context = {
        "template_data": {"title": "My Applications · DevJobs"},
        "applications": apps,
        "steps": steps,
    }
    return render(request, "applicant/myapplications.html", context)


@login_required
def create_profile(request):
    """Create or edit applicant profile"""
    user = request.user

    # Check if user is an applicant
    if not is_applicant(user):
        return redirect('home:index')

    # Get or create applicant profile
    applicant, created = Applicant.objects.get_or_create(account=user)

    if request.method == 'GET':
        template_data = {
            "title": "Create Your Profile · DevJobs",
            "applicant": applicant,
            "work_experiences": applicant.work_experiences.all(),
            "education": applicant.education.all(),
            "skills": applicant.skills.all(),
            "links": applicant.links.all(),
        }
        return render(request, 'applicant/create_profile.html', {'template_data': template_data})

    if request.method == 'POST':
        try:
            # Check if this is a JSON request (AJAX)
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)

                # Handle work experiences
                if 'work_experiences' in data:
                    applicant.work_experiences.all().delete()
                    for work_exp in data['work_experiences']:
                        if work_exp.get('company') and work_exp.get('position'):
                            WorkExperience.objects.create(
                                applicant=applicant,
                                company=work_exp.get('company', ''),
                                position=work_exp.get('position', ''),
                                start_date=datetime.strptime(work_exp.get('start_date', ''), '%Y-%m-%d').date() if work_exp.get('start_date') else None,
                                end_date=datetime.strptime(work_exp.get('end_date', ''), '%Y-%m-%d').date() if work_exp.get('end_date') else None,
                                is_current=work_exp.get('is_current', False),
                                description=work_exp.get('description', ''),
                                location=work_exp.get('location', ''),
                            )
                    return JsonResponse({'status': 'success'})

                # Handle education
                if 'education' in data:
                    applicant.education.all().delete()
                    for edu in data['education']:
                        if edu.get('institution') and edu.get('degree'):
                            Education.objects.create(
                                applicant=applicant,
                                institution=edu.get('institution', ''),
                                degree=edu.get('degree', ''),
                                field_of_study=edu.get('field_of_study', ''),
                                start_date=datetime.strptime(edu.get('start_date', ''), '%Y-%m-%d').date() if edu.get('start_date') else None,
                                end_date=datetime.strptime(edu.get('end_date', ''), '%Y-%m-%d').date() if edu.get('end_date') else None,
                                is_current=edu.get('is_current', False),
                                gpa=float(edu.get('gpa', 0)) if edu.get('gpa') else None,
                            )
                    return JsonResponse({'status': 'success'})

                # Handle skills
                if 'skills' in data:
                    applicant.skills.all().delete()
                    for skill in data['skills']:
                        if skill.get('skill_name'):
                            Skill.objects.create(
                                applicant=applicant,
                                skill_name=skill.get('skill_name', ''),
                                proficiency_level=skill.get('proficiency_level', 'intermediate'),
                                years_of_experience=int(skill.get('years_of_experience', 0)) if skill.get('years_of_experience') else None,
                            )
                    return JsonResponse({'status': 'success'})

                # Handle links
                if 'links' in data:
                    applicant.links.all().delete()
                    for link in data['links']:
                        if link.get('url'):
                            Link.objects.create(
                                applicant=applicant,
                                url=link.get('url', ''),
                                platform=link.get('platform', 'other'),
                                description=link.get('description', ''),
                            )
                    return JsonResponse({'status': 'success'})

                return JsonResponse({'status': 'error', 'message': 'No valid data provided'})

            # Handle regular form submission
            data = request.POST

            # Update basic profile info
            applicant.headline = data.get('headline', '')
            applicant.resume = data.get('resume', '')
            applicant.save()

            # Handle work experiences
            if 'work_experiences' in data:
                applicant.work_experiences.all().delete()
                work_experiences = data.getlist('work_experiences')
                for i, work_exp in enumerate(work_experiences):
                    if work_exp:  # Skip empty entries
                        WorkExperience.objects.create(
                            applicant=applicant,
                            company=data.get(f'work_company_{i}', ''),
                            position=data.get(f'work_position_{i}', ''),
                            start_date=datetime.strptime(data.get(f'work_start_{i}', ''), '%Y-%m-%d').date() if data.get(f'work_start_{i}') else None,
                            end_date=datetime.strptime(data.get(f'work_end_{i}', ''), '%Y-%m-%d').date() if data.get(f'work_end_{i}') else None,
                            is_current=data.get(f'work_current_{i}') == 'on',
                            description=data.get(f'work_description_{i}', ''),
                            location=data.get(f'work_location_{i}', ''),
                        )

            # Handle education
            if 'education' in data:
                applicant.education.all().delete()
                education = data.getlist('education')
                for i, edu in enumerate(education):
                    if edu:  # Skip empty entries
                        Education.objects.create(
                            applicant=applicant,
                            institution=data.get(f'edu_institution_{i}', ''),
                            degree=data.get(f'edu_degree_{i}', ''),
                            field_of_study=data.get(f'edu_field_{i}', ''),
                            start_date=datetime.strptime(data.get(f'edu_start_{i}', ''), '%Y-%m-%d').date() if data.get(f'edu_start_{i}') else None,
                            end_date=datetime.strptime(data.get(f'edu_end_{i}', ''), '%Y-%m-%d').date() if data.get(f'edu_end_{i}') else None,
                            is_current=data.get(f'edu_current_{i}') == 'on',
                            gpa=float(data.get(f'edu_gpa_{i}', 0)) if data.get(f'edu_gpa_{i}') else None,
                        )

            # Handle skills
            if 'skills' in data:
                applicant.skills.all().delete()
                skills = data.getlist('skills')
                for i, skill in enumerate(skills):
                    if skill:  # Skip empty entries
                        Skill.objects.create(
                            applicant=applicant,
                            skill_name=data.get(f'skill_name_{i}', ''),
                            proficiency_level=data.get(f'skill_level_{i}', 'intermediate'),
                            years_of_experience=int(data.get(f'skill_years_{i}', 0)) if data.get(f'skill_years_{i}') else None,
                        )

            # Handle links
            if 'links' in data:
                applicant.links.all().delete()
                links = data.getlist('links')
                for i, link in enumerate(links):
                    if link:  # Skip empty entries
                        Link.objects.create(
                            applicant=applicant,
                            url=data.get(f'link_url_{i}', ''),
                            platform=data.get(f'link_platform_{i}', 'other'),
                            description=data.get(f'link_description_{i}', ''),
                        )

            return redirect('applicant:view_profile')

        except Exception as e:
            # Handle errors
            template_data = {
                "title": "Create Your Profile · DevJobs",
                "applicant": applicant,
                "error": str(e),
            }
            return render(request, 'applicant/create_profile.html', {'template_data': template_data})


@login_required
def view_profile(request):
    """View applicant profile"""
    user = request.user

    # Check if user is an applicant
    if not is_applicant(user):
        return redirect('home:index')

    try:
        applicant = user.applicant
    except Applicant.DoesNotExist:
        return redirect('applicant:create_profile')

    template_data = {
        "title": "My Profile · DevJobs",
        "applicant": applicant,
        "work_experiences": applicant.work_experiences.all(),
        "education": applicant.education.all(),
        "skills": applicant.skills.all(),
        "links": applicant.links.all(),
    }
    return render(request, 'applicant/view_profile.html', {'template_data': template_data})
