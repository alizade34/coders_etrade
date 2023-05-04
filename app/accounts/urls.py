from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('activate-account/<slug>/', views.activate_account_view, name='activate-account'),
    path('change-password/', views.change_password_view, name='change-password'),
    path('reset-password/', views.reset_passsword_view, name='reset-password'),
    path('reset-password-check/<uuid64>/<token>/', views.reset_password_check_view, name='reset-password-check'),
    path('reset-password-complete/<uuid64>/', views.reset_password_complete_view, name='reset-password-complete'),
]