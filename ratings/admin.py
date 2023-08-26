from django.contrib import admin
from ratings.models import WespaRating, NationalRating, Unrated

class WespaAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'rating', 'last')
    search_fields = ('name',)

class NationalAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'rating', 'last')
    search_fields = ('name',)

admin.site.register(WespaRating, WespaAdmin)
admin.site.register(NationalRating, NationalAdmin)
admin.site.register(Unrated)