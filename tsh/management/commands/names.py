import pandas as pd

from django.core.management.base import BaseCommand
from tournament.models import Tournament, Participant, Result
from tsh import tsh
from profiles.models import Profile


class Command(BaseCommand):
    """Fix issues with the importer"""
    def add_arguments(self, parser) -> None:
        parser.add_argument('--tournament', help="The name of the tournament")
        parser.add_argument('--tournament_id', help="The id of the tournament")
        parser.add_argument('tsh_file', help="the path to the 'a.t' file from tsh")
        parser.add_argument('rating_file', help="the path to the .RT2 file for ratings")


    def handle(self, *args, **options):
        if options.get('tournament'):
            self.t = Tournament.get_by_name(options.get('tournament'),'')
        else:
            self.t = Tournament.objects.get(pk=options.get('tournament_id'))

        with open('/home/raditha/Downloads/finalists.txt') as fp:
            for line in fp:
                line = line.strip()
                try:
                    n = int(line)
                    tournament = Tournament.objects.get(id=n)
                except:
                    try:
                        p = Participant.objects.get(tournament=tournament, name=line)
                        print(p.user.id)
                    except:
                        print(tournament.id, p.name, "NOT FOUND")

    def from_tsh(self, options):
        with open(options['tsh_file']) as fp:
            content = fp.read()

        names = []
        with open(options['tsh_file']) as fp:
            results = tsh.tsh_import(fp)
            for participant in results:
                name = participant['name']
                if name != 'Bye':
                    try:
                        p = self.t.participants.get(name=name)
                        #print(p.id, p.name)
                        if ' ' not in p.name or '.' in p.name:
                            profile = Profile.objects.get(user=p.user)
                            if profile.national_list_name is None:
                                if profile.wespa_list_name is None:
                                    print(p.name, '|', profile.preferred_name)
                                    content = content.replace(p.name, profile.preferred_name)
                                    p.name = profile.preferred_name
                                    p.save()
                                else:
                                    print(p.name, profile.wespa_list_name)
                            else:
                                print(p.name, profile.national_list_name)
                        names.append(p.name)

                    except Participant.DoesNotExist:
                        print("Not found :",name)
                        names.append(name)
                
        rat = pd.read_fwf(options['rating_file'], skiprows=1, 
                    names=['Nick','State', '_Name', 'Games','rating','last'])
        
        names = pd.DataFrame(names, columns=['_Name'])
        result = names.merge(rat, how='left')[['_Name','rating']].fillna(100)
        path = options['tsh_file'].replace('a.t','ratings.csv')
        result.to_csv(path)
        with open(options['tsh_file'], 'w') as fp:
            fp.write(content)

        


        