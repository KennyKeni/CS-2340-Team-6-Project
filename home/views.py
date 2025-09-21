from django.shortcuts import render


def index(request):
    # Basic context; plays nicely with your base.html title usage
    context = {
        "template_data": {"title": "Home · DevJobs"},
    }
    return render(request, "home/index.html", context)
