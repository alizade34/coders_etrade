from rest_framework import generics
from rest_framework.response import Response
from .serializers import (
    LoginSerializer, RegisterSerializer, ActivationSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer,
    ChangePasswordSerializer
)
from accounts.models import MyUser as User
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from rest_framework import status
from django.shortcuts import reverse
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # email = serializer.validated_data.get("email")
        # user = User.objects.get(email=email)
        #
        # token = RefreshToken.for_user(user)
        #
        # data = {
        #     **serializer.data,
        #     "refresh": str(token),
        #     "access": str(token.access_token)
        # }

        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    # def post(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save(is_active=True)
    #
    #     return Response(serializer.data, status=201)


class ActivationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ActivationSerializer
    lookup_field = 'slug'

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"user": self.get_object()}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = User.objects.get(email=email)
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = request.build_absolute_uri(reverse(
            "accounts-api:reset-password-check",
            kwargs={'uidb64': uidb64, 'token': token},
        ))

        send_mail(
            "Password Reset",
            f"Please click the link below\n{reset_link}",
            settings.EMAIL_HOST_USER,
            [email]
        )

        return Response(
            {'message': 'Password reset link has been sent to your email.'},
            status=status.HTTP_200_OK
        )


class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user=user, token=token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            password = serializer.validated_data.get('password')
            user.password = make_password(password)
            user.save()
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': _('Invalid reset link.')}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    # permission_classes = (IsAuthenticated, )
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['old_password']
        )

        if user is not None:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)