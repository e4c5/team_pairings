from rest_framework import serializers
from tournament.models import Tournament, TournamentRound, Participant,\
     Result, BoardResult

class TournamentRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentRound
        fields = '__all__'

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = [
            'id',
            'name', 'played','game_wins','round_wins','spread',
            'offed','rating'
        ]
    

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['score1','score2','games_won', 'p1', 'p2']

class TournamentSerializer(serializers.ModelSerializer):
    is_editable = serializers.SerializerMethodField()
    private = serializers.BooleanField(required=False, default=True)

    def get_is_editable(self, obj):
        if hasattr(obj, 'editable'):
            return obj.editable
        return True

    class Meta:
        model = Tournament
        fields = ['id', 'start_date','name','rated','slug', 'entry_mode',
                   'is_editable', 'num_rounds', 'private', 'team_size']

    
class BoardResultSerializer(serializers.Serializer):
    score1 = serializers.IntegerField()
    score2 = serializers.IntegerField()
    p1 = serializers.IntegerField(required=False)
    p2 = serializers.IntegerField(required=False)

