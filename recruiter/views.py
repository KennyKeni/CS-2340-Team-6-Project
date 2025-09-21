from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

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
