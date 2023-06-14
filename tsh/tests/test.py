from io import StringIO
from django.test import TransactionTestCase, TestCase
from django.core.management import call_command, CommandError
from tournament.models import Tournament, Participant

from tsh import tsh

class TransTests(TransactionTestCase):

    def setUp(self) -> None:
        self.t1 = Tournament.objects.create(name='Sri Lankan open', start_date='2023-02-25',
            rated=False,  entry_mode='S', num_rounds=18)
        
        return super().setUp()
    
    def test_import(self):
        with open('tsh/data/tournament1/a.t') as fp:
            participants = tsh.tsh_import(fp)
            self.assertEqual(len(participants), 39)


    def test_impex_command(self):
        """Tests both import and export together
        Since there really isn't a good way to test export without launching
        tsh which is really ugly and not what unit testing is about
        """
        out = StringIO()
        call_command(
            'importer', 'tsh/data/tournament1/a.t', 
            '--tournament_id', self.t1.pk,
            stdout=out
        )

        self.assertEqual('', out.getvalue())
        self.assertEqual(Participant.objects.count(), 39)

        bye = Participant.objects.get(name='Bye')
        self.assertEqual(bye.seed, 0)

        p1 = Participant.objects.get(seed=1)
        self.assertEquals(p1.white, 9)
        self.assertEquals(p1.game_wins, 15)
        self.assertEquals(p1.spread, 1474)

        out = StringIO()
        tsh.tsh_export(self.t1, out)
        results = out.getvalue().split("\n")
        self.assertEqual(len(results), 39) # theres a blank line at the end not sure why!


    def test_bad_command(self):
        self.assertRaises(CommandError, call_command, 'exporter')
        self.assertRaises(CommandError, call_command, 'exporter', '--tournament_id', 10)
        self.assertRaises(CommandError, call_command, 'exporter', '--tournament', 'bada')

        self.assertRaises(CommandError, call_command, 'importer')
        self.assertRaises(CommandError, call_command, 'importer', '--tournament_id', 10)
        self.assertRaises(CommandError, call_command, 'importer', '--tournament', 'bada')

    
