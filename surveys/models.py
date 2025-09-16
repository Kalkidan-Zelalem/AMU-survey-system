
# surveys/models.py
import uuid  # --- ADD THIS IMPORT ---
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Models for the Survey Structure ---

class Survey(models.Model):
    # --- (Your existing fields are preserved) ---
    start_date = models.DateTimeField(null=True, blank=True, help_text="Optional: The survey will become available on this date/time.")
    end_date = models.DateTimeField(null=True, blank=True, help_text="Optional: The survey will close on this date/time.")
    
    class RespondentType(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        FACULITY = 'FACULITY', 'Faculity'
        STAFF = 'STAFF', 'Staff'
        SURVEY_CREATOR = 'SURVEY_CREATOR', 'Survey Creator'
        OTHER = 'OTHER', 'Other Community Member'
        ALL = 'ALL', 'All Respondents'

    title = models.CharField(max_length=200, help_text="The title of the survey.")
    description = models.TextField(blank=True, default='', help_text="A description or instructions for the survey.")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_surveys")
    target_audience = models.CharField(max_length=20, choices=RespondentType.choices, default=RespondentType.ALL, help_text="Choose who is eligible to take this survey.")
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True, help_text="Uncheck this to close the survey to new responses.")

    # --- ADD THESE TWO NEW FIELDS FOR THE SHAREABLE LINK ---
    public_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True,
        help_text="The unique public identifier for the shareable link."
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Enable this to make the survey accessible via the public shareable link."
    )
    # --- END OF NEW FIELDS ---

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('survey-detail', args=[str(self.id)])

    class Meta:
        ordering = ['-created_at']


class Question(models.Model):
    """
    A single question within a survey, with a specific type.
    """
    class QuestionType(models.TextChoices):
        TEXT = 'TEXT', 'Text (Short Answer)'
        TEXTAREA = 'TEXTAREA', 'Paragraph (Long Answer)'
        CHOICE = 'CHOICE', 'Multiple Choice (Single Answer)'
        MULTIPLE_CHOICE = 'MULTICHOICE', 'Checkboxes (Multiple Answers)'
        RATING = 'RATING', 'Rating (1-5)'

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)
    
    # This field allows the creator to choose the question type.
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.TEXT,
        help_text="Choose the type of answer you expect."
    )
    order = models.PositiveIntegerField(default=0, help_text="Determines the order in which questions appear.")

    def __str__(self):
        return f"{self.survey.title} - Q{self.order}: {self.text[:50]}"

    class Meta:
        ordering = ['survey', 'order']


class Choice(models.Model):
    """
    A possible choice for a 'CHOICE' or 'MULTIPLE_CHOICE' question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.question.text[:30]}... - {self.text}"


# --- Models for Storing Responses ---

class Response(models.Model):
    """
    Represents a single, complete submission of a survey by a respondent.
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='survey_responses'
    )
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Response by {self.respondent.username} for '{self.survey.title}'"

    class Meta:
        # This crucial constraint ensures a user can only respond to a survey once.
        unique_together = ('survey', 'respondent')


class Answer(models.Model):
    """
    Stores the answer to a specific question as part of a single response.
    """
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # For TEXT, TEXTAREA, and RATING question types
    body = models.TextField(null=True, blank=True)
    
    # For MULTIPLE_CHOICE question types
    choices = models.ManyToManyField(Choice, related_name='answers', blank=True)

    def __str__(self):
        return f"Answer for Q: '{self.question.text[:30]}...' in Response ID: {self.response.id}"


# --- Profile Model to Extend User ---

class Profile(models.Model):
    """
    Extends the built-in User model to store the respondent's type.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Use the same choices from the Survey model for consistency, but exclude 'ALL'.
    USER_TYPE_CHOICES = [
        choice for choice in Survey.RespondentType.choices if choice[0] != 'ALL'
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        help_text="Select the user's role in the community."
    )

    def __str__(self):
        # get_user_type_display() returns the human-readable label (e.g., "Student")
        return f"{self.user.username}'s Profile - {self.get_user_type_display()}"

# --- Django Signals to Automate Profile Creation ---

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a Profile every time a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the Profile every time the User object is saved.
    """
    # Check for the related 'profile' object before trying to save it.
    if hasattr(instance, 'profile'):
        instance.profile.save()