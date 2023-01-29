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
        # funnily enough if you use to_jsonb in the outermost query below
        # psycopg2 gives you a string instead of a dic
        query = """select to_json(f) from (
            select tt.*, 	
                (select jsonb_agg(to_jsonb(parties)) 
                from tournament_participant parties where tournament_id = tt.id) participants,
                (select jsonb_agg(to_jsonb(rounds)) 
                from tournament_tournamentround rounds where tournament_id = tt.id) rounds
            from tournament_tournament tt where id = %s 	   
        ) f """

        with connection.cursor() as cursor:
            print(kwargs)
            cursor.execute(query, [kwargs['pk']])
            return Response( cursor.fetchone()[0])


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


