from rest_framework import serializers
from tournament.models import Tournament, TournamentRound, Participant, Result

class TournamentSerializer(serializers.ModelSerializer):
    is_editable = serializers.SerializerMethodField()

    def get_is_editable(self, obj):
        if hasattr(obj, 'editable'):
            return obj.editable
        return True


    class Meta:
        model = Tournament
        fields = '__all__' #['id', 'start_date','name','rated','slug']

    
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
    p1 = ParticipantSerializer(read_only=True)
    p2 = ParticipantSerializer(read_only=True)

    class Meta:
        model = Result
        fields = '__all__'


class ResultDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = '__all__'        



class TournamentSerializer(serializers.ModelSerializer):
    is_editable = serializers.SerializerMethodField()

    def get_is_editable(self, obj):
        if hasattr(obj, 'editable'):
            return obj.editable
        return True


    class Meta:
        model = Tournament
        fields = ['id', 'start_date','name','rated','slug', 'is_editable']

    
