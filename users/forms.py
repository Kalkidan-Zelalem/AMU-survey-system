# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from surveys.models import Profile # <-- IMPORTANT: Import the Profile model

# Get the CustomUser model you are using
CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    # This is the improved way: Get choices directly from the Profile model.
    # We are no longer hard-coding the choices here.
    user_type = forms.ChoiceField(
        label="Your Role",
        choices=Profile.USER_TYPE_CHOICES, # <-- Gets the list from the "Single Source of Truth"
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # The fields the user will fill out on the registration form.
        fields = ('username', 'first_name', 'last_name', 'email', 'user_type')

    # This save method is not strictly necessary if your view handles it,
    # but it's a good practice to keep the logic bundled with the form.
    # If your view is already saving the profile, this won't break anything.
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # The post_save signal has already created a profile.
            # Now, we update that profile with the user_type from the form.
            if hasattr(user, 'profile'):
                user.profile.user_type = self.cleaned_data.get('user_type')
                user.profile.save()
        return user