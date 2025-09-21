from django.urls import path

from applicant import views

urlpatterns = [
    path("search/", views.applicant_search, name="applicant.search"),
]
