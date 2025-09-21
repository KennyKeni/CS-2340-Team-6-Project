from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from recruiter.models import Recruiter


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
