from django import forms
from .models import JobPosting


class JobPostingForm(forms.ModelForm):
    """Reusable, readable form recruiters use to create/edit job postings."""

    class Meta:
        model = JobPosting
        fields = [
            "title",
            "summary",
            "responsibilities",
            "salary",
            "work_hours",
            "skills_required",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Role title"}),
            "summary": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Brief summary"}),
            "responsibilities": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "One responsibility per line"}
            ),
            "salary": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., $80k–$100k"}),
            "work_hours": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Full-time, 40hrs/wk"}),
            "skills_required": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "e.g., Python, Django, SQL"}
            ),
        }
