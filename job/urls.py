from django.urls import path
from . import views

urlpatterns = [
    # Existing routes
    path('', views.job_listings, name='job_listings'),
    path('search/', views.search_jobs, name='search_jobs'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply_to_job, name='apply_to_job'),

    path('map/', views.job_map, name='job_map'),
]
