from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from recruiter.models import JobPosting
from .forms import ApplicationNoteForm
# from .models import Application
from django.apps import apps

def search_jobs(request):
	jobs = JobPosting.objects.all()
	title = request.GET.get('title', '').strip()
	skills = request.GET.get('skills', '').strip()
	location = request.GET.get('location', '').strip()
	salary_min = request.GET.get('salary_min', '').strip()
	salary_max = request.GET.get('salary_max', '').strip()
	remote = request.GET.get('remote', '')
	visa = request.GET.get('visa', '')

	if title:
		jobs = jobs.filter(title__icontains=title)
	if skills:
		for skill in [s.strip() for s in skills.split(',') if s.strip()]:
			jobs = jobs.filter(skills_required__icontains=skill)
	if location:
		jobs = jobs.filter(location__icontains=location)
	if salary_min:
		jobs = jobs.filter(salary__regex=r'\d+')  # crude filter, assumes salary is a string
	if salary_max:
		jobs = jobs.filter(salary__regex=r'\d+')
	if remote == 'remote':
		jobs = jobs.filter(remote=True)
	elif remote == 'onsite':
		jobs = jobs.filter(remote=False)
	if visa == 'yes':
		jobs = jobs.filter(visa_sponsorship=True)
	elif visa == 'no':
		jobs = jobs.filter(visa_sponsorship=False)

	context = {
		'jobs': jobs,
	}
	return render(request, 'job/search.html', context)

def _get_applicant_application_model():
    return apps.get_model("applicant", "Application")

@require_http_methods(["GET"])
def job_detail(request, pk: int):
    job = get_object_or_404(JobPosting, pk=pk)
    AppApplication = _get_applicant_application_model()

    existing_application = None
    if request.user.is_authenticated:
        existing_application = AppApplication.objects.filter(
            job=job, applicant=request.user
        ).first()

    form = ApplicationNoteForm()
    return render(request, "job/job_detail.html", {
        "job": job,
        "form": form,
        "existing_application": existing_application,
    })

@login_required
@require_http_methods(["POST"])
def apply_to_job(request, pk: int):
    job = get_object_or_404(JobPosting, pk=pk)
    form = ApplicationNoteForm(request.POST)
    AppApplication = _get_applicant_application_model()

    if not form.is_valid():
        messages.error(request, "Please fix the errors and try again.")
        return redirect("job:job_detail", pk=job.pk)

    note = form.cleaned_data.get("note", "")

    # Only set fields that actually exist on applicant.Application
    model_field_names = {f.name for f in AppApplication._meta.get_fields()}
    defaults = {}
    if "note" in model_field_names:
        defaults["note"] = note
    if "status" in model_field_names:
        defaults.setdefault("status", "applied")

    app, created = AppApplication.objects.get_or_create(
        job=job, applicant=request.user, defaults=defaults
    )
    if not created and "note" in model_field_names:
        AppApplication.objects.filter(pk=app.pk).update(note=note)

    messages.success(request, "Application submitted.")
    return redirect("job:job_detail", pk=job.pk)