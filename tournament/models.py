import re
from django.db import models, connection

from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Tournament(models.Model):
    ''' A tournament can sometimes have many sections, they can be rated or unrated.
    But one thing for sure they will have at least two players
    '''
    start_date = models.TextField()
    name = models.TextField()
    rated = models.IntegerField(default=True)
    slug = models.TextField(unique=True, blank=True)
    # team size is not null when a team tournament
    team_size = models.IntegerField(blank=True, null=True)

    @classmethod    
    def tournament_slug(self, name):
        ''' Slugify tournament names so that we can use them in links '''
        name = re.sub('\(?sl\)?$', '', name.lower())
        return slugify(name.strip())
    
    @classmethod
    def get_by_name(self, tournament_name, start_date, rated=True):
        ''' Fetches a tournament instance from the databse, creates one if needed '''

        try :
            slug = Tournament.tournament_slug(tournament_name)
            tourney = Tournament.objects.get(slug=slug)
    
        except :
            tourney = Tournament.objects.create(name=tournament_name,
                                 rated=rated, start_date=start_date,
                                 slug=Tournament.tournament_slug(tournament_name))

        return tourney        

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/tournament/{0}/".format(self.slug)
    
    @property
    def num_rounds(self):
        '''
        Returns the number of rounds in the tournament
        '''
        return self.rounds.count()
    
    
    @property
    def current_round(self):
        '''
        Returns the current round
        
        That is the round that is in progress. None if the tournament has concluded. 
        '''
        try:
            if self.rounds.all()[0].roundresult_set.count() > 0:
                rnd = self.rounds.filter(roundresult__score_for=None).order_by('-round_no')[0]
                return rnd.round_no
            return 0
        except IndexError:
            return None
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.tournament_slug(self.name)
            
        super().save(*args, **kwargs)


class TournamentRound(models.Model):
    ROUND_ROBIN = "ROUND_ROBIN"
    SWISS = "SWISS"
    KOTH = "KOTH"
    RANDOM = "RANDOM"
    MANUAL = "MANUAL"
    
    PAIRING_CHOICES = ([ROUND_ROBIN, 'Round Robin'], [SWISS, 'Swiss'],
                       [KOTH, 'KOTH'], [RANDOM, 'Random'], [MANUAL,"Manual"])
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    round_no = models.IntegerField()
    spread_cap = models.IntegerField(null=True, blank=True)
    pairing_system = models.CharField(max_length=16, choices=PAIRING_CHOICES)
    repeats = models.IntegerField(default=0)
    based_on = models.IntegerField(null=True, blank=True)
    paired = models.BooleanField(default=False)
    num_rounds = models.IntegerField()
    team_size = models.IntegerField()
    

class Participant(models.Model):
    ''' A player or a team in a tournament'''
    name = models.CharField(max_length=128)
    played = models.IntegerField(default=0, null=True)
    game_wins = models.FloatField(default=0, null=True)
    round_wins = models.FloatField(default=0, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')

    spread = models.IntegerField(default=0, null=True)
    position = models.IntegerField(default=0, null=True)
    offed = models.IntegerField(default=0, null=True)
    seed = models.IntegerField(default=0, null=True)

   
class Result(models.Model):
    round = models.ForeignKey(TournamentRound, on_delete=models.PROTECT)
    first = models.ForeignKey(Participant, on_delete=models.PROTECT, related_name='first')   
    second = models.ForeignKey(Participant,on_delete=models.PROTECT, related_name='second')   
    # only used for team tournaments.
    # the number of games won in the round by the first player
    games_won = models.IntegerField(blank=True, null=True)
    score1 = models.IntegerField(blank=True, null=True)
    score2 = models.IntegerField(blank=True, null=True)
    

@receiver(post_save, sender=Result)
def update_result(sender, instance, created, **kwargs):
    print(instance)
    print(created)

    q = """
        update tournament_participant set played = a.games + b.games,
            game_wins = a.games_won + b.games_won, 
            round_wins = a.rounds_won + b.rounds_won, spread = a.margin + b.margin
            from (select count(*) as games, coalesce(sum(games_won),0) games_won, 
                coalesce(sum(CASE when games_won is null THEN 0 
                                WHEN games_won > 2.5 THEN 1 
                                WHEN games_won = 2.5 THEN .5 else 0 end), 0) rounds_won,
                coalesce(sum(score1 - score2),0) margin
            from tournament_result tr where first_id = {0} and games_won is not null) a,
            (select count(*) as games, coalesce(sum(5 - games_won),0) games_won, 
                coalesce(sum(CASE WHEN games_won IS NULL THEN 0 
                         WHEN games_won < 2.5 THEN 1 
                         WHEN games_won = 2.5 THEN .5 else 0 END),0) rounds_won,
                coalesce(sum(score1 - score2),0) margin
            from tournament_result tr where second_id = {0} and games_won is not null) b
            where id = {0}"""
    if not created:
        if instance.score1 or instance.score2:
            with connection.cursor() as cursor:
                print(q.format(instance.first_id))
                print(q.format(instance.second_id))
                cursor.execute(q.format(instance.first_id))
                cursor.execute(q.format(instance.second_id))
