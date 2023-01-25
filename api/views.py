import json

from django.shortcuts import render
from django.db import connection

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from tournament import models
from api.serializers import (ParticipantSerializer, TournamentSerializer, 
        TournamentRoundSerializer, ResultSerializer)

def index(request):
    return render(request, 'index.html')

class TournamentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = models.Tournament.objects.all()
    serializer_class = TournamentSerializer

    def retrieve(self, request, *args, **kwargs):
        query = """
       select json_object('id',id, 'start_date', start_date, 'rated', rated,'slug', slug, 'team_size', team_size, 
       'participants', (select json_group_array(
				json_object('id', id, 'name', name, 'played', played, 'game_wins',game_wins,
					'spread', spread, 'position', "position", 'offed', offed, 'seed', 'seed'
				)
			) from tournament_participant tp where tournament_id = %s) 
		,
		'rounds', (select json_group_array(
				json_object('id', id, 'round_no', round_no, 'spread_cap', spread_cap, 'repeats', repeats,
					'based_on', based_on, 'tournament_id', "tournament_id", 'paired', paired, 
					'num_rounds', num_rounds, 'team_size', team_size
				)
			) from tournament_tournamentround tt where tournament_id = %s) 
		)
        from tournament_tournament tt where id = %s
        """

        with connection.cursor() as cursor:
            print(kwargs)
            cursor.execute(query, [kwargs['pk'], kwargs['pk'], kwargs['pk']])
            return Response( json.loads(cursor.fetchone()[0]))


class TournamentRoundViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentRoundSerializer

    @action(detail=True, methods=['post'])
    def pair(self, request, pk=None):
        if models.Result.objects.filter(round=pk).exists():
            return Response({'status': 'error', 'message': 'already pairedd'})
        else:
            pass

    def get_queryset(self):
        return models.TournamentRound.objects.filter(tournament_id = self.kwargs['tid'])
        

class ParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ParticipantSerializer

    def perform_create(self, serializer):
        serializer.save(tournament_id=self.kwargs['tid'])

    def get_queryset(self):
        return models.Participant.objects.filter(
            tournament_id = self.kwargs['tid']).order_by('-round_wins','-game_wins','-spread')


class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ResultSerializer
    def get_queryset(self):
        return models.Result.objects.filter(round_id = self.kwargs['rid'])


