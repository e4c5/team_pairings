import csv
from tournament.models import Participant

def add_players(filename, tournament):
    with open(filename) as fp:
        reader = csv.reader(fp)

        for line in reader:
            Participant.objects.create(tournament=tournament, name=line[0],
                seed=line[1])
