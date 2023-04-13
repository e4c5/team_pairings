import re
import traceback
import json

from django.db import transaction

def tsh_import(f):
    ''' Used for processing the contents of a.t files.
    Method is invoked by the live_data webview. Doesn't save anything
    to the database. Returns a python dictionary
    '''
    players = [{'name': 'bye'}]
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
                        p12 = itms
                    elif obj_name == 'newr':
                        newr = d.strip().split(' ')[1:]

                    elif obj_name == 'rrank':
                        # important change on Nov 29, 2015 - it was decided to always 
                        # use rcrank instead of rrank since rrank was noticed to have 
                        # the wrong information at times example SOY3 2015

                        # Exception will be when the rcrank field has fewer data items
                        # than the rrank field
                        tmp_rank = itms 
                        if not rank:
                            rank = tmp_rank
                        else :
                            if len(tmp_rank) > len(rank):
                                rank = tmp_rank

                    elif obj_name == 'rcrank' and rank == None:
                        rank = [0] + itms
                    elif obj_name == 'off':
                        offed = True
                    

                if rank != None:
                    if opponents and len(rank) > len(opponents) :
                        rank = rank[1:]

                    if not p12:
                        p12 = ['3'] * (len(rank)+1)

                players.append({'name': name, 'opponents' :opponents,'scores':scores,
                    'p12': p12, 'rank': rank,'newr': newr, 'off': offed, 'seed': seed,
                    'old_rating': rating})
                
                if len(scores) > rounds :
                    rounds = len(scores)
                
        if len(players) < 2:
            print('a.t file does not contain any data')
            return {}
        
        return players

if __name__ == '__main__':
    print(tsh_import('tsh/data/tournament1/a.t'))