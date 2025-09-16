
# users/views.py

from django.shortcuts import render, redirect
# from django.views import generic  <- This import is not used, it's safe to remove.
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib import messages # Import the messages framework for user feedback

# A view for the home page (Unchanged, as requested)
def home(request):
    return render(request, 'home.html')

# A view for the registration page (FIXED)
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # This line saves the new user and fires the signal that creates their empty profile.
            user = form.save()

            # --- THIS IS THE FIX ---
            # 1. Get the chosen role from the validated form data.
            user_type_from_form = form.cleaned_data.get('user_type')

            # 2. Update the user's profile with this role.
            #    The 'user.profile' object exists because of the signal you created.
            #    This check is extra safe.
            if hasattr(user, 'profile'):
                user.profile.user_type = user_type_from_form
                user.profile.save()
            # --- END OF FIX ---

            login(request, user)  # Log the user in immediately (Your feature is preserved)
            
            # It's good practice to give the user feedback.
            messages.success(request, f"Welcome, {user.username}! Your account has been created successfully.")
            
            return redirect('home')  # Redirect to the home page (Your feature is preserved)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})