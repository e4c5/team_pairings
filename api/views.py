import json
from asgiref.sync import async_to_sync

from django.shortcuts import render
from django.db import connection
from django.db.models import Q
from channels.layers import get_channel_layer

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tournament import models
from api.serializers import (ParticipantSerializer, TournamentSerializer, 
        TournamentRoundSerializer, ResultSerializer)
from api.swiss import SwissPairing
from api.permissions import IsAuthenticatedOrReadOnly

"""
The author is fully aware of the django ORM and the django DRF
however for most task, it's actually a lot easier and the performance
is a lot better to simply use the postgresql json / jsonb functions
"""
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
    def truncate(self, request, tid, pk=None):
        """Deletes the last round of a tournament.
        A very dangerous operation. To avoid accidental truncation, the TD is 
        supposed to send this username as a post data item.
        """
        rnd = models.TournamentRound.objects.get(pk=pk)
        if rnd.paired:
            # find out if the round after this one is already paired.
            after = models.TournamentRound.objects.filter(
                Q(round_no__gt=rnd.round_no) & Q(tournament=rnd.tournament) & 
                Q(paired=True) 
            )
            if after.exists():
                return Response(
                    {'status': 'error', 'message': 'next round already paired'}
                )    

            td = models.Director.objects.filter(
                Q(tournament_id=tid) & Q(user=request.user))
            if td.exists():
                if request.data.get('td') == request.user.username:
                    models.BoardResult.objects.filter(round=rnd).delete()
                    models.Result.objects.filter(round=rnd).delete()
                    self.unpair_helper(rnd)
                    return Response({'status': 'ok'})
                else:
                    return Response({'status': 'error', 'message': 'confirmation code needed'})
            else:
                return Response(
                    {'status': 'error', 'message': 'not a director'}
                )    

        else:
            return Response({'status': 'error', 'message': 'round not paired'})


    @action(detail=True, methods=['post'])
    def pair(self, request, tid, pk=None):
        """Pairs the given round.
        Possible only if there is at least 2 players in this tournament and
        has not been paired already."""
        if models.Result.objects.filter(round=pk).exists():
            return Response({'status': 'error', 'message': 'already paired'})

        rnd = models.TournamentRound.objects.get(pk=pk)
        count = rnd.tournament.participants.count()
        if count < 2:
            return Response({'status': 'error',
                 'message': 'A tournament needs at least two player'})
        p = SwissPairing(rnd)
        p.make_it()
        results = p.save()
        res_serializer = ResultSerializer(results, many=True)
        rnd_serializer = TournamentRoundSerializer(rnd)

        rnd.paired = True
        rnd.save()

        broadcast({
                    "round": rnd_serializer.data,
                    "results": res_serializer.data,
                    "participants": get_participants(tid),
                    "tournament_id": tid
                }
        )
        return Response({'status': 'ok'})


    def unpair_helper(self, rnd):
        rnd.paired = False
        rnd.save()
        rnd_serializer = TournamentRoundSerializer(rnd)
        
        broadcast({
                    "round": rnd_serializer.data,
                    "results": [],
                    "participants": get_participants(rnd.tournament_id),
                    "tournament_id": rnd.tournament_id
                }
        )

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
            self.unpair_helper(rnd)
            return Response({"status": "ok"})

        else:
            return Response({"status": "error", "message": "Not paired"})

    def get_queryset(self):
        return models.TournamentRound.objects.filter(tournament_id = self.kwargs['tid'])
        

def get_participant(pk):
    """Fetch information about a single participant.
    includes participants overall result, list of team members, the results of
    each round and finally the results of each team member as well.
    """
    query = """select json_agg(f) from (
                    select tp.*, 
                        (select jsonb_agg(to_jsonb(tm)) from tournament_teammember tm
                        where team_id = tp.id) members,
                        (select jsonb_agg(to_jsonb(tr)) from tournament_result tr
                        where p1_id = tp.id or p2_id = tp.id) results
                    from tournament_participant tp where tp.id = %s
                ) f	 """

    with connection.cursor() as cursor:
        cursor.execute(query, [pk])
        return cursor.fetchone()[0][0]


def get_participants(tid):
    '''Fetch list of participants.
    includes the results of each round for those participants and also the
    team member details.
    '''
    query = """select json_agg(f) from (
                    select tp.*, 
                        (select jsonb_agg(to_jsonb(tm)) from tournament_teammember tm
                        where team_id = tp.id) members,
                        (select jsonb_agg(to_jsonb(tr)) from tournament_result tr
                        where p1_id = tp.id or p2_id = tp.id) results
                    from tournament_participant tp where tp.tournament_id = %s
                ) f	 """

    with connection.cursor() as cursor:
        cursor.execute(query, [tid])
        return cursor.fetchone()[0]


class ParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ParticipantSerializer

    def perform_create(self, serializer):
        serializer.save(tournament_id=self.kwargs['tid'])
        broadcast({"participant": serializer.data})

    def retrieve(self, request, pk=None, **kwargs):
        return Response(get_participant(pk))

    def get_queryset(self):
        return models.Participant.objects.filter(
            tournament_id = self.kwargs['tid']).order_by('-round_wins','-game_wins','-spread')

def get_results(round_id):
    query = """select json_agg(to_jsonb(tr)) 
                from tournament_result tr where round_id = %s"""

    with connection.cursor() as cursor:
        cursor.execute(query, [round_id])
        return cursor.fetchone()[0]


class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ResultSerializer


    def update(self, request, *args, **kwargs):
        result = super().update(request, *args, **kwargs)
        rnd = models.TournamentRound.objects.get(pk=kwargs['rid'])

        broadcast({
                    "participants": get_participants(kwargs['tid']),
                    "tournament_id": kwargs['tid'],
                    "results": get_results(kwargs['rid']),
                    "round": TournamentRoundSerializer(rnd).data
                }
        )

        return result

    def get_queryset(self):
        return models.Result.objects.filter(round_id = self.kwargs['rid'])


def broadcast(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat",
        {
            "type": "chat.message",
            "message": message
        },
    )
