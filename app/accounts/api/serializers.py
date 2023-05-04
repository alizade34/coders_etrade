from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from services.generator import Generator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, allow_blank=False
    )

    class Meta:
        model = User
        fields = ("email", "password")
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = User.objects.filter(email=email)

        if not user.exists():
            raise serializers.ValidationError({"error": "This email address does not exist!"})

        user = user.get()

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "The password is wrong!"})

        return attrs

    def to_representation(self, instance):
        repr_ = super().to_representation(instance)
        user = User.objects.get(email=instance.get('email'))
        token = RefreshToken.for_user(user)
        repr_["tokens"] = {
            "refresh": str(token),
            "access": str(token.access_token)

        }
        return repr_


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, allow_blank=False
    )
    password_confirm = serializers.CharField(
        style={"input_type": "password"}, write_only=True, allow_blank=False
    )

    class Meta:
        model = User
        fields = ("email", 'fullname', 'slug', 'password', 'password_confirm')
        extra_kwargs = {
            "password": {"write_only": True},
            "slug": {"read_only": True}
        }


    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "This email already exists"})

        if password != password_confirm:
            raise serializers.ValidationError({"error": "Passwords do not match"})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        user = User.objects.create(
            **validated_data, is_active=False,
            activation_code=Generator.create_activation_code(size=6, model_=User),
            activation_code_expires_at=timezone.now() + timezone.timedelta(minutes=15)
        )
        user.set_password(password)
        user.save()

        # mail sending
        send_mail(
            "Meliora - Activation Code",
            f"Your Activation code is: {user.activation_code}",
            settings.EMAIL_HOST_USER,
            [user.email]
        )

        return user


class ActivationSerializer(serializers.ModelSerializer):
    activation_code = serializers.CharField(max_length=255)
    class Meta:
        model = User
        fields = ('email', 'slug', 'activation_code')
        extra_kwargs = {
            'email': {'read_only': True},
            'slug': {'read_only': True}
        }

    def validate(self, attrs):
        activation_code = attrs.get('activation_code')
        user = self.context.get("user")
        now = timezone.now()
        if now > user.activation_code_expires_at:
            raise serializers.ValidationError(
                {
                    "error": "Activation code has expired"
                }
            )

        if str(activation_code) != str(user.activation_code):
            raise serializers.ValidationError(
                {
                    "error": "Activation code is wrong"
                }
            )

        return attrs

    def create(self, validated_data):
        user = self.context.get('user')
        user.is_active = True
        user.activation_code = None
        user.activation_code_expires_at = None
        user.save()

        return user

    def to_representation(self, instance):
        repr_ = super().to_representation(instance)
        token = RefreshToken.for_user(instance)
        repr_["tokens"] = {
            "refresh": str(token),
            "access": str(token.access_token)

        }
        return repr_


class ResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ('email', )

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("User with this email address does not exist."))
        return value


class ResetPasswordConfirmSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, allow_blank=False
    )
    password_confirm = serializers.CharField(
        style={"input_type": "password"}, write_only=True, allow_blank=False
    )

    class Meta:
        model = User
        fields = ('password', 'password_confirm')

    def validate_password(self, value):
        # Add any additional password validation logic here, such as checking for complexity requirements
        return value


class ChangePasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    old_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, allow_blank=False
    )
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, allow_blank=False
    )

    class Meta:
        model = User
        fields = ('email', 'old_password', 'new_password')
