from django.contrib import admin
from profiles.models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('national_list_name', 'wespa_list_name', 'preferred_name', 'beginner')
    
admin.site.register(Profile, ProfileAdmin)
 