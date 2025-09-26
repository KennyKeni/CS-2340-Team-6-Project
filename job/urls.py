from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_jobs, name='search_jobs'),
    path('search/', views.search_jobs, name='search_jobs'),
    path("<int:pk>/", views.job_detail, name="job_detail"),
    path("<int:pk>/apply/", views.apply_to_job, name="apply_to_job"),
]