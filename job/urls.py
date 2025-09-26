from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_listings, name='job_listings'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply_to_job, name='apply_to_job'),
]
