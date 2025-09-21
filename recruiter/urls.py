from django.urls import path

from recruiter import views

urlpatterns = [
    path("search/", views.recruiter_search, name="recruiter.search"),
]
