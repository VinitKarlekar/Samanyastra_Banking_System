from django.contrib import admin
from .models import CustomUser  # Import the User model

# Register the User model with the admin site
@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'email', 'account_number')  # Display user ID and other fields
    search_fields = ('first_name', 'email')  # Enable search by first name and email

# Register your models here.
