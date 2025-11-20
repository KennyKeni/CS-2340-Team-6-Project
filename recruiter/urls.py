from django.urls import path
from . import views

app_name = "recruiter"

urlpatterns = [
    path("search/", views.recruiter_search, name="recruiter_search"),
    path("candidates/", views.candidate_search, name="candidate_search"),
    path("candidates/map/", views.candidate_map, name="candidate_map"),
    path("profile/", views.profile, name="profile"),
    path("jobs/", views.my_job_postings, name="jobs"),
    path("jobs/create/", views.job_create, name="job_create"),
    path("jobs/<int:pk>/edit/", views.job_update, name="job_update"),
    path("jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
    path("jobs/<int:job_id>/applications/", views.job_applications_pipeline, name="job_applications"),
    path("applications/update-status/", views.update_application_status, name="update_application_status"),
    path("notifications/", views.notifications, name="notifications"),
    path("messages/", views.messages_list, name="messages"),
    path("message/<uuid:recipient_id>/", views.send_message, name="send_message"),
    path("email/<uuid:candidate_id>/", views.compose_email, name="compose_email"),
    path("emails/", views.email_history, name="email_history"),
    path("api/notifications/count/", views.get_unread_notifications_count, name="unread_notifications_count"),
    path("saved-searches/", views.saved_searches, name="saved_searches"),
    path("save-search/", views.save_search, name="save_search"),
    path("save-search/<int:search_id>/", views.save_search, name="edit_saved_search"),
    path("saved-search/<int:search_id>/delete/", views.delete_saved_search, name="delete_saved_search"),
]
