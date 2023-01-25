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
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    first = ParticipantSerializer(read_only=True)
    second = ParticipantSerializer(read_only=True)

    class Meta:
        model = Result
        fields = '__all__'


class ResultDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = '__all__'        


