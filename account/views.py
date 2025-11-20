import json
from datetime import datetime
from typing import cast

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from account.forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
    ProfileUpdateForm,
)
from account.models import Account
from applicant.models import Applicant, Education, Link, Skill, WorkExperience
from applicant.utils import is_applicant
from recruiter.models import Recruiter
from recruiter.utils import is_recruiter
from job.utils import geocode_address


# Helper method for anyone that needs it
def show(request, id):
    """Debug helper to show an account by ID."""
    _ = Account.objects.get(id=id)


@require_http_methods(["GET", "POST"])
def account_signup(request):
    """Handle user sign-up and account creation."""
    if request.method == "GET":
        template_data = {"title": "Sign Up · DevJobs"}
        return render(request, "account/signup.html", {"template_data": template_data})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")  # Debug line
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        form = CustomUserCreationForm(data)
        print(f"Form errors: {form.errors}")  # Debug line
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)

                    # Geocode user's address to get latitude/longitude
                    if user.street_address and user.city and user.state:
                        latitude, longitude = geocode_address(
                            street_address=user.street_address,
                            city=user.city,
                            state=user.state,
                            zip_code=user.zip_code,
                            country=user.country
                        )
                        if latitude and longitude:
                            user.latitude = latitude
                            user.longitude = longitude

                    user.save()
                    user_type = data.get("user_type")

                    if user_type == "applicant":
                        Applicant.objects.create(
                            account=user,
                            headline=form.cleaned_data.get("headline", ""),
                        )
                    elif user_type == "recruiter":
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
                            "user_id": str(user.id),
                            "username": user.username,
                            "user_type": user_type,
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

    return redirect("/")


@require_http_methods(["GET", "POST"])
def account_login(request) -> HttpResponse:
    """Handle user login."""
    if request.method == "GET":
        template_data = {"title": "Login · DevJobs"}
        return render(request, "account/login.html", {"template_data": template_data})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        username = data.get("username")
        password = data.get("password")

        # Check if account exists and is banned before form validation
        if username:
            try:
                account = Account.objects.get(username=username)
                if not account.is_active:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": "Account Disabled: Your account has been deactivated by an administrator. Please contact support for assistance.",
                        },
                        status=403,
                    )
            except Account.DoesNotExist:
                pass

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
                        "user_type": (
                            "applicant"
                            if is_applicant(account_user)
                            else "recruiter"
                            if is_recruiter(account_user)
                            else ""
                        ),
                    },
                    status=200,
                )
            else:
                return JsonResponse(
                    {"success": False, "error": "Invalid credentials"}, status=401
                )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)


@require_http_methods(["GET", "POST"])
@login_required
def account_logout(request) -> HttpResponse:
    """Log the user out."""
    logout(request)
    return redirect("home:index")


@require_http_methods(["PATCH"])
@csrf_exempt
@login_required
def profile_update(request) -> JsonResponse:
    """Handle user profile updates via JSON PATCH requests."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user = cast(Account, request.user)
    form = ProfileUpdateForm(data, instance=user)

    if not form.is_valid():
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    try:
        with transaction.atomic():
            updated_user = form.save()

            # ✅ NEW: Commute preferences (persist to database)
            if "preferred_commute_radius" in data:
                updated_user.preferred_commute_radius = float(
                    data["preferred_commute_radius"]
                )
            if "preferred_commute_mode" in data:
                updated_user.preferred_commute_mode = data["preferred_commute_mode"]
            if "preferred_commute_time" in data:
                updated_user.preferred_commute_time = int(
                    data["preferred_commute_time"]
                )
            updated_user.save()

            # Applicant-specific updates
            if is_applicant(updated_user):
                try:
                    applicant = updated_user.applicant

                    if "headline" in data:
                        applicant.headline = form.cleaned_data.get(
                            "headline", applicant.headline
                        )
                    if "resume" in data:
                        applicant.resume = form.cleaned_data.get(
                            "resume", applicant.resume
                        )
                    applicant.save()

                    # Recreate related objects if included
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
                                years_of_experience=skill.get("years_of_experience"),
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

            # Recruiter-specific updates
            elif is_recruiter(updated_user):
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
                    "email": updated_user.email,
                    "preferred_commute_radius": updated_user.preferred_commute_radius,
                    "preferred_commute_mode": updated_user.preferred_commute_mode,
                },
                status=200,
            )

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Error updating profile: {str(e)}"},
            status=500,
        )
