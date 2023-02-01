from django.contrib import admin
from django.contrib.auth.models import User
from tournament.models import Tournament, TournamentRound, Participant, Director


# Register your models here.

class TournamentAdmin(admin.ModelAdmin):
    list_display = ['id','name','num_rounds','entry_mode']

class RoundAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'round_no','spread_cap','pairing_system',
        'repeats','based_on']

class TDAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'user']

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['tournament','name']

admin.site.register(Tournament, TournamentAdmin)    
admin.site.register(TournamentRound, RoundAdmin) 
admin.site.register(Participant,ParticipantAdmin)
admin.site.register(Director,TDAdmin)
