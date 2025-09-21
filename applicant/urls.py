from django.urls import path
from . import views

app_name = "applicant"

urlpatterns = [
    path("search/", views.applicant_search, name="applicant_search"),
    path("applications/", views.my_applications, name="applications"),
]
