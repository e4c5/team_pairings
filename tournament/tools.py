import csv
from faker import Faker

from tournament.models import Participant, TeamMember, Tournament, BoardResult
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
        if participant.team_members.count() == tournament.team_size:
            for tm in participant.team_members.all():
                if tm.name == '':
                    tm.name = fake.name()
                    tm.save()
        else:                    
            for i in range(tournament.team_size):
                TeamMember.objects.create(team=participant, board=i+1,
                    name=fake.name(), wins=0, spread=0)


def random_results(tournament):
    """All pending results in will be filled randomly"""
    rnd = tournament.rounds.filter(paired=True).order_by('-round_no')[0]
    fake = Faker()
    for result in rnd.results.select_related('p1','p2').all():
        if tournament.entry_mode == Tournament.BY_PLAYER:
            # results entered per each player
            mid = tournament.team_size // 2
            if result.p2.name == 'Bye':
                # player 1 got a bye
                for i in range(tournament.team_size):
                    if i <= mid:
                        BoardResult.objects.create(
                            round=rnd, board=i+1,
                            score1=100, score2=0,
                            team1=result.p1, team2=result.p2
                        )
                    else:
                        BoardResult.objects.create(
                            round=rnd, board=i+1,
                            score1=0, score2=1,
                            team1=result.p1, team2=result.p2
                        )   
            elif result.p1.name == 'Bye':
                # player 2 got a bye
                for i in range(tournament.team_size):
                    if i <= mid:
                        BoardResult.objects.create(
                            round=rnd, board=i+1,
                            score1=100, score2=0,
                            team1=result.p2, team2=result.p1
                        )
                    else:
                        BoardResult.objects.create(
                            round=rnd, board=i+1,
                            score1=0, score2=1,
                            team1=result.p2, team2=result.p1
                        ) 
            else:
                for i in range(tournament.team_size):
                    score1=fake.random_int(290, 550)
                    score2=fake.random_int(290, 550)
                    BoardResult.objects.get_or_create(
                        round=rnd, board=i+1,
                        team1=result.p2, team2=result.p1,
                        defaults={'score1': score1, 'score2': score2}
                    )

        else:
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
