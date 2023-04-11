import re
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Create your models here.


class Tournament(models.Model):
    ''' A tournament can sometimes have many sections, they can be rated or unrated.
    But one thing for sure they will have at least two players
    '''
    BY_TEAM = 'T'
    BY_PLAYER = 'P'
    DATA_ENTRY_CHOICES = ((BY_TEAM, 'By Team'), (BY_PLAYER, 'By Player'))

    start_date = models.TextField()
    name = models.TextField()
    rated = models.IntegerField(default=True)
    slug = models.TextField(unique=True, blank=True)

    # team size is not null when a team tournament
    team_size = models.IntegerField(blank=True, null=True)

    # do we add up the team scores and enter that or do we enter them
    # player by player?
    entry_mode = models.CharField(choices=DATA_ENTRY_CHOICES, default=BY_TEAM, max_length=1)

    num_rounds = models.IntegerField()

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
            return None

        return tourney        

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/tournament/{0}/".format(self.slug)
    
    @property
    def current_round(self):
        '''
        Returns the current round
        
        That is the round that is in progress. None if the tournament has concluded. 
        '''
        try:
            if self.rounds.all()[0].results.count() > 0:
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
    """Represents a tournament round configuration"""
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

    # when we make the pairing for this round, which result do we use 
    # for pairing?
    based_on = models.IntegerField(null=True, blank=True)
    paired = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Round {self.round_no}'
        
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(based_on__lt=models.F('round_no')),
                name='based_on_check'
            ),
            models.CheckConstraint(
                check=models.Q(round_no__gt=0),
                name='round_no_check'
            )
        ]

class Director(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)


class Participant(models.Model):
    ''' A player or a team in a tournament'''
    name = models.CharField(max_length=128)
    played = models.IntegerField(default=0, null=True)
    game_wins = models.FloatField(default=0, null=True)
    round_wins = models.FloatField(default=0, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')

    spread = models.IntegerField(default=0, null=True)
    offed = models.IntegerField(default=0, null=True)
    rating = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f'{self.name} {self.round_wins} {self.game_wins}'
    class Meta:
        unique_together = ['name','tournament']

        constraints = [
            models.CheckConstraint(
                check=models.Q(game_wins__gte=0),
                name='wins_check'
            ),
            models.CheckConstraint(
                check=models.Q(round_wins__gte=0),
                name='round_win_check'
            )
        ]

   
class   Result(models.Model):
    """A round result.
    
    If you make any changes here, double check the update_result function which 
    is a signal for post_save
    """
    round = models.ForeignKey(TournamentRound, on_delete=models.PROTECT, related_name='results')
    # the fact that this is called p1 does not mean this player goes first
    p1 = models.ForeignKey(Participant, on_delete=models.PROTECT, related_name='p1')   
    # p2 doesn't mean going second
    p2 = models.ForeignKey(Participant,on_delete=models.PROTECT, related_name='p2')   

    # The starting player, a non null entry means that player identified
    # goes first. Null means they toss for it. 
    starting = models.ForeignKey(Participant, null=True, blank=True,
        on_delete=models.PROTECT, related_name='starting')   

    # only used for team tournaments.
    # the number of games won in the round by the first player
    games_won = models.DecimalField(blank=True, null=True, max_digits=3, decimal_places=1)
    score1 = models.IntegerField(blank=True, null=True)
    score2 = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        if self.score1:
            return f"{self.p1.name} {self.score1} vs {self.p2.name} {self.score2}"
        return f"{self.p1.name} vs {self.p2.name}"

    class Meta:
        unique_together = ['round','p1','p2']
        constraints = [
            models.CheckConstraint(
                check=models.Q(p1_id__lt=models.F('p2_id')),
                name='p1p2_check'
            ),
        ]

class TeamMember(models.Model):
    """In a team tournament, this represents a team member"""
    team = models.ForeignKey(Participant, on_delete=models.PROTECT)   
    board = models.IntegerField()
    name = models.CharField(max_length=128)
    wins = models.FloatField()
    spread = models.IntegerField()


class BoardResult(models.Model):
    """A result for an individual board in a tournament"""
    round = models.ForeignKey(TournamentRound, on_delete=models.PROTECT)
    team1 = models.ForeignKey(Participant, on_delete=models.PROTECT, related_name='team1')   
    team2 = models.ForeignKey(Participant,on_delete=models.PROTECT, related_name='team2')   
    board = models.IntegerField()
    score1 = models.IntegerField(null=True, blank=True)
    score2 = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['round','team1','team2','board']
        constraints = [
            models.CheckConstraint(
                check=models.Q(team1_id__lt=models.F('team2_id')),
                name='t1t2_check'
            ),
        ]


@receiver(pre_save, sender=Result)
def result_presave(sender, instance, **kwargs):
    """Before saving a round result validate p1 and p2

    this can't be done in a constraint but  trigger can be used. The constrain
    we are trying to enforce is that resutls are always saved with the lower
    participant id taking up p1 and the higher one taking up p2
    """
    if instance.p1 and instance.p1.id > instance.p2.id:
        instance.p1, instance.p2 = instance.p2, instance.p1 
        if instance.games_won:
            instance.score1, instance.score2 = instance.score2, instance.score1


@receiver(pre_save, sender=BoardResult)
def board_result_presave(sender, instance, **kwargs):
    """Before saving a round result validate p1 and p2

    Please see result_presave
    """
    if instance.team1 and instance.team1.id > instance.team2.id:
        instance.team1, instance.team2 = instance.team2, instance.team1
        if instance.score1:
            instance.score1, instance.score2 = instance.score2, instance.score1


@receiver(post_save, sender=BoardResult)
def update_board_result(sender, instance, created, **kwargs):
    """Update a team result when a board result is entered.
    
    This is used for tournaments where we keep score of individual players
    rather than add the total resutl to the team

    This signal ensures that the total result for both the team and the 
    player will be updated accordingly.
    """
    if instance.score1 or instance.score2:
        try:
            player1 = TeamMember.objects.get(
                Q(team=instance.team1) & Q(board=instance.board)
            )
            player2 = TeamMember.objects.get(
                Q(team=instance.team2) & Q(board=instance.board)
            )
        except TeamMember.DoesNotExist:
            player1 = None
            player2 = None

        r = Result.objects.get(
            (Q(p1=instance.team1) & Q(p2=instance.team2)) 
        )

        if r.games_won is None:
            r.games_won = 0
            r.score1 = 0
            r.score2 = 0
        if instance.score1 > instance.score2:
            r.games_won +=1            
            if player1:
                player1.wins += 1
        elif instance.score1 == instance.score2:
            r.games_won += 0.5         
            if player2:
                player2.wins +=1

        r.score1 += instance.score1
        r.score2 += instance.score2
        r.save()

        if player1 and player2:
            player1.spread += (instance.score1 - instance.score2)
            player2.spread -= (instance.score1 - instance.score2)
            player1.save()
            player2.save()
        

@receiver(post_save, sender=Result)
def update_result(sender, instance, created, **kwargs):
    """When a result instance is saved the standings need to update"""
    if not created:
        if instance.score1 or instance.score2:
            if instance.round.tournament.team_size:
                update_team_standing(instance.p1_id)
                update_team_standing(instance.p2_id)
            else:
                update_standing(instance.p1_id)
                update_standing(instance.p2_id)


def update_standing(pid):
    """Update standings for an individual tournament
    Args: pid: participant id
    """

    q = """
        update tournament_participant set played = a.games + b.games,
            game_wins = a.games_won + b.games_won, 
            spread = a.margin + b.margin
            from 
                (select count(*) as games, coalesce(sum(games_won), 0) games_won, 
                    coalesce(sum(score1 - score2), 0) margin
            from tournament_result tr where p1_id = {0} and games_won is not null) a,
                (select count(*) as games, coalesce(sum(1 - games_won), 0) games_won, 
                    coalesce(sum(score2 - score1), 0) margin
            from tournament_result tr where p2_id = {0} and games_won is not null) b
            where id = {0}"""

    print(q.format(pid))
    with connection.cursor() as cursor:
        cursor.execute(q.format(pid))

def update_team_standing(pid):
    """Execute the standing update query. for the given participant
    Args: pid: participant id

    Also see api.views.update_all_standings
    """
    q = """
        update tournament_participant set played = a.games + b.games,
            game_wins = a.games_won + b.games_won, spread = a.margin + b.margin
            from (select count(*) as games, coalesce(sum(games_won),0) games_won, 
                coalesce(sum(CASE when games_won is null THEN 0 
                                WHEN games_won > 2.5 THEN 1 
                                WHEN games_won = 2.5 THEN .5 else 0 end), 0) rounds_won,
                coalesce(sum(score1 - score2),0) margin
            from tournament_result tr where p1_id = {0} and games_won is not null) a,
            (select count(*) as games, coalesce(sum(5 - games_won),0) games_won, 
                coalesce(sum(CASE WHEN games_won IS NULL THEN 0 
                         WHEN games_won < 2.5 THEN 1 
                         WHEN games_won = 2.5 THEN .5 else 0 END),0) rounds_won,
                coalesce(sum(score2 - score1),0) margin
            from tournament_result tr where p2_id = {0} and games_won is not null) b
            where id = {0}"""

    with connection.cursor() as cursor:
        cursor.execute(q.format(pid))

@receiver(post_save, sender=Tournament)
def setup_tournament(sender, instance, created, **kwargs):
    if created and instance.num_rounds > 0:
        for i in range(1, instance.num_rounds + 1):
            TournamentRound.objects.create(tournament=instance, round_no=i,
                    pairing_system=TournamentRound.SWISS, repeats=0,
                    based_on=i - 1)
