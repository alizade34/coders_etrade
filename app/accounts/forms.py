from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField

User = get_user_model()

class LoginForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'class-control'})

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise forms.ValidationError('Email or password is wrong')

        if not user.is_active:
            raise forms.ValidationError('Your account is not active')

        return self.cleaned_data

class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('email', 'fullname', 'password', 'password_confirm')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'class-control'})

    def clean(self):

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This username already exists')
        
        if password != password_confirm:
            raise forms.ValidationError('Passwords do not match')
        
        return self.cleaned_data

class ResetPasswordForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', )

    def clean(self):
        email = self.cleaned_data.get('email')

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This user does not exist")

        return self.cleaned_data

class ResetPasswordCompleteForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label='New password')
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label='New password confirm')

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError('Passwords do not match')

        return self.cleaned_data

class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email','fullname','password1','password2')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email','fullname','password', 'is_active', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]