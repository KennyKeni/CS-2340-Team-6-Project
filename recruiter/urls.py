from django.urls import path
from . import views

app_name = "recruiter"

urlpatterns = [
    path("search/", views.recruiter_search, name="recruiter_search"),
    path("candidates/", views.candidate_search, name="candidate_search"),
    path("jobs/", views.my_job_postings, name="jobs"),
    path("jobs/create/", views.job_create, name="job_create"),
    path("jobs/<int:pk>/edit/", views.job_update, name="job_update"),
    path("jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
]
