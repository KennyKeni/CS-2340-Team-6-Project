from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.apps import apps
import json
from datetime import datetime
from typing import cast

from account.forms import CustomAuthenticationForm, CustomUserCreationForm, ProfileUpdateForm
from account.models import Account, UserType
from applicant.models import Applicant, Education, Link, Skill, WorkExperience
from recruiter.models import Recruiter
from django.contrib.auth.decorators import login_required


# Helper method for anyone that needs it
def show(request, id):
    movie = Account.objects.get(id=id)


def _wants_json(request) -> bool:
    ct = (request.content_type or "").lower()
    accept = (request.META.get("HTTP_ACCEPT") or "").lower()
    return "application/json" in ct or "application/json" in accept
APPLICANT_GROUP = "applicant"
RECRUITER_GROUP = "recruiter"

def _get_or_create_group_ci(name: str) -> Group:
    """
    Case-insensitive fetch or create for a Group to avoid duplicates like
    'Recruiter' vs 'recruiter'.
    """
    existing = Group.objects.filter(name__iexact=name).first()
    return existing or Group.objects.create(name=name)

def _set_group_membership(user: Account, user_type: str) -> None:
    """
    Ensure the user belongs to the group that matches their user_type and not
    to the other one.
    """
    applicant_group = _get_or_create_group_ci(APPLICANT_GROUP)
    recruiter_group = _get_or_create_group_ci(RECRUITER_GROUP)

    # Remove both first (idempotent), then add the correct one.
    user.groups.remove(applicant_group, recruiter_group)
    if user_type == UserType.APPLICANT:
        user.groups.add(applicant_group)
    elif user_type == UserType.RECRUITER:
        user.groups.add(recruiter_group)

@require_http_methods(["GET", "POST"])
@csrf_exempt  # keep if you still post JSON from a client; otherwise you can remove this
def account_signup(request):
    # ---------- GET: render page ----------
    if request.method == "GET":
        form = CustomUserCreationForm(initial={"user_type": UserType.APPLICANT})
        return render(request, "account/signup.html", {"form": form})

    # ---------- POST: JSON or HTML ----------
    if _wants_json(request):
        # JSON API (kept compatible with your existing code)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        form = CustomUserCreationForm(data)
        if not form.is_valid():
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

        try:
            with transaction.atomic():
                # Save account with all required fields
                user: Account = form.save(commit=False)
                # ensure user_type comes through; default to applicant
                user.user_type = form.cleaned_data.get("user_type") or UserType.APPLICANT
                user.email = form.cleaned_data.get("email", "")
                user.phone_number = form.cleaned_data.get("phone_number", "")
                user.street_address = form.cleaned_data.get("street_address", "")
                user.city = form.cleaned_data.get("city", "")
                user.state = form.cleaned_data.get("state", "")
                user.country = form.cleaned_data.get("country", "")
                user.zip_code = form.cleaned_data.get("zip_code", "")
                user.save()

                if user.user_type == UserType.APPLICANT:
                    applicant = Applicant.objects.create(
                        account=user,
                        headline=form.cleaned_data.get("headline", ""),
                        resume=data.get("resume", ""),
                    )

                    for work_exp in data.get("work_experiences", []):
                        WorkExperience.objects.create(
                            applicant=applicant,
                            company=work_exp.get("company", ""),
                            position=work_exp.get("position", ""),
                            start_date=datetime.strptime(work_exp["start_date"], "%Y-%m-%d").date(),
                            end_date=(datetime.strptime(work_exp["end_date"], "%Y-%m-%d").date()
                                      if work_exp.get("end_date") else None),
                            is_current=work_exp.get("is_current", False),
                            description=work_exp.get("description", ""),
                            location=work_exp.get("location", ""),
                        )

                    for edu in data.get("education", []):
                        Education.objects.create(
                            applicant=applicant,
                            institution=edu.get("institution", ""),
                            degree=edu.get("degree", ""),
                            field_of_study=edu.get("field_of_study", ""),
                            start_date=datetime.strptime(edu["start_date"], "%Y-%m-%d").date(),
                            end_date=(datetime.strptime(edu["end_date"], "%Y-%m-%d").date()
                                      if edu.get("end_date") else None),
                            is_current=edu.get("is_current", False),
                            gpa=edu.get("gpa"),
                        )

                    for skill in data.get("skills", []):
                        Skill.objects.create(
                            applicant=applicant,
                            skill_name=skill.get("skill_name", ""),
                            proficiency_level=skill.get("proficiency_level", "intermediate"),
                            years_of_experience=skill.get("years_of_experience"),
                        )

                    for link in data.get("links", []):
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
                _set_group_membership(user, user.user_type)
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
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    else:
        # HTML form post
        form = CustomUserCreationForm(request.POST)
        if not form.is_valid():
            return render(request, "account/signup.html", {"form": form}, status=400)

        # Only allow APPLICANT for now (recruiter radio is disabled in UI)
        requested_type = form.cleaned_data.get("user_type") or UserType.APPLICANT
        if requested_type != UserType.APPLICANT:
            form.add_error(None, "Recruiter sign-up is coming soon. Please choose Applicant.")
            return render(request, "account/signup.html", {"form": form}, status=400)

        with transaction.atomic():
            user: Account = form.save(commit=False)
            user.user_type = UserType.APPLICANT
            user.email = form.cleaned_data.get("email", "")
            user.phone_number = form.cleaned_data.get("phone_number", "")
            user.street_address = form.cleaned_data["street_address"]
            user.city = form.cleaned_data["city"]
            user.state = form.cleaned_data["state"]
            user.country = form.cleaned_data["country"]
            user.zip_code = form.cleaned_data["zip_code"]
            user.save()

            Applicant.objects.create(
                account=user,
                headline=form.cleaned_data.get("headline", ""),
                resume="",
            )
        _set_group_membership(user, UserType.APPLICANT)
        login(request, user)
        return redirect("job:search_jobs")


@require_http_methods(["GET", "POST"])
@csrf_exempt  # keep if you still post JSON; otherwise remove
def account_login(request) -> HttpResponse:
    # ---------- GET: render page ----------
    if request.method == "GET":
        form = CustomAuthenticationForm(request)
        return render(request, "account/login.html", {"form": form})

    # ---------- POST: JSON or HTML ----------
    if _wants_json(request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        form = CustomAuthenticationForm(data=data, request=request)
        if not form.is_valid():
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

        user = form.get_user()
        if user is None:
            return JsonResponse({"success": False, "error": "Invalid credentials"}, status=401)

        login(request, user)
        return JsonResponse(
            {
                "success": True,
                "message": "Login successful",
                "user_id": str(user.id),
                "username": user.username,
                "user_type": getattr(user, "user_type", ""),
            },
            status=200,
        )
    else:
        # HTML form post
        form = CustomAuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            return render(request, "account/login.html", {"form": form}, status=400)

        user = form.get_user()
        login(request, user)
        next_url = request.GET.get("next") or "job:search_jobs"
        return redirect(next_url)


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
                _set_group_membership(updated_user, updated_user.user_type)

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
