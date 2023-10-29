from django.contrib import admin
from profiles.models import Profile


class ProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'national_list_name', 'wespa_list_name', 'gender','date_of_birth',
                     'preferred_name', 'beginner', 'organization', 'full_name')
    list_editable = ('preferred_name',)
    search_fields = ['full_name', 'preferred_name']


admin.site.register(Profile, ProfileAdmin)
 