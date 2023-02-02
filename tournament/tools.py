import csv
from faker import Faker

from tournament.models import Participant, TeamMember, TournamentRound
from tournament.models import update_standing

def add_participants(tournament, use_faker=False, count=0, filename=""):
    """Adds a list of participants (teams) to a tournament
    Args: tournament: the tournament we are filling up
        use_faker: use faker library to come up with the names. If false
            data will be read from a file provided through filename
        count: number of entries to add
        filename: the name of the file to read data from, whill be used
            only when faker is false

    when using faker the ratings will always increase from the first added
    record to the last
    """
    if use_faker:
        fake = Faker()
        for i in range(count):
            Participant.objects.create(tournament=tournament, 
                name = fake.city() + " Scrabble Club",
                rating = i * 10 + 1)

    else:
        with open(filename) as fp:
            reader = csv.reader(fp)

            for line in reader:
                Participant.objects.create(tournament=tournament, name=line[0],
                    rating=line[1])


def add_team_members(tournament):
    """Adds members to a team.
    Faker is used to produce the data"""
    fake = Faker()

    for participant in tournament.participants.all():
        for i in range(tournament.team_size):
            TeamMember.objects.create(team=participant, board=i+1,
                name=fake.name(), wins=0, spread=0)


def random_results(tournament):
    """All pending results in will be filled randomly"""
    rnd = TournamentRound.objects.filter(paired=True).order_by('-round_no')[0]
    fake = Faker()
    for result in rnd.results.all():
        if result.p1.name == 'Bye':
            result.score1 = 0
            result.games_won =2
            result.score2 = 300
        elif result.p2.name == 'Bye':
            result.score2 = 0
            result.games_won =3
            result.score1 = 300
        else:
            result.score1 = fake.random_int(900, 2500)
            result.score2 = fake.random_int(900, 2500)
            result.games_won = fake.random_int(0, 5)
            if result.games_won > 2:
                if result.score1 < result.score2:
                    result.score1, result.score2 = result.score2, result.score1

        result.save()


def truncate_rounds(tournament, number):
    """Truncate the tournament
    Args: number : the last round to remain standing
        send 0 here to truncate all the results and pairings"""

    for round in tournament.rounds.filter(round_no__gt=number):
        round.results.all().delete()
        round.paired = 0;
        round.save()

    for p in tournament.participants.all():
        update_standing(p.id)
