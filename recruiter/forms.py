from django import forms
from .models import CandidateEmail, Message, SavedSearch
from job.models import JobPosting


class CandidateEmailForm(forms.ModelForm):
    """Form for recruiters to send emails to candidates"""
    
    class Meta:
        model = CandidateEmail
        fields = ['subject', 'body', 'related_job']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email subject...',
                'maxlength': 500
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your message to the candidate...'
            }),
            'related_job': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        
    def __init__(self, *args, **kwargs):
        recruiter = kwargs.pop('recruiter', None)
        super().__init__(*args, **kwargs)
        
        # Only show jobs owned by the current recruiter
        if recruiter:
            self.fields['related_job'].queryset = JobPosting.objects.filter(
                owner=recruiter.account,
                is_active=True
            )
            self.fields['related_job'].empty_label = "Select a related job (optional)"
        
        # Add help text and labels
        self.fields['subject'].label = 'Email Subject'
        self.fields['body'].label = 'Message'
        self.fields['related_job'].label = 'Related Job Posting'
        self.fields['related_job'].help_text = 'Optional: Associate this email with one of your job postings'


class MessageForm(forms.ModelForm):
    """Form for direct messaging between recruiters and candidates"""
    
    class Meta:
        model = Message
        fields = ['subject', 'body', 'related_job']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter message subject...',
                'maxlength': 200
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write your message...'
            }),
            'related_job': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        
    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        
        # Only show jobs owned by the current sender if they're a recruiter
        if sender and hasattr(sender, 'recruiter'):
            self.fields['related_job'].queryset = JobPosting.objects.filter(
                owner=sender,
                is_active=True
            )
            self.fields['related_job'].empty_label = "Select a related job (optional)"
        else:
            self.fields['related_job'].queryset = JobPosting.objects.none()
            self.fields['related_job'].widget = forms.HiddenInput()
        
        # Add help text and labels
        self.fields['subject'].label = 'Subject'
        self.fields['body'].label = 'Message'
        self.fields['related_job'].label = 'Related Job'
        self.fields['related_job'].help_text = ''


class SavedSearchForm(forms.ModelForm):
    """Form for saving candidate searches"""
    
    # Override the JSONField fields as CharFields for easier input
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter skills separated by commas (e.g., Python, Django, React)'
        })
    )
    
    job_types = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter job types separated by commas (e.g., full-time, remote, contract)'
        })
    )
    
    class Meta:
        model = SavedSearch
        fields = ['name', 'location', 'min_experience', 'max_experience', 
                 'education_level', 'salary_min', 'salary_max']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a name for this search...',
                'maxlength': 100
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., New York, NY or Remote'
            }),
            'min_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Minimum years of experience'
            }),
            'max_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Maximum years of experience'
            }),
            'education_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor\'s, Master\'s, PhD'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1000,
                'placeholder': 'Minimum salary'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1000,
                'placeholder': 'Maximum salary'
            })
        }
        
    def clean_skills(self):
        skills_text = self.cleaned_data.get('skills', '')
        if skills_text:
            # Convert comma-separated string to list
            skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
            return skills_list
        return []
    
    def clean_job_types(self):
        job_types_text = self.cleaned_data.get('job_types', '')
        if job_types_text:
            # Convert comma-separated string to list
            job_types_list = [job_type.strip() for job_type in job_types_text.split(',') if job_type.strip()]
            return job_types_list
        return []
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        # Convert lists back to comma-separated strings for display
        if instance:
            if instance.skills:
                self.fields['skills'].initial = ', '.join(instance.skills)
            if instance.job_types:
                self.fields['job_types'].initial = ', '.join(instance.job_types)
    
    def clean(self):
        cleaned_data = super().clean()
        min_experience = cleaned_data.get('min_experience')
        max_experience = cleaned_data.get('max_experience')
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if min_experience and max_experience and min_experience > max_experience:
            raise forms.ValidationError("Minimum experience cannot be greater than maximum experience.")
        
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError("Minimum salary cannot be greater than maximum salary.")
        
        return cleaned_data