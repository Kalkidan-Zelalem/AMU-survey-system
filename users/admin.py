# users/admin.py - CORRECTED VERSION

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# We will also need the Profile model to show the user's role
from surveys.models import Profile

# This defines an "inline" admin view for the Profile model
# It allows you to edit the Profile directly on the User's admin page
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    """
    This class defines the custom admin interface for our CustomUser model.
    """
    # We add the new inline Profile editor to the user's admin page
    inlines = (ProfileInline,)
    
    # We'll add a new function to display the user type from the Profile model
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff')
    
    list_filter = ('is_staff', 'is_superuser', 'is_active') # 'user_type' removed
    
    # We must remove 'user_type' from the fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        # The 'User Role' section is now handled by the ProfileInline
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_user_type(self, instance):
        # This function fetches the user type from the related Profile
        if hasattr(instance, 'profile'):
            return instance.profile.get_user_type_display()
        return "No Profile"
    
    get_user_type.short_description = 'User Type' # Sets the column header text

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Finally, register our CustomUser model with our custom admin class
admin.site.register(CustomUser, CustomUserAdmin)