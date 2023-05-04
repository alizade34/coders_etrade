from django.shortcuts import render, redirect, get_object_or_404, reverse
from .forms import LoginForm, RegisterForm, ResetPasswordForm, ResetPasswordCompleteForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from services.generator import Generator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .decorators import not_authorized_user, check_activation_code_time
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


User = get_user_model()

def login_view(request):

    form = LoginForm()
    next_url = request.GET.get('next', None)

    if request.method == 'POST':
        form = LoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(email=email, password=password)
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect('/')

        else:
            print(form.errors) 

    context = {
        'form': form
    }

    return render(request, 'accounts/login.html', context)

@not_authorized_user
def register_view(request):

    form = RegisterForm()

    # if request.user.is_authenticated:
    #     return redirect('/')

    if request.method == 'POST':
        form = RegisterForm(request.POST or None)

        if form.is_valid():
            new_user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            new_user.set_password(password)
            new_user.is_active = False
            new_user.activation_code = Generator.create_activation_code(size=6, model_=User)
            new_user.activation_code_expires_at = timezone.now() + timezone.timedelta(minutes=15)
            new_user.save()

            # mail sending
            send_mail(
                "eTrade - Activation Code",
                f"Your Activation code is: {new_user.activation_code}",
                settings.EMAIL_HOST_USER,
                [new_user.email]
            )

            return redirect('accounts:activate-account', slug=new_user.slug)

    context = {
        'form': form
    }

    return render(request, 'accounts/register.html', context)

def logout_view(request):

    logout(request)
    return redirect('/')

@check_activation_code_time
def activate_account_view(request, slug):
    user = get_object_or_404(User, slug=slug)

    if request.method == 'POST':
        code = request.POST.get('code', None)

        if code == user.activation_code:
            user.is_active = True
            user.activation_code = None
            user.activation_code_expires_at = None
            user.save()

            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Activation code is incorrect!')

    context = {

    }

    return render(request, 'accounts/activate-account.html', context)

@login_required(login_url='/login/')
def change_password_view(request):
    form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST or None, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)

            return redirect('/')

    context = {
        "form": form,
    }

    return render(request, 'accounts/change-password.html', context)

def reset_passsword_view(request):
    form = ResetPasswordForm

    if request.method == "POST":
        form = ResetPasswordForm(request.POST or None)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)

            # mail process
            uuid64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            link = request.build_absolute_uri(reverse(
                "accounts:reset-password-check",
                kwargs={'uuid64': uuid64, 'token': token},

            ))
            # sending mail
            send_mail(
                "Password Reset",
                f"Please click the link below\n{link}",
                settings.EMAIL_HOST_USER,
                [email]
            )


            return redirect('accounts:login')

    context = {
        'form': form
    }

    return render(request, 'accounts/reset-password.html', context)


def reset_password_check_view(request, uuid64, token):
    id = smart_str(urlsafe_base64_decode(uuid64))
    user = User.objects.get(id=id)

    if not PasswordResetTokenGenerator().check_token(user=user, token=token):
        messages.error(request, 'Token is wrong.')
        return redirect('accounts:login')

    return redirect('accounts:reset-password-complete', uuid64=uuid64)

def reset_password_complete_view(request, uuid64):
    form = ResetPasswordCompleteForm()

    id = smart_str(urlsafe_base64_decode(uuid64))
    user = User.objects.get(id=id)

    if request.method == 'POST':
        form = ResetPasswordCompleteForm(request.POST or None)

        if form.is_valid():
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()

            return redirect('/login/')
    context = {
        'form': form
    }

    return render(request, 'accounts/reset-password-complete.html', context)