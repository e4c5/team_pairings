from datetime import date
import faker
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tournament.models import Tournament, Director, Result
from tournament.tools import add_participants

from tsh import tsh

class Command(BaseCommand):
    """Creates some sample tournaments.
    When a new tournament director is welcomed into the system a few sample
    tournaments should be setup so that they can get familiar with the system
    """

    def add_arguments(self, parser) -> None:
        parser.add_argument('--user', required=True,
                            help="The username of the tournament director")
        
        parser.add_argument('--delete', required=False,
                            help="Deletes all samples for the user")


    def handle(self, *args, **options):
        u = User.objects.get(username=options['user'])
        if options.get('delete'):
            tournaments = [f'{u.username} Eighteen Rounds', 
                          f'{u.username} Five Rounder', f'{u.username} small']
            for name in tournaments:
                t = Tournament.objects.get(name=name)
                for rnd in t.rounds.order_by('round_no'):
                    Result.objects.filter(round=rnd).delete()
                    rnd.delete()

                t.participants.all().delete()
                t.delete()

        else:
            soy = Tournament.objects.create(
                name=f"{u.username} Eighteen Rounds",
                num_rounds=18, start_date=date.today(),
                private=True
            )
            Director.objects.create(tournament=soy, user=u)

            results = tsh.tsh_import('tsh/data/tournament1/a.t')
            tsh.save_to_db(soy, results)

            five = Tournament.objects.create(
                name=f"{u.username} Five Rounder",
                num_rounds=5, start_date=date.today(),
                private=True
            )
            Director.objects.create(tournament=five, user=u)
            add_participants(five, count=100, use_faker=True)

            five = Tournament.objects.create(
                name=f"{u.username} Small",
                num_rounds=5, start_date=date.today(),
                private=True
            )
            Director.objects.create(tournament=five, user=u)
            add_participants(five, count=10, use_faker=True)
            