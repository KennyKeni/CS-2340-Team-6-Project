from django import forms
from .models import JobPosting


class JobPostingForm(forms.ModelForm):
    """Form for creating/editing job postings."""

    class Meta:
        model = JobPosting
        fields = [
            "title",
            "company",
            "location",
            "job_type",
            "description",
            "requirements",
            "benefits",
            "salary_min",
            "salary_max",
            "salary_currency",
            "application_deadline",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Job Title"}),
            "company": forms.TextInput(attrs={"class": "form-control", "placeholder": "Company Name"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Location"}),
            "job_type": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Job description and summary"}),
            "requirements": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Job requirements"}),
            "benefits": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Benefits and perks"}),
            "salary_min": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Minimum Salary"}),
            "salary_max": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Maximum Salary"}),
            "salary_currency": forms.TextInput(attrs={"class": "form-control", "placeholder": "USD", "maxlength": "3"}),
            "application_deadline": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }