from django.urls import path
from . import views

app_name = "applicant"

urlpatterns = [
    path("search/", views.applicant_search, name="applicant_search"),
    path("applications/", views.my_applications, name="applications"),
    path("profile/create/", views.create_profile, name="create_profile"),
    path("profile/view/", views.view_profile, name="view_profile"),
    path("recommendations/", views.job_recommendations, name="job_recommendations"),
    
    # Messaging and notifications
    path("notifications/", views.notifications, name="notifications"),
    path("messages/", views.messages_list, name="messages"),
    path("api/notifications/count/", views.get_unread_notifications_count, name="unread_notifications_count"),
]
