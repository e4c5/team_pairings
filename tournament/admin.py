from django.contrib import admin
from django.contrib.auth.models import User
from tournament.models import Tournament, TournamentRound, Participant, \
        Director, TeamMember, BoardResult, Result

# Register your models here.

class BoardResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'round','team1','team2','board','score1','score2']
    raw_id_fields = ['round', 'team1', 'team2']

class ResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'round','p1','p2','games_won','score1','score2']
    raw_id_fields = ['round', 'p1', 'p2','starting']
    
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['id','name','num_rounds','entry_mode']

class RoundAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'round_no','spread_cap','pairing_system',
        'repeats','based_on']
    search_fields = ['tournament__name']

class TDAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'user']

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['pk', 'tournament','name','seed','round_wins','game_wins']
    search_fields = ['tournament__name', 'name']

class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['team','board','name','wins','spread']


admin.site.register(Tournament, TournamentAdmin)    
admin.site.register(TournamentRound, RoundAdmin) 
admin.site.register(Participant,ParticipantAdmin)
admin.site.register(Director,TDAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(BoardResult, BoardResultAdmin)
admin.site.register(Result, ResultAdmin)