import csv
from faker import Faker
import json
import requests

from django.db.models import Q

from tournament.models import Participant, TeamMember, Tournament, BoardResult
from tournament.models import update_standing, update_team_standing


def add_woogle_participants(tournament, filename):
    """Add participents for a woogles online tournament. The file is expected to be 
    a list of woogles usernames. We will fetch the user's ratings from the woogles 
    profile and then add them to the tournament"""

    with open(filename) as fp:
        for line in fp:
            line = line.strip()
            response = requests.post('https://woogles.io/twirp/user_service.ProfileService/GetProfile',
                        json={'username': line})    
            
            if response.status_code == 200:
                data = response.json()
                ratings = json.loads(data['ratings_json'])
                try:
                    print(",".join([line, str(int(ratings['Data']['CSW19.classic.regular']['r']))]))
                except KeyError:
                    print(",".join([line, "0"]))
            else:
                print(line)


def add_participants(tournament, use_faker=False, count=0, filename="", seed=None):
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
    participants = []
    if use_faker:
        fake = Faker()
        if seed:
            Faker.seed(seed)
        for i in range(count):
            if tournament.team_size:
                p = Participant.objects.create(tournament=tournament, 
                    name = fake.city() + " Scrabble Club",
                    approval='V',
                    rating = i * 10 + 1)
            else:
                p = Participant.objects.create(tournament=tournament, 
                    name = fake.name(), approval='V',
                    rating = fake.random_int(500, 1400))
                
            participants.append(p)
    else:
        with open(filename) as fp:
            reader = csv.reader(fp)
            for line in reader:
                try:
                    p = Participant.objects.create(tournament=tournament, name=line[0],
                        rating=int(line[1]), approval='V')
                    participants.append(p)
                except IndexError:
                    pass
    return participants


def add_team_members(tournament):
    """Adds members to a team.
    Faker is used to produce the data"""
    fake = Faker()

    for participant in tournament.participants.all():
        for i in range(tournament.team_size):
            TeamMember.objects.create(team=participant, board=i+1,
                name=fake.name(), wins=0, spread=0)


def random_results(tournament):
    """All pending results in will be filled randomly.
    Args: tournament : the tournament for which results need to be added
    Returns: the round for which results were added
    """
    rnd = tournament.rounds.filter(paired=True).order_by('-round_no')[0]
    fake = Faker()
    for result in rnd.results.select_related('p1','p2').all():
        if tournament.entry_mode == Tournament.NON_TEAM:
            # this is not a team tournament
            if not result.score1 and not result.score2:
                result.score1 = fake.random_int(290, 550)
                result.score2 = fake.random_int(290, 550)
                if result.score1 == result.score2:
                    result.games_won = 0.5
                if result.score1 > result.score2:
                    result.games_won = 1
                else:
                    result.games_won = 0

                result.save()

        elif tournament.entry_mode == Tournament.BY_PLAYER:
            # results entered per each player
            mid = tournament.team_size // 2
            if not result.score1 and not result.score2:
                for i in range(tournament.team_size):
                    b = BoardResult.objects.get(
                        Q(round=rnd) & Q(team1=result.p1) & Q(team2=result.p2) & Q(board=i+1)
                    )
                    if b.score1 is None:
                        b.score1 = fake.random_int(290, 550)
                        b.score2 = fake.random_int(290, 550)
                        b.save()
                # no need to save result here. Post save event for BoardResult
                # takes care of that
        else:
            if not result.score1 and not result.score2:
                result.score1 = fake.random_int(900, 2500)
                result.score2 = fake.random_int(900, 2500)
                result.games_won = fake.random_int(0, 5)
                if result.games_won > 2:
                    if result.score1 < result.score2:
                        result.score1, result.score2 = result.score2, result.score1

                result.save()
    return rnd

def truncate_rounds(tournament, number):
    """Truncate the tournament
    Args: number : the last round to remain standing
        send 0 here to truncate all the results and pairings"""

    for round in tournament.rounds.filter(round_no__gt=number):
        round.results.all().delete()
        round.boardresult_set.all().delete()
        round.paired = 0;
        round.save()

    for p in tournament.participants.all():
        if tournament.team_size:
            update_team_standing(p.id)
        else:
            update_standing(p.id)
