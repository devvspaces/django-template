from django import forms
from django.contrib.auth import password_validation

from utils.validators import validate_special_char

from .models import Profile, User


# User form for admin
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        min_length=8,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Must be similar to first password to pass verification",
    )
    username = forms.CharField(
        max_length=20,
        label="Profile Username",
        help_text="Enter a unique username for this user",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    subscription = forms.ChoiceField(
        choices=Profile.ACCOUNT_SUBSCRIPTION, required=False
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password2",
        )

    # Validate the username if unique
    def clean_username(self):
        username = self.cleaned_data.get("username")

        # Validate the username has only valid chars
        validate_special_char(username)

        # Does username already exist
        if User.objects.filter(username__exact=username).exists():
            raise forms.ValidationError("Username name is not available")

        return username

    def clean_password(self):
        ps1 = self.cleaned_data.get("password")
        password_validation.validate_password(ps1, None)
        return ps1

    def clean_password2(self):
        ps1 = self.cleaned_data.get("password")
        ps2 = self.cleaned_data.get("password2")
        if (ps1 and ps2) and (ps1 != ps2):
            raise forms.ValidationError("The passwords does not match")
        return ps2

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get("password"))

        if commit:
            user.save()
            # Profile is already created, update values with data in form
            profile = user.profile
            subscription = self.cleaned_data.get("subscription")
            # Add data
            profile.subscription = subscription if subscription else "F"
            profile.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError({
                "username": "Username or password is incorrect"
            })

        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise forms.ValidationError({
                "username": "Username or password is incorrect"
            })

        return cleaned_data
