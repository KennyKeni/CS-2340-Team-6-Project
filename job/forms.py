from django import forms

class ApplicationNoteForm(forms.Form):
    note = forms.CharField(
        label="Add a note (optional)",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Why you’re a great fit…"})
    )