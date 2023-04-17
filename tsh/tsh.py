import re
from django.db.models import Q
from tournament.models import Result

def tsh_export(tournament, out):
    """Dumps the given tournament to the file like object
    Args: tournament: the tournament to export
        out: a file like object
    """
    for participant in tournament.participants.order_by('seed'):
        if (participant.seed == 0 or participant.name == 'Bye' 
                or participant.name == 'Absent' or participant.name == ''):
            continue

        opponents = []
        scores = []
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

        print("{0:25s}{1:3d} {2}; {3}; {4}".format(
            participant.name, participant.rating, " ".join(opponents),
            " ".join(scores),
            "off 0;" if participant.offed else ""
        ), file=out)


def tsh_import(f):
    ''' Used for processing the contents of a.t files.
    Method is invoked by the live_data webview. Doesn't save anything
    to the database. Returns a python dictionary
    '''
    players = [{'name': 'Bye', 'seed': 0}]
    rounds = 0;

    with open(f) as fp:
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

if __name__ == '__main__':
    print(tsh_import('tsh/data/tournament1/a.t'))