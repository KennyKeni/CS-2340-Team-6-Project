from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.utils import timezone
from .models import JobPosting
from applicant.models import Application
from applicant.utils import is_applicant


def job_listings(request):
    """Display all active job listings"""
    jobs = JobPosting.objects.filter(is_active=True).select_related('owner')
    
    # Filter by job type if provided
    job_type = request.GET.get('type')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Filter by location if provided
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Filter by company if provided
    company = request.GET.get('company')
    if company:
        jobs = jobs.filter(company__icontains=company)
    
    # Check if user has already applied to each job
    if request.user.is_authenticated and is_applicant(request.user):
        applied_job_ids = Application.objects.filter(
            applicant=request.user
        ).values_list('job_id', flat=True)
    else:
        applied_job_ids = []
    
    context = {
        'jobs': jobs,
        'applied_job_ids': applied_job_ids,
        'job_types': JobPosting._meta.get_field('job_type').choices,
    }
    return render(request, 'job/job_listings.html', context)


def job_detail(request, job_id):
    """Display detailed job information"""
    job = get_object_or_404(JobPosting, id=job_id, is_active=True)

    # Check if user has already applied
    has_applied = False
    if request.user.is_authenticated and is_applicant(request.user):
        has_applied = Application.objects.filter(
            job=job, 
            applicant=request.user
        ).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
    }
    return render(request, 'job/job_detail.html', context)


@login_required
@require_http_methods(["POST"])
def apply_to_job(request, job_id):
    """Apply to a job with personalized note"""
    if not is_applicant(request.user):
        return JsonResponse({'error': 'Only applicants can apply to jobs'}, status=403)
    
    job = get_object_or_404(JobPosting, id=job_id, is_active=True)

    # Check if user has already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        return JsonResponse({'error': 'You have already applied to this job'}, status=400)
    
    try:
        # Get personalized note from request
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            personalized_note = data.get('personalized_note', '')
        else:
            personalized_note = request.POST.get('personalized_note', '')
        
        # Create application
        application = Application.objects.create(
            job=job,
            applicant=request.user,
            note=personalized_note
        )
        
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Application submitted successfully!',
                'application_id': application.id
            })
        else:
            messages.success(request, 'Application submitted successfully!')
            return redirect('job:job_detail', job_id=job_id)
            
    except IntegrityError:
        return JsonResponse({'error': 'You have already applied to this job'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Failed to submit application'}, status=500)


def search_jobs(request):
    """Enhanced job search with advanced filtering"""
    jobs = JobPosting.objects.filter(is_active=True).select_related('owner')

    # Get search parameters
    title = request.GET.get('title', '').strip()
    skills = request.GET.get('skills', '').strip()
    location = request.GET.get('location', '').strip()
    salary_min = request.GET.get('salary_min', '').strip()
    salary_max = request.GET.get('salary_max', '').strip()
    remote = request.GET.get('remote', '')
    visa = request.GET.get('visa', '')

    # Apply filters
    if title:
        jobs = jobs.filter(title__icontains=title)

    if skills:
        # Search in requirements field for skills (comma-separated)
        for skill in [s.strip() for s in skills.split(',') if s.strip()]:
            jobs = jobs.filter(requirements__icontains=skill)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if salary_min:
        try:
            min_salary = float(salary_min)
            jobs = jobs.filter(salary_min__gte=min_salary)
        except ValueError:
            pass

    if salary_max:
        try:
            max_salary = float(salary_max)
            jobs = jobs.filter(salary_max__lte=max_salary)
        except ValueError:
            pass

    if remote == 'remote':
        jobs = jobs.filter(job_type='remote')
    elif remote == 'onsite':
        jobs = jobs.exclude(job_type='remote')

    if visa == 'yes':
        jobs = jobs.filter(visa_sponsorship=True)
    elif visa == 'no':
        jobs = jobs.filter(visa_sponsorship=False)

    # Check if user has already applied to each job
    if request.user.is_authenticated and is_applicant(request.user):
        applied_job_ids = Application.objects.filter(
            applicant=request.user
        ).values_list('job_id', flat=True)
    else:
        applied_job_ids = []

    context = {
        'jobs': jobs,
        'applied_job_ids': applied_job_ids,
        'job_types': JobPosting._meta.get_field('job_type').choices,
    }
    return render(request, 'job/search.html', context)
