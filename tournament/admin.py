from typing import Any
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from tournament.models import Tournament, TournamentRound, Participant, \
        Director, TeamMember, BoardResult, Result
from api.pairing import create_boards, delete_boards

# Register your models here.

class BoardResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'round','team1','team2','board','score1','score2']
    raw_id_fields = ['round', 'team1', 'team2']

class ResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'round','p1','p2','games_won','score1','score2']
    raw_id_fields = ['round', 'p1', 'p2','starting']
    search_fields = ['p1__name', 'p2__name']

    def delete_model(self, request: HttpRequest, obj: Any) -> None:
        super().delete_model(request, obj)
        delete_boards(obj)
        
    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            create_boards(obj.round.tournament, obj)

        return super().save_model(request, obj, form, change)
    
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
    exclude = ['approved_by']
    raw_id_fields = ['tournament','user']

    def save_model(self, request, obj, form, change):
        obj.approved_by = request.user
        obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)
        
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['team','board','name','wins','spread']


admin.site.register(Tournament, TournamentAdmin)    
admin.site.register(TournamentRound, RoundAdmin) 
admin.site.register(Participant,ParticipantAdmin)
admin.site.register(Director,TDAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(BoardResult, BoardResultAdmin)
admin.site.register(Result, ResultAdmin)