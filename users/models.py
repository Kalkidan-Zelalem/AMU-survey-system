
# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # The user_type field that was here should be REMOVED.
    # We will use the Profile model in surveys/models.py instead.
    pass # You can leave it as pass or add other fields later.