from django import forms
from .models import Message, SavedSearch, CandidateEmail
from job.models import JobPosting


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
        recipient = kwargs.pop('recipient', None)
        super().__init__(*args, **kwargs)
        
        # Show different jobs based on sender type
        if sender and hasattr(sender, 'recruiter'):
            # For recruiters: show jobs they own
            self.fields['related_job'].queryset = JobPosting.objects.filter(
                owner=sender,
                is_active=True
            )
            self.fields['related_job'].empty_label = "Select a related job (optional)"
        elif sender and hasattr(sender, 'applicant'):
            # For applicants: show all active job postings from the recruiter they're messaging
            if recipient and hasattr(recipient, 'recruiter'):
                # Show all active jobs from this recruiter
                self.fields['related_job'].queryset = JobPosting.objects.filter(
                    owner=recipient,
                    is_active=True
                )
            else:
                # If recipient is not a recruiter, show no jobs
                self.fields['related_job'].queryset = JobPosting.objects.none()
            
            self.fields['related_job'].empty_label = "Select a related job (optional)"
        else:
            # For other users: hide the field
            self.fields['related_job'].queryset = JobPosting.objects.none()
            self.fields['related_job'].widget = forms.HiddenInput()
        
        # Add help text and labels
        self.fields['subject'].label = 'Subject'
        self.fields['body'].label = 'Message'
        self.fields['related_job'].label = 'Related Job'
        self.fields['related_job'].help_text = ''


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


class SavedSearchForm(forms.ModelForm):
    """Form for saving candidate searches"""
    
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter skills separated by commas (e.g., Python, Django, React)'
        })
    )
    
    class Meta:
        model = SavedSearch
        fields = ['name', 'city', 'state', 'country']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a name for this search...',
                'maxlength': 100
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., New York, San Francisco, Austin'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., California, Texas, New York'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., United States, Canada, United Kingdom'
            })
        }
        
    def clean_skills(self):
        skills_text = self.cleaned_data.get('skills', '')
        if skills_text:
            # Convert comma-separated string to list
            skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
            return skills_list
        return []
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        # Convert lists back to comma-separated strings for display
        if instance:
            if instance.skills:
                self.fields['skills'].initial = ', '.join(instance.skills)