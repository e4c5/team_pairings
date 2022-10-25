from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from tournament import models
from api.serializers import (ParticipantSerializer, TournamentSerializer, 
        TournamentRoundSerializer, ResultSerializer)

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
    queryset = models.Participant.objects.all()
    serializer_class = ParticipantSerializer

class ResultViewSet(viewsets.ModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = ResultSerializer


