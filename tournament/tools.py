import csv
from faker import Faker

from tournament.models import Participant, TeamMember

def add_participants(tournament, use_faker=False, count=0, filename=""):
    if use_faker:
        fake = Faker()
        for _ in range(count):
            Participant.objects.create(tournament=tournament, 
                name=fake.city() + " Scrabble Club",
                seed=fake.random_int(0, 1000))

    else:
        with open(filename) as fp:
            reader = csv.reader(fp)

            for line in reader:
                Participant.objects.create(tournament=tournament, name=line[0],
                    seed=line[1])


def add_team_members(tournament):
    fake = Faker()

    for participant in tournament.participants.all():
        for i in range(tournament.team_size):
            TeamMember.objects.create(team=participant, board=i+1,
                name=fake.name(), wins=0, spread=0)
