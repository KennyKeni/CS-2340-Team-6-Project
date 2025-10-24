# forms.py
from django import forms
from .models import JobPosting

class JobPostingForm(forms.ModelForm):
    application_deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],  # matches <input type="datetime-local">
    )

    required_skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 2,
            "placeholder": "Enter required skills (comma-separated, e.g., Python, Django, React)"
        }),
        help_text="Comma-separated list of required skills"
    )

    preferred_skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 2,
            "placeholder": "Enter preferred skills (comma-separated, e.g., Docker, AWS)"
        }),
        help_text="Comma-separated list of preferred skills"
    )

    class Meta:
        model = JobPosting
        fields = [
            "title", "company", "street_address", "city", "state",
            "zip_code", "country", "job_type", "description",
            "requirements", "benefits", "salary_min", "salary_max",
            "salary_currency", "application_deadline",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Job Title"}),
            "company": forms.TextInput(attrs={"class": "form-control", "placeholder": "Company Name"}),
            "street_address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Street Address"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "State/Province"}),
            "zip_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "ZIP/Postal Code"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Country"}),
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
        if not self.initial.get("country"):
            self.fields["country"].initial = "USA"
        # These are optional at the model level; keep the form consistent
        for name in ["requirements", "benefits", "salary_min", "salary_max", "application_deadline"]:
            self.fields[name].required = False

        # Make address fields required for accurate geocoding
        for name in ["street_address", "city", "state", "zip_code"]:
            self.fields[name].required = True

        # Populate skills fields from existing JobSkill instances if editing
        if self.instance and self.instance.pk:
            from .models import JobSkill
            required_skills = JobSkill.objects.filter(
                job=self.instance,
                importance_level='required'
            ).values_list('skill_name', flat=True)
            preferred_skills = JobSkill.objects.filter(
                job=self.instance,
                importance_level='preferred'
            ).values_list('skill_name', flat=True)

            if required_skills:
                self.fields['required_skills'].initial = ', '.join(required_skills)
            if preferred_skills:
                self.fields['preferred_skills'].initial = ', '.join(preferred_skills)

    def clean_salary_currency(self):
        val = (self.cleaned_data.get("salary_currency") or "").strip()
        if not val:
            return "USD"
        return val.upper()[:3]

    def clean_required_skills(self):
        skills_str = self.cleaned_data.get('required_skills', '').strip()
        if not skills_str:
            return []
        return [s.strip() for s in skills_str.split(',') if s.strip()]

    def clean_preferred_skills(self):
        skills_str = self.cleaned_data.get('preferred_skills', '').strip()
        if not skills_str:
            return []
        return [s.strip() for s in skills_str.split(',') if s.strip()]

    def save_skills(self, job):
        from .models import JobSkill

        JobSkill.objects.filter(job=job).delete()

        required_skills = self.cleaned_data.get('required_skills', [])
        for skill_name in required_skills:
            JobSkill.objects.create(
                job=job,
                skill_name=skill_name,
                importance_level='required'
            )

        preferred_skills = self.cleaned_data.get('preferred_skills', [])
        for skill_name in preferred_skills:
            JobSkill.objects.create(
                job=job,
                skill_name=skill_name,
                importance_level='preferred'
            )
