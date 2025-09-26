from django.urls import path

from account import views
# app_name = "account"
urlpatterns = [
    path("signup/", views.account_signup, name="signup"),
    path(route="login/", view=views.account_login, name="login"),
    path("logout/", views.account_logout, name="logout"),
    path("profile/update/", views.profile_update, name="profile_update"),
]
