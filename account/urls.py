from django.urls import path

from account import views

urlpatterns = [
    path('signup/', views.account_signup, name='account.signup'),
    path(route='login/', view=views.account_login, name='account.login'),
    path('logout/', views.account_logout, name='account.logout'),
    path('profile/update/', views.profile_update, name='account.profile_update'),
]
