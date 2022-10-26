from pyexpat import model
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from tournament import models
from api.serializers import (ParticipantSerializer, TournamentSerializer, 
        TournamentRoundSerializer, ResultSerializer)
import tournament

# Create your views here.

def index(request):
    return render(request, 'index.html')

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = models.Tournament.objects.all()
    serializer_class = TournamentSerializer

    def retrieve(self, request, *args, **kwargs):
        print('here')
        instance = self.get_object()
        instance.editable = instance.rounds.filter(paired=True).count() == 0
        serializer = self.get_serializer(instance)
        return Response(serializer.data)



class TournamentRoundViewSet(viewsets.ModelViewSet):
    queryset = models.TournamentRound.objects.all()
    serializer_class = TournamentRoundSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        return models.Participant.objects.filter(tournament_id = self.kwargs['tid'])
        

class ResultViewSet(viewsets.ModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = ResultSerializer


