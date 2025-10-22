# account/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from account.models import Account
from applicant.models import Applicant
from recruiter.models import Recruiter


class CustomErrorList(ErrorList):
    """Custom error list styling for Bootstrap alerts."""

    def __str__(self):
        if not self:
            return ""
        return mark_safe(
            "".join(
                [
                    f'<div class="alert alert-danger" role="alert">{e}</div>'
                    for e in self
                ]
            )
        )


class CustomUserCreationForm(UserCreationForm):
    """User registration form supporting both applicants and recruiters."""

    user_type = forms.ChoiceField(
        choices=[("applicant", "Applicant"), ("recruiter", "Recruiter")],
        widget=forms.Select(attrs={"class": "form-control"})
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    # Address fields
    street_address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    city = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    state = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    country = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    zip_code = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))

    # Applicant-specific
    headline = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    # Recruiter-specific
    company = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    position = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = Account
        fields = (
            "username", "email", "first_name", "last_name", "phone_number",
            "street_address", "city", "state", "country", "zip_code",
            "password1", "password2"
        )

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in self.fields:
            self.fields[fieldname].help_text = ""
            self.fields[fieldname].widget.attrs.update({"class": "form-control"})


class ProfileUpdateForm(forms.ModelForm):
    """Profile update form for applicants and recruiters."""

    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    profile_picture = forms.URLField(required=False, widget=forms.URLInput(attrs={"class": "form-control"}))
    street_address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    city = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    state = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    country = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    zip_code = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    # 🚗 Commute preferences
    preferred_commute_radius = forms.FloatField(
        required=False,
        label="Preferred Commute Radius (miles)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "100"})
    )

    preferred_commute_mode = forms.ChoiceField(
        required=False,
        label="Preferred Commute Mode",
        choices=Account.COMMUTE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    preferred_commute_time = forms.IntegerField(
        required=False,
        label="Preferred Commute Time (minutes)",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "5", "max": "120"})
    )

    class Meta:
        model = Account
        fields = (
            "email", "phone_number", "profile_picture",
            "street_address", "city", "state", "country", "zip_code",
            "preferred_commute_radius", "preferred_commute_mode", "preferred_commute_time",
        )

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        for fieldname in self.fields:
            self.fields[fieldname].help_text = ""


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with styled Bootstrap fields."""

    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        for fieldname in ["username", "password"]:
            self.fields[fieldname].widget.attrs.update({"class": "form-control"})
