# forms.py
from django import forms
from .models import JobPosting

class JobPostingForm(forms.ModelForm):
    application_deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],  # matches <input type="datetime-local">
    )

    class Meta:
        model = JobPosting
        fields = [
            "title", "company", "location", "job_type", "description",
            "requirements", "benefits", "salary_min", "salary_max",
            "salary_currency", "application_deadline",
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nice default in the input (still overridable by user)
        if not self.initial.get("salary_currency"):
            self.fields["salary_currency"].initial = "USD"
        # These are optional at the model level; keep the form consistent
        for name in ["requirements", "benefits", "salary_min", "salary_max", "application_deadline"]:
            self.fields[name].required = False

    def clean_salary_currency(self):
        val = (self.cleaned_data.get("salary_currency") or "").strip()
        if not val:
            return "USD"
        return val.upper()[:3]
