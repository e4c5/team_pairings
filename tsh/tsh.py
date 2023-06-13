import re
from django.db.models import Q
from django.db import transaction

from tournament.models import Result, Participant


def tsh_export(tournament, out):
    """Dumps the given tournament to the file like object.

    Args: tournament: the tournament to export
        out: a file like object
    """
    transaction.set_autocommit(False) 

    # Because TSH relies on line numbers for pairing, once a player is
    # added, she cannot be deleted but merely switched off. Our program
    # being database backed can have players being deleted. which raises
    # problems when exporting. The solution then is to reseed the players
    players = []
    i = 0

    for participant in tournament.participants.order_by('seed'):
        if (participant.seed == 0 or participant.name == 'Bye' 
                or participant.name == 'Absent' or participant.name == ''):
            continue
        participant.seed = i + 1
        participant.save()
        players.append(participant)
        i += 1

    for participant in players:

        opponents = []
        scores = []
        p12 = []
        results = Result.objects.filter( 
            Q(p1=participant) | Q(p2=participant)
        ).order_by('round__round_no')
        
        for result in results:
            if result.p1 == participant:
                opponents.append(str(result.p2.seed))
                scores.append(str(result.score1))
            else:
                opponents.append(str(result.p1.seed))
                scores.append(str(result.score2))

            if result.starting == result.p1:
                p12.append('1')
            elif result.starting == result.p2:
                p12.append('2')
            else:
                p12.append('3')

        print("{0:25s}{1:3d} {2}; {3}; {4}; p12 {5}".format(
            participant.name, participant.rating, " ".join(opponents),
            " ".join(scores),
            "off 0" if participant.offed else "",
            " ".join(p12)
        ), file=out)
    transaction.rollback()


def tsh_import(fp):
    ''' Used for processing the contents of a.t files.
    
    Method is invoked by the live_data webview. Doesn't save anything
    to the database. 

    Args: fp - a file like object
    Returns: Tournament results as an array of dictionaries
    '''
    players = [{'name': 'Bye', 'seed': 0}]
    rounds = 0;


    for seed, line in enumerate(fp):
        if line and len(line) > 30 :
            # print(line)
            rating = re.search('[0-9]{1,4} ', line).group(0).strip()
            name = line[0: line.index(rating)].strip()
            newr = None
            data = line[line.index(rating):]
            data = data.split(';')
            opponents = data[0].strip().split(' ')[1:]
            scores = data[1].strip().split(' ')
            p12 = None
            rank = None

            offed = False
            
            for d in data:
                obj = d.strip().split(' ')
                obj_name = obj[0].strip()
                itms = obj[1:]
                
                if obj_name == 'p12':
                    # A value of 1,2 means the obvious, 0 means the play had a bye
                    # when it's three they tossed for it

                    p12 = itms

                elif obj_name == 'off':
                    offed = True
                
            players.append({'name': name, 'opponents' :opponents,'scores':scores,
                'p12': p12, 'rank': rank,'newr': newr, 'off': offed, 'seed': seed + 1,
                'old_rating': rating})
            
            if len(scores) > rounds :
                rounds = len(scores)
            
    if len(players) < 2:
        print('a.t file does not contain any data')
        return {}
    
    return players

@transaction.atomic
def save_to_db(tournament, results):
    """Save TSH results to DB.
    We use transactions for two reason, because it's a lot faster than auto
    commit and sould the import fail, the old data is preserved.
    Args: tournament: the tournament to import into
          results: results parsed from tsh
    """
    Result.objects.filter(round__tournament=tournament).delete()
    tournament.participants.all().delete()

    # pass one create the database records for the participants.
    rounds = []
    for rnd in tournament.rounds.order_by('round_no'):
        rounds.append(rnd.pk)
        rnd.paired = True
        rnd.save()
        
    participants = []
    for result in results:
        p, _ = Participant.objects.get_or_create(
            name=result['name'],  tournament=tournament,
            defaults={
                "name": result['name'], "offed": result.get('off', False),
                "tournament": tournament
            }
        )
        print(p.id)
        participants.append(p)
        
    # pass 2 save the actual results
    for result in results:
        if result['name'] != 'Bye':
            for idx in range(len(result['opponents'])):
                if idx <= len(result['scores']) -1:
                    score1 = int(result['scores'][idx])
                else:
                    score1 = None
                opponent = int(result['opponents'][idx])
            
                if opponent == 0:
                    score2 = 0
                else:
                    if idx <= len(result['scores']) -1:
                        score2 = int(results[opponent]['scores'][idx])
                    else:
                        score2 = None

                p1 = participants[result['seed']]
                p2 = participants[opponent]

                if p1.id > p2.id:
                    p2, p1 = p1, p2
                    score2, score1 = score1, score2

                if score1 is not None and score2 is not None:
                    if score1 == score2:
                        if opponent == 0:
                            # tsh has this feature where a person can be switched off without
                            # a forfeit. I do not believe this to be a good idea. it can give
                            # someone an undue advantage to be absent for a few rounds and then
                            # comeback later.
                            win = 0
                        else:
                            win = 0.5
                    elif score1 > score2:
                        win = 1
                    else:
                        win = 0

                defaults = {
                    "p1": p1, "p2": p2,
                    "score1" : score1, "score2": score2, 
                    "games_won": win, 
                    "round_id" : rounds[idx]
                }

                if result['p12'][idx] == '1':
                    defaults['starting'] = p1

                print(Result.objects.get_or_create(
                    p1=p1, p2=p2,round_id=rounds[idx],
                    defaults=defaults
                ))

    tournament.update_all_standings()
