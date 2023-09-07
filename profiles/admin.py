from django.contrib import admin
from profiles.models import Profile


class ProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'national_list_name', 'wespa_list_name',
                     'preferred_name', 'beginner', 'organization', 'full_name')
    
    search_fields = ['full_name', 'preferred_name']


admin.site.register(Profile, ProfileAdmin)
 