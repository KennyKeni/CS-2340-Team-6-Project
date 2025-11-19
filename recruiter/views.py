from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .decorators import recruiter_required
from .forms import MessageForm, SavedSearchForm, CandidateEmailForm
from .models import Recruiter, Notification, Message, SavedSearch, CandidateEmail
from job.forms import JobPostingForm
from job.models import JobPosting
from job.utils import geocode_address
from applicant.models import Applicant, Application, ApplicationStatus
from account.models import Account
from utils.messaging import get_messages_context


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
                "user_type": "recruiter",
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


@recruiter_required
def my_job_postings(request):
    postings = JobPosting.objects.filter(owner=request.user).order_by("-created_at")
    form = JobPostingForm()
    context = {
        "template_data": {"title": "My Job Postings · DevJobs"},
        "postings": postings,
        "form": form,
        # For default page load, modal is closed; action points to create
        "open_modal": False,
        "modal_title": "Create Job Posting",
        "form_action": "recruiter:job_create",
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, "recruiter/myjobpostings.html", context)


@recruiter_required
@require_http_methods(["GET", "POST"])
def job_create(request):
    """GET = show blank form in open modal. POST = create."""
    if request.method == "GET":
        postings = JobPosting.objects.filter(owner=request.user).order_by("-created_at")
        form = JobPostingForm()
        return render(
            request,
            "recruiter/myjobpostings.html",
            {
                "template_data": {"title": "My Job Postings · DevJobs"},
                "postings": postings,
                "form": form,
                "open_modal": True,                 # modal visible
                "modal_title": "Create Job Posting",
                "form_action": "recruiter:job_create",
                "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
            },
        )

    # POST
    form = JobPostingForm(request.POST)
    if form.is_valid():
        job = form.save(commit=False)
        job.owner = request.user

        # Geocode the address to get latitude and longitude
        latitude, longitude = geocode_address(
            street_address=job.street_address,
            city=job.city,
            state=job.state,
            zip_code=job.zip_code,
            country=job.country
        )
        if latitude and longitude:
            job.latitude = latitude
            job.longitude = longitude

        job.save()
        form.save_skills(job)
        messages.success(request, "Job posting created.")
        return redirect("recruiter:jobs")

    postings = JobPosting.objects.filter(owner=request.user).order_by("-created_at")
    messages.error(request, "Please fix the errors in the form.")
    return render(
        request,
        "recruiter/myjobpostings.html",
        {
            "template_data": {"title": "My Job Postings · DevJobs"},
            "postings": postings,
            "form": form,                         # bound with errors
            "open_modal": True,
            "modal_title": "Create Job Posting",
            "form_action": "recruiter:job_create",
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        },
        status=400,
    )


@recruiter_required
@require_http_methods(["GET", "POST"])
def job_update(request, pk: int):
    """GET = open modal prefilled. POST = save edits."""
    job = get_object_or_404(JobPosting, pk=pk, owner=request.user)

    if request.method == "GET":
        postings = JobPosting.objects.filter(owner=request.user).order_by("-created_at")
        form = JobPostingForm(instance=job)
        return render(
            request,
            "recruiter/myjobpostings.html",
            {
                "template_data": {"title": "My Job Postings · DevJobs"},
                "postings": postings,
                "form": form,
                "open_modal": True,
                "modal_title": "Edit Job Posting",
                "form_action": "recruiter:job_update",  # will pass pk in template
                "edit_pk": job.pk,
                "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
            },
        )

    # POST
    form = JobPostingForm(request.POST, instance=job)
    if form.is_valid():
        job = form.save(commit=False)

        # Geocode the address to get latitude and longitude
        latitude, longitude = geocode_address(
            street_address=job.street_address,
            city=job.city,
            state=job.state,
            zip_code=job.zip_code,
            country=job.country
        )
        if latitude and longitude:
            job.latitude = latitude
            job.longitude = longitude

        job.save()
        form.save_skills(job)
        messages.success(request, "Job posting updated.")
        return redirect("recruiter:jobs")

    postings = JobPosting.objects.filter(owner=request.user).order_by("-created_at")
    messages.error(request, "Please fix the errors in the form.")
    return render(
        request,
        "recruiter/myjobpostings.html",
        {
            "template_data": {"title": "My Job Postings · DevJobs"},
            "postings": postings,
            "form": form,
            "open_modal": True,
            "modal_title": "Edit Job Posting",
            "form_action": "recruiter:job_update",
            "edit_pk": job.pk,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        },
        status=400,
    )


@recruiter_required
@require_http_methods(["POST"])
def job_delete(request, pk: int):
    """Delete a job posting (owned by current recruiter)."""
    job = get_object_or_404(JobPosting, pk=pk, owner=request.user)
    job.delete()
    messages.success(request, "Job posting deleted.")
    return redirect("recruiter:jobs")


@recruiter_required
def candidate_search(request):
    """Search for candidates/applicants with filtering"""
    candidates = Applicant.objects.select_related('account', 'privacy_settings').prefetch_related(
        'skills', 'work_experiences', 'education', 'links'
    ).all()

    # Filter out candidates who have hidden their profiles from recruiters
    candidates = candidates.filter(
        Q(privacy_settings__visible_to_recruiters=True) | 
        Q(privacy_settings__isnull=True)  # Include profiles without privacy settings (default visible)
    )

    # Get search parameters
    q = request.GET.get('q', '').strip()  # Name/headline search
    username = request.GET.get('username', '').strip()  # Exact username search
    skills = request.GET.get('skills', '').strip()
    projects = request.GET.get('projects', '').strip()  # Links search
    city = request.GET.get('city', '').strip()
    state = request.GET.get('state', '').strip()
    country = request.GET.get('country', '').strip()

    # Apply filters
    if username:
        # Exact username match (takes priority over q)
        candidates = candidates.filter(account__username__iexact=username)
    elif q:
        # Search in name (first_name, last_name, username) and headline
        candidates = candidates.filter(
            Q(account__first_name__icontains=q) |
            Q(account__last_name__icontains=q) |
            Q(account__username__icontains=q) |
            Q(headline__icontains=q)
        )

    if skills:
        # Search in skills (comma-separated)
        for skill in [s.strip() for s in skills.split(',') if s.strip()]:
            candidates = candidates.filter(skills__skill_name__icontains=skill)

    if projects:
        # Search in links (GitHub, portfolio URLs, descriptions)
        candidates = candidates.filter(
            Q(links__url__icontains=projects) |
            Q(links__description__icontains=projects)
        )

    if city:
        candidates = candidates.filter(account__city__icontains=city)

    if state:
        candidates = candidates.filter(account__state__icontains=state)

    if country:
        candidates = candidates.filter(account__country__icontains=country)

    # Remove duplicates that might occur due to joins
    candidates = candidates.distinct()

    context = {
        'candidates': candidates,
        'template_data': {'title': 'Find Candidates · DevJobs'},
    }
    return render(request, 'recruiter/candidate_search.html', context)




@login_required
def notifications(request):
    """View to show all notifications for the current user"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'related_job', 'related_application', 'related_message').order_by('-created_at')
    
    # Mark notifications as read when viewed
    notifications.filter(is_read=False).update(is_read=True)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'template_data': {
            'title': 'Notifications · DevJobs'
        }
    }
    return render(request, 'recruiter/notifications.html', context)


@login_required
def send_message(request, recipient_id):
    """View for sending direct messages"""
    recipient = get_object_or_404(Account, id=recipient_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user, recipient=recipient)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            
            # Create notification for recipient
            Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notification_type='message',
                title=f'New message from {request.user.get_full_name()}',
                message=f'You have received a new message: {message.subject}',
                related_message=message
            )

            messages.success(request, f'Message sent to {recipient.get_full_name()}!')
            
            # Redirect to appropriate messages page based on user type
            if hasattr(request.user, 'applicant'):
                return redirect(f"{reverse('applicant:messages')}?partner_id={recipient.id}")
            else:
                return redirect(f"{reverse('recruiter:messages')}?partner_id={recipient.id}")
    else:
        form = MessageForm(sender=request.user, recipient=recipient)
    
    context = {
        'form': form,
        'recipient': recipient,
        'template_data': {
            'title': f'Message {recipient.get_full_name()} · DevJobs'
        }
    }
    return render(request, 'recruiter/send_message.html', context)


@login_required
def messages_list(request):
    """View to show all conversations for the current user"""
    # Get messaging context from shared utility
    context = get_messages_context(request)

    # Add template-specific data
    context['template_data'] = {
        'title': 'Message History · DevJobs'
    }

    return render(request, 'recruiter/messages.html', context)


@login_required
@recruiter_required
def saved_searches(request):
    """View to manage saved searches"""
    searches = SavedSearch.objects.filter(
        recruiter=request.user
    ).order_by('-created_at')
    
    context = {
        'searches': searches,
        'template_data': {
            'title': 'Saved Searches · DevJobs'
        }
    }
    return render(request, 'recruiter/saved_searches.html', context)


@login_required
@recruiter_required
def save_search(request, search_id=None):
    """View to create a new saved search or edit an existing one"""
    search = None
    if search_id:
        search = get_object_or_404(SavedSearch, id=search_id, recruiter=request.user)
    
    if request.method == 'POST':
        form = SavedSearchForm(request.POST, instance=search)
        if form.is_valid():
            search = form.save(commit=False)
            search.recruiter = request.user
            
            # The form's clean methods already convert comma-separated strings to lists
            search.skills = form.cleaned_data.get('skills', [])
            
            search.save()
            messages.success(request, 'Search saved successfully!')
            return redirect('recruiter:saved_searches')
    else:
        if search:
            # Editing existing search
            form = SavedSearchForm(instance=search)
        else:
            # Pre-populate form with current search parameters
            form = SavedSearchForm(initial={
                'skills': request.GET.get('skills', ''),
                'city': request.GET.get('city', ''),
                'state': request.GET.get('state', ''),
                'country': request.GET.get('country', ''),
            })
    
    context = {
        'form': form,
        'template_data': {
            'title': 'Save Search · DevJobs'
        }
    }
    return render(request, 'recruiter/save_search.html', context)


@login_required
@recruiter_required
def delete_saved_search(request, search_id):
    """View to delete a saved search"""
    search = get_object_or_404(SavedSearch, id=search_id, recruiter=request.user)
    search.delete()
    messages.success(request, 'Search deleted successfully!')
    return redirect('recruiter:saved_searches')


@login_required
def get_unread_notifications_count(request):
    """API endpoint to get unread notifications count"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
@recruiter_required
def compose_email(request, candidate_id):
    """View for recruiters to compose and send emails to candidates"""
    candidate = get_object_or_404(Account, id=candidate_id)
    recruiter = request.user.recruiter

    # Ensure the candidate is actually an applicant
    if not hasattr(candidate, 'applicant'):
        messages.error(request, "The specified user is not a candidate.")
        return redirect('recruiter:candidate_search')

    if request.method == 'POST':
        form = CandidateEmailForm(request.POST, recruiter=recruiter)
        if form.is_valid():
            email = form.save(commit=False)
            email.sender = request.user
            email.recipient = candidate

            # Try to send the email
            try:
                # Add recruiter signature to email body
                email_body_with_signature = f"{email.body}\n\n---\n{request.user.first_name} {request.user.last_name}\n{request.user.email}"

                send_mail(
                    subject=f"{settings.EMAIL_SUBJECT_PREFIX}{email.subject}",
                    message=email_body_with_signature,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[candidate.email],
                    fail_silently=False,
                )
                email.is_sent = True
                messages.success(request, f"Email sent successfully to {candidate.get_full_name()}!")
            except Exception as e:
                email.is_sent = False
                email.error_message = str(e)
                messages.error(request, f"Failed to send email: {str(e)}")

            email.save()
            return redirect('recruiter:email_history')
    else:
        form = CandidateEmailForm(recruiter=recruiter)

    context = {
        'form': form,
        'candidate': candidate,
        'template_data': {
            'title': f'Email {candidate.get_full_name()} · DevJobs'
        }
    }
    return render(request, 'recruiter/compose_email.html', context)


@login_required
@recruiter_required
def email_history(request):
    """View to show email history for the current recruiter"""
    emails = CandidateEmail.objects.filter(
        sender=request.user
    ).select_related('recipient', 'related_job').order_by('-sent_at')

    # Pagination
    paginator = Paginator(emails, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'emails': page_obj,
        'template_data': {
            'title': 'Email History · DevJobs'
        }
    }
    return render(request, 'recruiter/email_history.html', context)


@login_required
@recruiter_required
def job_applications_pipeline(request, job_id):
    """View to display applications for a specific job in a Kanban board format"""
    # Get the job and verify the recruiter owns it
    job = get_object_or_404(JobPosting, pk=job_id, owner=request.user)

    # Get all applications for this job
    applications = Application.objects.filter(job=job).select_related(
        'applicant', 'applicant__applicant'
    ).prefetch_related(
        'applicant__applicant__skills'
    ).order_by('-updated_at')

    # Group applications by status for Kanban columns
    applications_by_status = {
        ApplicationStatus.APPLIED: [],
        ApplicationStatus.REVIEW: [],
        ApplicationStatus.INTERVIEW: [],
        ApplicationStatus.OFFER: [],
        ApplicationStatus.CLOSED: [],
    }

    for application in applications:
        if application.status in applications_by_status:
            applications_by_status[application.status].append(application)

    context = {
        'job': job,
        'applications_by_status': applications_by_status,
        'status_choices': ApplicationStatus.choices,
        'template_data': {
            'title': f'Applications: {job.title} · DevJobs'
        }
    }
    return render(request, 'recruiter/job_applications_pipeline.html', context)


@login_required
@recruiter_required
@require_http_methods(["POST"])
def update_application_status(request):
    """AJAX endpoint to update an application's status"""
    try:
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')

        if not application_id or not new_status:
            return JsonResponse({
                'success': False,
                'error': 'Missing application_id or status'
            }, status=400)

        # Validate status is valid
        valid_statuses = [status[0] for status in ApplicationStatus.choices]
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'error': 'Invalid status value'
            }, status=400)

        # Get the application and verify the recruiter owns the job
        application = get_object_or_404(Application, pk=application_id)

        if application.job.owner != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to update this application'
            }, status=403)

        # Update the status
        application.status = new_status
        application.save()

        return JsonResponse({
            'success': True,
            'message': 'Application status updated successfully',
            'new_status': application.get_status_display()
        })

    except Application.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Application not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@recruiter_required
def candidate_map(request):
    """
    Display candidates on an interactive map with location clustering.
    Respects privacy settings for exact vs approximate locations.
    """
    # Get all visible applicants with geocoded locations and privacy settings
    applicants = (
        Applicant.objects
        .select_related('account', 'privacy_settings')
        .prefetch_related('skills')
        .filter(
            Q(privacy_settings__visible_to_recruiters=True) |
            Q(privacy_settings__isnull=True)  # Include profiles without privacy settings
        )
        .filter(
            account__latitude__isnull=False,
            account__longitude__isnull=False
        )
    )

    # Apply search filters from query parameters
    skills = request.GET.get('skills')
    if skills:
        skill_list = [s.strip() for s in skills.split(',')]
        for skill in skill_list:
            applicants = applicants.filter(skills__skill_name__icontains=skill)

    city = request.GET.get('city')
    if city:
        applicants = applicants.filter(account__city__icontains=city)

    state = request.GET.get('state')
    if state:
        applicants = applicants.filter(account__state__icontains=state)

    country = request.GET.get('country')
    if country:
        applicants = applicants.filter(account__country__icontains=country)

    # Build candidate data for the map
    candidates_data = []
    for applicant in applicants.distinct():
        privacy_settings = applicant.get_or_create_privacy_settings()

        # Determine what location info to show based on privacy settings
        show_exact = privacy_settings.show_exact_location
        show_approx = privacy_settings.show_approximate_location

        # Skip if both location settings are False
        if not show_exact and not show_approx:
            continue

        # Get account data
        account = applicant.account

        # Determine location precision for display
        if show_exact:
            location_type = 'exact'
            location_display = f"{account.street_address}, {account.city}, {account.state}" if account.street_address else f"{account.city}, {account.state}"
        elif show_approx:
            location_type = 'approximate'
            location_display = f"{account.city}, {account.state}"
        else:
            continue  # Skip if no location to show

        # Get top skills
        top_skills = list(applicant.skills.values_list('skill_name', flat=True)[:5])

        candidates_data.append({
            'id': str(applicant.account.id),
            'name': account.get_full_name() or account.username,
            'username': account.username,
            'headline': applicant.headline if privacy_settings.show_headline else '',
            'location': location_display,
            'location_type': location_type,  # 'exact' or 'approximate'
            'latitude': account.latitude,
            'longitude': account.longitude,
            'skills': top_skills if privacy_settings.show_skills else [],
            'email': account.email if privacy_settings.show_email else None,
        })

    import json

    context = {
        'template_data': {
            'title': 'Candidate Map · DevJobs'
        },
        'candidates_json': json.dumps(candidates_data),
        'candidates_count': len(candidates_data),
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'filters': {
            'skills': skills or '',
            'city': city or '',
            'state': state or '',
            'country': country or '',
        }
    }

    return render(request, 'recruiter/candidate_map.html', context)
