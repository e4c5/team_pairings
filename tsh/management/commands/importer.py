from django.core.management.base import BaseCommand
from tournament.models import Tournament, Participant, Result
from tsh import tsh

class Command(BaseCommand):

    def add_arguments(self, parser) -> None:
        parser.add_argument('--tournament', help="The name of the tournament")
        parser.add_argument('--tournament_id', help="The id of the tournament")
        parser.add_argument('tsh_file', help="the path to the 'a.t' file from tsh")


    def handle(self, *args, **options):
        if options.get('tournament'):
            self.t = Tournament.get_by_name(options.get('tournament'),'')
        else:
            self.t = Tournament.objects.get(pk=options.get('tournament_id'))

        rounds = [rnd.pk for rnd in self.t.rounds.order_by('round_no')]

        results = tsh.tsh_import(options['tsh_file'])
        # pass one create the database records for the participants.
        participants = []
        for result in results:
            p, _ = Participant.objects.get_or_create(
                name=result['name'],  tournament=self.t,
                defaults={
                    "name": result['name'], "offed": result.get('off', False),
                    "tournament": self.t
                }
            )
            participants.append(p)
            
        # pass 2 save the actual results
        for result in results:
            if result['name'] != 'Bye':
                for idx in range(len(result['opponents'])):
                    score1 = int(result['scores'][idx])
                    opponent = int(result['opponents'][idx])
                
                    if opponent == 0:
                        score2 = 0
                    else:
                        score2 = int(results[opponent]['scores'][idx])
                    
                    p1 = participants[result['seed']]
                    p2 = participants[opponent]

                    if p1.id > p2.id:
                        p2, p1 = p1, p2
                        score2, score1 = score1, score2

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

                    Result.objects.get_or_create(
                        p1=p1, p2=p2,round_id=rounds[idx],
                        defaults = {
                            "p1": p1, "p2": p2,
                            "score1" : score1, "score2": score2, 
                            "games_won": win, 
                            "round_id" : rounds[idx]
                        }
                    )

        self.t.update_all_standings()
