from typing import cast
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
from account.forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProfileUpdateForm,
)
from account.models import Account, UserType
from applicant.models import Applicant, WorkExperience, Education, Skill, Link
from recruiter.models import Recruiter
from datetime import datetime


# Helper method for anyone that needs it
def show(request, id):
    movie = Account.objects.get(id=id)


@require_http_methods(["GET", "POST"])
@csrf_exempt
def account_signup(request):
    if request.method == "GET":
        # GET request - render the signup form, something like below
        # template_data = {}
        # template_data['title'] = 'Sign Up'
        # template_data['form'] = CustomUserCreationForm()
        # return render(request, 'accounts/signup.html', {'template_data': template_data})

        return redirect("/")  # Delete these once implemented

    if request.method == "POST":
        # POST request - process form submission
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        form = CustomUserCreationForm(data)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    if user.user_type == UserType.APPLICANT:
                        # Create applicant record
                        applicant = Applicant.objects.create(
                            account=user,
                            headline=form.cleaned_data.get("headline", ""),
                            resume=form.cleaned_data.get("resume", ""),
                        )

                        work_experiences = data.get("work_experiences", [])
                        for work_exp in work_experiences:
                            WorkExperience.objects.create(
                                applicant=applicant,
                                company=work_exp.get("company", ""),
                                position=work_exp.get("position", ""),
                                start_date=datetime.strptime(
                                    work_exp["start_date"], "%Y-%m-%d"
                                ).date(),
                                end_date=(
                                    datetime.strptime(
                                        work_exp["end_date"], "%Y-%m-%d"
                                    ).date()
                                    if work_exp.get("end_date")
                                    else None
                                ),
                                is_current=work_exp.get("is_current", False),
                                description=work_exp.get("description", ""),
                                location=work_exp.get("location", ""),
                            )

                        education_records = data.get("education", [])
                        for edu in education_records:
                            Education.objects.create(
                                applicant=applicant,
                                institution=edu.get("institution", ""),
                                degree=edu.get("degree", ""),
                                field_of_study=edu.get("field_of_study", ""),
                                start_date=datetime.strptime(
                                    edu["start_date"], "%Y-%m-%d"
                                ).date(),
                                end_date=(
                                    datetime.strptime(
                                        edu["end_date"], "%Y-%m-%d"
                                    ).date()
                                    if edu.get("end_date")
                                    else None
                                ),
                                is_current=edu.get("is_current", False),
                                gpa=edu.get("gpa"),
                            )

                        skills = data.get("skills", [])
                        for skill in skills:
                            Skill.objects.create(
                                applicant=applicant,
                                skill_name=skill.get("skill_name", ""),
                                proficiency_level=skill.get(
                                    "proficiency_level", "intermediate"
                                ),
                                years_of_experience=skill.get("years_of_experience"),
                            )

                        links = data.get("links", [])
                        for link in links:
                            Link.objects.create(
                                applicant=applicant,
                                url=link.get("url", ""),
                                platform=link.get("platform", "other"),
                                description=link.get("description", ""),
                            )
                    elif user.user_type == UserType.RECRUITER:
                        Recruiter.objects.create(
                            account=user,
                            company=form.cleaned_data.get("company", ""),
                            position=form.cleaned_data.get("position", ""),
                        )
                    login(request, user)
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Account created successfully",
                            "user_id": user.id,
                            "username": user.username,
                            "user_type": user.user_type,
                        },
                        status=201,
                    )
            except Exception as e:
                return JsonResponse(
                    {"success": False, "error": f"Error creating account: {str(e)}"},
                    status=500,
                )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    # Should never reach here
    return redirect("/")


@require_http_methods(["POST"])
@csrf_exempt
def account_login(request) -> HttpResponse:
    if request.method == "GET":
        # GET request - render the signup form, something like below
        # template_data = {}
        # template_data['title'] = 'Login'
        # template_data['form'] = CustomUserCreationForm()
        # return render(request, 'accounts/login.html', {'template_data': template_data})
        pass
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    form = CustomAuthenticationForm(data=data)
    if form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            account_user = cast(Account, user)
            login(request, account_user)
            return JsonResponse(
                {
                    "success": True,
                    "message": "Login successful",
                    "user_id": str(account_user.id),
                    "username": account_user.username,
                    "user_type": getattr(account_user, "user_type", ""),
                },
                status=200,
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Invalid credentials"}, status=401
            )
    else:
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


@login_required
def account_logout(request) -> HttpResponse:
    logout(request)
    return redirect("home.index")


@require_http_methods(["PATCH"])
@csrf_exempt
@login_required
def profile_update(request) -> JsonResponse:
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user = cast(Account, request.user)

    form = ProfileUpdateForm(data, instance=user)

    if form.is_valid():
        try:
            with transaction.atomic():
                updated_user = form.save()

                if updated_user.user_type == UserType.APPLICANT:
                    try:
                        applicant = updated_user.applicant
                        # Update applicant fields if provided
                        if "headline" in data:
                            applicant.headline = form.cleaned_data.get(
                                "headline", applicant.headline
                            )
                        if "resume" in data:
                            applicant.resume = form.cleaned_data.get(
                                "resume", applicant.resume
                            )
                        applicant.save()

                        if "work_experiences" in data:
                            applicant.work_experiences.all().delete()
                            for work_exp in data["work_experiences"]:
                                WorkExperience.objects.create(
                                    applicant=applicant,
                                    company=work_exp.get("company", ""),
                                    position=work_exp.get("position", ""),
                                    start_date=datetime.strptime(
                                        work_exp["start_date"], "%Y-%m-%d"
                                    ).date(),
                                    end_date=(
                                        datetime.strptime(
                                            work_exp["end_date"], "%Y-%m-%d"
                                        ).date()
                                        if work_exp.get("end_date")
                                        else None
                                    ),
                                    is_current=work_exp.get("is_current", False),
                                    description=work_exp.get("description", ""),
                                    location=work_exp.get("location", ""),
                                )

                        if "education" in data:
                            applicant.education.all().delete()
                            for edu in data["education"]:
                                Education.objects.create(
                                    applicant=applicant,
                                    institution=edu.get("institution", ""),
                                    degree=edu.get("degree", ""),
                                    field_of_study=edu.get("field_of_study", ""),
                                    start_date=datetime.strptime(
                                        edu["start_date"], "%Y-%m-%d"
                                    ).date(),
                                    end_date=(
                                        datetime.strptime(
                                            edu["end_date"], "%Y-%m-%d"
                                        ).date()
                                        if edu.get("end_date")
                                        else None
                                    ),
                                    is_current=edu.get("is_current", False),
                                    gpa=edu.get("gpa"),
                                )

                        if "skills" in data:
                            applicant.skills.all().delete()
                            for skill in data["skills"]:
                                Skill.objects.create(
                                    applicant=applicant,
                                    skill_name=skill.get("skill_name", ""),
                                    proficiency_level=skill.get(
                                        "proficiency_level", "intermediate"
                                    ),
                                    years_of_experience=skill.get(
                                        "years_of_experience"
                                    ),
                                )

                        if "links" in data:
                            applicant.links.all().delete()
                            for link in data["links"]:
                                Link.objects.create(
                                    applicant=applicant,
                                    url=link.get("url", ""),
                                    platform=link.get("platform", "other"),
                                    description=link.get("description", ""),
                                )

                    except Applicant.DoesNotExist:
                        return JsonResponse(
                            {"error": "Applicant profile not found"}, status=404
                        )

                elif updated_user.user_type == UserType.RECRUITER:
                    try:
                        recruiter = updated_user.recruiter
                        if "company" in data:
                            recruiter.company = form.cleaned_data.get(
                                "company", recruiter.company
                            )
                        if "position" in data:
                            recruiter.position = form.cleaned_data.get(
                                "position", recruiter.position
                            )
                        recruiter.save()
                    except Recruiter.DoesNotExist:
                        return JsonResponse(
                            {"error": "Recruiter profile not found"}, status=404
                        )

                return JsonResponse(
                    {
                        "success": True,
                        "message": "Profile updated successfully",
                        "user_id": str(updated_user.id),
                        "username": updated_user.username,
                        "user_type": updated_user.user_type,
                        "email": updated_user.email,
                    },
                    status=200,
                )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error updating profile: {str(e)}"},
                status=500,
            )
    else:
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
