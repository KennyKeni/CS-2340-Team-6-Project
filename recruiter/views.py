from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from recruiter.models import Recruiter

from .decorators import recruiter_required
from .forms import JobPostingForm
from .models import JobPosting


@recruiter_required
def my_job_postings(request):
    """List the current recruiter's postings and render the create/edit modal."""
    postings = JobPosting.objects.filter(owner=request.user).order_by("-created_at")
    form = JobPostingForm()
    context = {
        "template_data": {"title": "My Job Postings · DevJobs"},
        "postings": postings,
        "form": form,
    }
    return render(request, "recruiter/myjobpostings.html", context)


@recruiter_required
@require_http_methods(["POST"])
def job_create(request):
    """Create a new job posting owned by the current recruiter."""
    form = JobPostingForm(request.POST)
    if form.is_valid():
        job = form.save(commit=False)
        job.owner = request.user
        job.save()
        messages.success(request, "Job posting created.")
    else:
        messages.error(request, "Please fix the errors in the form.")
    return redirect("recruiter:jobs")


@recruiter_required
@require_http_methods(["POST"])
def job_update(request, pk: int):
    """Update an existing job posting (owned by current recruiter)."""
    job = get_object_or_404(JobPosting, pk=pk, owner=request.user)
    form = JobPostingForm(request.POST, instance=job)
    if form.is_valid():
        form.save()
        messages.success(request, "Job posting updated.")
    else:
        messages.error(request, "Please fix the errors in the form.")
    return redirect("recruiter:jobs")


@recruiter_required
@require_http_methods(["POST"])
def job_delete(request, pk: int):
    """Delete a job posting (owned by current recruiter)."""
    job = get_object_or_404(JobPosting, pk=pk, owner=request.user)
    job.delete()
    messages.success(request, "Job posting deleted.")
    return redirect("recruiter:jobs")


@require_http_methods(["GET"])
def recruiter_search(request):
    # Get all recruiters initially
    recruiters = Recruiter.objects.select_related("account").all()

    # Apply filters based on query parameters
    company = request.GET.get("company")
    if company:
        recruiters = recruiters.filter(company__icontains=company)

    position = request.GET.get("position")
    if position:
        recruiters = recruiters.filter(position__icontains=position)

    # Account-level filters
    city = request.GET.get("city")
    if city:
        recruiters = recruiters.filter(account__city__icontains=city)

    state = request.GET.get("state")
    if state:
        recruiters = recruiters.filter(account__state__icontains=state)

    country = request.GET.get("country")
    if country:
        recruiters = recruiters.filter(account__country__icontains=country)

    username = request.GET.get("username")
    if username:
        recruiters = recruiters.filter(account__username__icontains=username)

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

    total_count = recruiters.count()
    recruiters = recruiters[offset : offset + limit]

    # Serialize data
    results = []
    for recruiter in recruiters:
        account = recruiter.account
        results.append(
            {
                "id": recruiter.account.id,
                "username": account.username,
                "email": account.email,
                "phone_number": account.phone_number,
                "profile_picture": account.profile_picture,
                "street_address": account.street_address,
                "city": account.city,
                "state": account.state,
                "country": account.country,
                "zip_code": account.zip_code,
                "company": recruiter.company,
                "position": recruiter.position,
                "user_type": account.user_type,
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
