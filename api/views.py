import json
from asgiref.sync import async_to_sync

from django.shortcuts import render
from django.db import connection
from channels.layers import get_channel_layer

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tournament import models
from api.serializers import (ParticipantSerializer, TournamentSerializer, 
        TournamentRoundSerializer, ResultSerializer)
from api.swiss import SwissPairing
from api.permissions import IsAuthenticatedOrReadOnly


def index(request):
    return render(request, 'index.html')


class TournamentViewSet(viewsets.ModelViewSet):
    """CRUD for tournaments"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = models.Tournament.objects.all()
    serializer_class = TournamentSerializer

    def retrieve(self, request, *args, **kwargs):
        # funnily enough if you use to_jsonb in the outermost query below
        # psycopg2 gives you a string instead of a dict
        query = """select to_json(f) from (
            select tt.*, 	
                (select jsonb_agg(to_jsonb(parties)) 
                    FROM (
                        select rank() over(order by round_wins desc, game_wins desc, spread desc, rating desc) as "pos", * 
                        from tournament_participant parties 
                            where tournament_id = tt.id and name != 'Bye'
                    ) parties
                ) participants,
                (select jsonb_agg(to_jsonb(r)) FROM (
                    SELECT * from tournament_tournamentround rounds 
                        where tournament_id = tt.id order by round_no
                    ) r
                ) rounds
            from tournament_tournament tt where id = %s 	   
        ) f """

        with connection.cursor() as cursor:
            cursor.execute(query, [kwargs['pk']])
            return Response( cursor.fetchone()[0])


class TournamentRoundViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = TournamentRoundSerializer


    @action(detail=True, methods=['post'])
    def pair(self, request, tid, pk=None):
        """Pairs the given round.
        Possible only if there is at least 2 players in this tournament and
        has not been paired already."""
        if models.Result.objects.filter(round=pk).exists():
            return Response({'status': 'error', 'message': 'already pairedd'})

        rnd = models.TournamentRound.objects.get(pk=pk)
        count = rnd.tournament.participants.count()
        if count < 2:
            return Response({'status': 'error',
                 'message': 'A tournament needs at least two player'})
        p = SwissPairing(rnd)
        p.make_it()
        results = p.save()
        serializer = ResultSerializer(results, many=True)
        rnd.paired = True
        rnd.save()
        return Response({'status': 'ok', 
            'results': serializer.data})


    @action(detail=True, methods=['post'])
    def unpair(self, request, tid, pk=None):
        """Unpair a round if it does not have any results"""
        rnd = models.TournamentRound.objects.get(pk=pk)
        if rnd.paired:
            qs = models.Result.objects.filter(round=rnd)
            if qs.exclude(score1=None).exists():
                return Response({"status": "error", 
                    "message": "This round already has results. Delete them first"})
            
            qs.delete()
            rnd.paired = False
            rnd.save()
            return Response({"status": "ok"})

        else:
            return Response({"status": "error", "message": "Not paired"})

    def get_queryset(self):
        return models.TournamentRound.objects.filter(tournament_id = self.kwargs['tid'])
        

def get_participants(tid):
    ''''Retrieve all information about participant'''
    query = """select to_json(f) from (
                    select tp.*, 
                        (select jsonb_agg(to_jsonb(tm)) from tournament_teammember tm
                        where team_id = tp.id) members,
                        (select jsonb_agg(to_jsonb(tr)) from tournament_result tr
                        where p1_id = tp.id or p2_id = tp.id) results
                    from tournament_participant tp where tp.id = %s
                ) f	 """

    with connection.cursor() as cursor:
        cursor.execute(query, [tid])
        return cursor.fetchone()[0]


class ParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ParticipantSerializer

    def retrieve(self, request, *args, **kwargs):
        ''''Retrieve all information about participant'''
        return Response(get_participants(kwargs['pk']))

    def perform_create(self, serializer):
        serializer.save(tournament_id=self.kwargs['tid'])
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "chat",
            {
                "type": "chat.message",
                "message": {"type": "participant", "body": serializer.data}
            },
        )


    def get_queryset(self):
        return models.Participant.objects.filter(
            tournament_id = self.kwargs['tid']).order_by('-round_wins','-game_wins','-spread')


class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ResultSerializer


    def update(self, request, *args, **kwargs):
        result = super().update(request, *args, **kwargs)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "chat",
            {
                "type": "chat.message",
                "message": {"type": "participants",
                    "tournament_id": kwargs['tid'],
                    "body": get_participants(kwargs['tid'])}
            },
        )

        return result

    def get_queryset(self):
        return models.Result.objects.filter(round_id = self.kwargs['rid'])


