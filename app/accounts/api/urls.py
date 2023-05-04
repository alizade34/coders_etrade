from django.urls import path
from . import views

app_name = "accounts-api"


urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("activate/<slug>/", views.ActivationView.as_view(), name="activate"),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-check/<uidb64>/<token>/', views.ResetPasswordConfirmView.as_view(), name='reset-password-check'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password')
]