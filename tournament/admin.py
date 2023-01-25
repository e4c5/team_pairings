from django.contrib import admin
from tournament.models import Tournament, TournamentRound

# Register your models here.

class TournamentAdmin(admin.ModelAdmin):
    list_display = ['id','name']

class RoundAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'round_no','spread_cap','pairing_system',
        'repeats','based_on']

admin.site.register(Tournament, TournamentAdmin)    
admin.site.register(TournamentRound, RoundAdmin)
