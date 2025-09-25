from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.utils import timezone
from .models import Job, JobApplication
from account.models import UserType


def job_listings(request):
    """Display all active job listings"""
    jobs = Job.objects.filter(is_active=True).select_related('recruiter')
    
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
    if request.user.is_authenticated and request.user.user_type == UserType.APPLICANT:
        applied_job_ids = JobApplication.objects.filter(
            applicant=request.user
        ).values_list('job_id', flat=True)
    else:
        applied_job_ids = []
    
    context = {
        'jobs': jobs,
        'applied_job_ids': applied_job_ids,
        'job_types': Job._meta.get_field('job_type').choices,
    }
    return render(request, 'job/job_listings.html', context)


def job_detail(request, job_id):
    """Display detailed job information"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user has already applied
    has_applied = False
    if request.user.is_authenticated and request.user.user_type == UserType.APPLICANT:
        has_applied = JobApplication.objects.filter(
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
    if request.user.user_type != UserType.APPLICANT:
        return JsonResponse({'error': 'Only applicants can apply to jobs'}, status=403)
    
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user has already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
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
        application = JobApplication.objects.create(
            job=job,
            applicant=request.user,
            personalized_note=personalized_note
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
