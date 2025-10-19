from django import forms
from .models import CandidateEmail
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