# surveys/admin.py

from django.contrib import admin
from .models import Survey, Question, Choice, Response, Answer, Profile

# --- Inline Admin for Choices and Answers ---

# This allows you to add/edit Choices directly from the Question page
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1 # Show 1 extra empty form for adding a new choice

# This allows you to see the read-only Answers directly from the Response page
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0 # Don't show any extra forms
    readonly_fields = ('question', 'body', 'get_choices') # Make fields read-only
    can_delete = False # Prevent deleting answers from this view

    # Custom method to display ManyToMany choices nicely
    def get_choices(self, obj):
        return ", ".join([c.text for c in obj.choices.all()])
    get_choices.short_description = 'Selected Choices'

# --- Custom Admin Views ---

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'order')
    list_filter = ('survey', 'question_type')
    inlines = [ChoiceInline] # Add the ChoiceInline here

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'survey', 'respondent', 'submitted_at')
    list_filter = ('survey', 'submitted_at')
    inlines = [AnswerInline] # Add the AnswerInline here
    readonly_fields = ('survey', 'respondent', 'submitted_at') # Make the main fields read-only

# --- Simple registrations for other models ---

admin.site.register(Survey)
admin.site.register(Profile)

# Note: We don't need to register Choice or Answer separately
# because they are handled by the inlines.