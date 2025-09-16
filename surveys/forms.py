# surveys/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Survey, Question, Choice

# --- FORMS FOR THE SINGLE-PAGE CREATE VIEW ---

class SurveyCreateForm(forms.ModelForm):
    """Form for the main Survey details used in the new single-page create view."""
    class Meta:
        model = Survey
        fields = ['title', 'description', 'target_audience', 'start_date', 'end_date', 'is_active','is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_audience': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuestionCreateForm(forms.ModelForm):
    """
    Form for a single Question within the creation page.
    Includes a 'choices_text' field to handle choices for choice-based questions.
    """
    choices_text = forms.CharField(
        label="Choices (one per line)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False,
        help_text="Required for single or multiple choice questions. Enter one choice per line."
    )

    class Meta:
        model = Question
        fields = ['text', 'question_type', 'choices_text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-select question-type-select'}),
        }

# --- FORMS FOR YOUR EXISTING UPDATE/DETAIL VIEWS ---

class QuestionForm(forms.ModelForm):
    """
    This is the original form used by your QuestionUpdateView. It does not
    need the choices_text field because that view handles a ChoiceFormSet.
    """
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# This Inline Formset is used by your existing QuestionUpdateView.
ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    fields=('text',),
    extra=1,
    can_delete=True,
    widgets={'text': forms.TextInput(attrs={'class': 'form-control'})}
)