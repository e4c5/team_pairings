import re
import decimal

from django.db import models, connection
from django.db.models import Q, Max
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
    NON_TEAM = 'S'

    DATA_ENTRY_CHOICES = ((BY_TEAM, 'By Team'), (NON_TEAM, 'Individual Tournament'),
                          (BY_PLAYER, 'By Player'))

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

    round_robin = models.BooleanField(default=False, blank=True, null=False)

    # this is tournament a private one?
    private = models.BooleanField(default=True, blank=True, null=False)
    # are we accepting registrations for this event
    registration_open = models.BooleanField(default=False, blank=True, null=False)

    venue = models.CharField(max_length=100, blank=True, default="To be notified")

    fee = models.IntegerField(default=0, blank=True, null=False)

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
    
    
    def score_bye(self, result):
        """The bye result should be entered automatically"""
        
        if not self.team_size:
            # this is for an individual tournament
            if result.p1.name == 'Bye':
                result.score1 = 0
                result.score2 = 100
            else:
                result.games_won = 1
                result.score1 = 100
                result.score2 = 0
            result.save()
            return
        
        elif self.entry_mode == Tournament.BY_PLAYER:
            # team tournament where results for each individual player is tracked
            rnd = result.round
            mid = self.team_size // 2
            if result.p2.name == 'Bye':
                # team1 1 got a bye
                for i in range(self.team_size):
                    b = BoardResult.objects.get(
                        Q(round=rnd) & Q(team1=result.p1) & Q(team2=result.p2) & Q(board=i+1)
                    )
                    if i <= mid:
                        b.score1, b.score2 = 100, 0
                    else:
                        b.score1, b.score2 = 0, 100
                    b.save()

            elif result.p1.name == 'Bye':
                # player 2 got a bye
                for i in range(self.team_size):
                    b = BoardResult.objects.get(
                        Q(round=rnd) & Q(team1=result.p1) & Q(team2=result.p2) & Q(board=i+1)
                    )
                    if i <= mid:
                        b.score1, b.score2 = 0, 100
                    else:
                        b.score1, b.score2 = 0, 0
                    b.save()
                
        
        if result.p2.name == 'Bye':
            # team 1 got the bye
            result.score1 = 300
            result.score2 = 0
            result.games_won = 3
        else:
            result.score2 = 300
            result.score1 = 0
            result.games_won = 2

        result.save()

    
    def get_last_completed(self):
        '''
        Returns the last round for which all results are in
        '''
        try:
            paired = self.rounds.filter(paired=True)
            results = Result.objects.exclude(score1=None).exclude(score2=None).filter(round__in=paired)
            return results.order_by('-round__round_no')[0].round
        except IndexError:
            return None
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.tournament_slug(self.name)

        if not self.team_size:
            self.entry_mode = Tournament.NON_TEAM
            
        super().save(*args, **kwargs)


    def update_num_rounds(self):
        """Change num rounds based on num players for RR"""        
        if self.round_robin:
            p = self.participants.exclude(offed=True).count()
            bye = self.participants.filter(name='Bye').exists()
            if p % 2 == 1 and not bye:
                Participant.objects.create(
                        name='Bye', tournament=self, rating=0
                    )
                p += 1

            if self.num_rounds < p - 1:
                for i in range(self.num_rounds + 1, p):
                    TournamentRound.objects.create(tournament=self, round_no=i,
                        pairing_system=TournamentRound.AUTO, repeats=0,
                        based_on=i - 1)
                
                self.num_rounds = p - 1
                self.save()

            if self.num_rounds > p - 1:
                self.num_rounds = p - 1
                self.rounds.filter(round_no__gt=p - 1).delete()
                self.save()

        
    def update_all_standings(self):
        """Updates all the standings for the current tournament.
        Args: tournament: A tournament object
        This is specially usefull when a round is truncated.
        see also: update_standings
        """

        for p in self.participants.all():
            # this absolutely is not the right way but this is not a function
            # that will be used all that much and even with 200 players this
            # is still only going to take a second or two.
            if self.team_size:
                update_team_standing(p.id)
            else:
                update_standing(p.id)


class TournamentRound(models.Model):
    """Represents a tournament round configuration"""
    ROUND_ROBIN = "ROUND_ROBIN"
    SWISS = "SWISS"
    KOTH = "KOTH"
    RANDOM = "RANDOM"
    MANUAL = "MANUAL"
    AUTO = "AUTO" # Try round robin first and then swiss.
    
    PAIRING_CHOICES = ([ROUND_ROBIN, 'Round Robin'], [SWISS, 'Swiss'],
                       [KOTH, 'KOTH'], [RANDOM, 'Random'], [MANUAL,"Manual"],
                       [AUTO, 'Auto'])
    
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
    APPROVAL_CHOICES = [
        ('V', 'Verified'), ('R','Verficiation Failed'), 
        ('P', 'Pending Verification'), ('U', 'Unpaid')
    ]

    name = models.CharField(max_length=128)
    played = models.IntegerField(default=0, null=True)
    game_wins = models.FloatField(default=0, null=True)
    round_wins = models.FloatField(default=0, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')

    spread = models.IntegerField(default=0, null=True)
    offed = models.IntegerField(default=0, null=True)
    rating = models.IntegerField(default=0, null=True)
    # to assign a number for each team or player.
    seed = models.IntegerField()

    # how many times did this player go first
    white = models.IntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.FileField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='approved_by',null=True,blank=True)
    approved_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approval = models.CharField(max_length=1, choices=APPROVAL_CHOICES, default='U')


    def mark_absent(self, rnd):
        bye, _ = Participant.objects.get_or_create(
                        name='Absent', tournament=rnd.tournament,
                        defaults = {'name': 'Absent', 'rating': 0,  'tournament': rnd.tournament}
        ) 
        Result.objects.create(p1=self, p2=bye, score1=0, score2=100,
                                    round=rnd, games_won=0)
        
    def __str__(self):
        if self.tournament.team_size:
            return f'{self.name} {self.round_wins} {self.game_wins}'
        else:
            return f'{self.name} {self.game_wins} {self.spread}'
    
    def save(self, *args, **kwargs):
        if self.name == 'Bye' or self.name == 'Absent':
            self.approval = 'V'
        super().save(*args, **kwargs)

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

class Payment(Participant):
    class Meta:
        proxy = True
   
class Result(models.Model):
    """A round result.
    
    If you make any changes here, double check the update_result function which 
    is a signal for post_save.

    When a round is paired, a result entry will be created for each pairin with
    score1 and score2 being set to null.

    Immidiately after these records created the pairing class will add scores 
    for the byes and the absentees. Afterwards the remainder will be filled by 
    tournament directors.
    
    So this is a two step process, keep that in mind when writing tests.
    """
    round = models.ForeignKey(TournamentRound, on_delete=models.PROTECT, related_name='results')
    # the fact that this is called p1 does not mean this player goes first
    p1 = models.ForeignKey(Participant, on_delete=models.PROTECT, related_name='p1',blank=True)   
    # p2 doesn't mean going second
    p2 = models.ForeignKey(Participant,on_delete=models.PROTECT, related_name='p2', blank=True)   

    # The starting player, a non null entry means that player identified
    # goes first. Null means they toss for it. 
    starting = models.ForeignKey(Participant, null=True, blank=True,
        on_delete=models.PROTECT, related_name='starting')   

    # only used for team tournaments.
    # the number of games won in the round by the first player
    games_won = models.FloatField(blank=True, null=True)
    score1 = models.IntegerField(blank=True, null=True)
    score2 = models.IntegerField(blank=True, null=True)
    table = models.IntegerField(default=0)

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

#
# almost all the code in the next section can be converted into triggers but
# I have my reasons for not doing so. One of the more important being making
# sure there is high levels of code coverage. Well triggers you can't get a
# coverage report AFAIK.
#
# The other obvious reason to keep the code here in signals rather than 
# triggers is that triggers are much much harder to debug.
#
# Primary drawback of this approach of course is that if someone manually
# edits the db, these signals will not be fired.

@receiver(pre_save, sender=Result)
def result_presave(sender, instance, **kwargs):
    """Before saving a round result validate p1 and p2

    this can't be done in a constraint but  trigger can be used. The constrain
    we are trying to enforce is that resutls are always saved with the lower
    participant id taking up p1 and the higher one taking up p2
    """
    if instance.p1 and instance.p1.id > instance.p2.id:
        instance.p1, instance.p2 = instance.p2, instance.p1 
        if instance.score1 and instance.score2:
            m = instance.round.tournament.team_size or 1
            instance.games_won = m - instance.games_won
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

        r = Result.objects.filter(
            (Q(p1=instance.team1) & Q(p2=instance.team2)) 
        ).order_by('-round__round_no')[0]
        
        r.games_won = 0
        r.score1 = 0
        r.score2 = 0
        boards = BoardResult.objects.filter(
            Q(round=instance.round) & Q(team1=r.p1) & Q(team2=r.p2)
        ).exclude(Q(score1=None) | Q(score2=None))

        for b in boards:
            if b.score1 > b.score2:
                r.games_won += 1
            elif b.score1 == b.score2:
                r.games_won += 0.5
            r.score1 += b.score1
            r.score2 += b.score2

        r.save()
        
        if player1 and player2:
            player1.spread += (instance.score1 - instance.score2)
            player2.spread -= (instance.score1 - instance.score2)
            player1.save()
            player2.save()
        

@receiver(post_save, sender=Result)
def update_result(sender, instance, created, **kwargs):
    """When a result instance is saved the standings need to update"""
    if (not created or instance.p1.name in ['Absent','Bye'] or instance.p2.name in ['Absent','Bye']):
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
            spread = a.margin + b.margin, white = a.white + b.white
            from 
                (select count(*) as games, coalesce(sum(games_won),0) games_won, 
                    coalesce(sum(score1 - score2), 0) margin, 
                    count(CASE WHEN starting_id = {0} THEN 1 ELSE NULL END) white
            from tournament_result tr where p1_id = {0} and score1 is not null and score2 is not null) a,
                (select count(*) as games, 
                    coalesce(sum(CASE WHEN score2 = 0 THEN 0 ELSE 1 - games_won END), 0) games_won, 
                    coalesce(sum(score2 - score1), 0) margin,
                    count(CASE WHEN starting_id = {0} THEN 1 ELSE NULL END) white
            from tournament_result tr where p2_id = {0}  and score1 is not null and score2 is not null) b
            where id = {0}"""

    with connection.cursor() as cursor:
        cursor.execute(q.format(pid))

def update_team_standing(pid):
    """Execute the standing update query. for the given participant
    Args: pid: participant id

    Also see Tournament.update_all_standings
    """
    q = """
        update tournament_participant set played = a.games + b.games,
            game_wins = a.games_won + b.games_won, white = a.white + b.white,
            round_wins = a.rounds_won + b.rounds_won, spread = a.margin + b.margin
            from (select count(*) as games, coalesce(sum(games_won),0) games_won, 
                coalesce(sum(CASE when games_won is null THEN 0 
                                WHEN games_won > 2.5 THEN 1 
                                WHEN games_won = 2.5 THEN .5 else 0 end), 0) rounds_won,
                coalesce(sum(score1 - score2),0) margin,
                coalesce(sum(CASE WHEN starting_id = {0} THEN 1 ELSE 0 END),0) white
            from tournament_result tr where p1_id = {0} and games_won is not null) a,
            (select count(*) as games, coalesce(sum(5 - games_won),0) games_won, 
                coalesce(sum(CASE WHEN games_won IS NULL THEN 0 
                         WHEN games_won < 2.5 THEN 1 
                         WHEN games_won = 2.5 THEN .5 else 0 END),0) rounds_won,
                coalesce(sum(score2 - score1),0) margin,
                coalesce(sum(CASE WHEN starting_id = {0} THEN 1 ELSE 0 END),0) white
            from tournament_result tr where p2_id = {0} and games_won is not null) b
            where id = {0}"""

    with connection.cursor() as cursor:
        cursor.execute(q.format(pid))

@receiver(post_save, sender=Tournament)
def setup_tournament(sender, instance, created, **kwargs):
    if created and instance.num_rounds > 0:
        for i in range(1, instance.num_rounds + 1):
            TournamentRound.objects.create(tournament=instance, round_no=i,
                    pairing_system=TournamentRound.AUTO, repeats=0,
                    based_on=i - 1)


@receiver(pre_save, sender=Participant)
def participant_seed(sender, instance, **kwargs):
    if not instance.pk and instance.seed is None:
        if instance.name == 'Bye':
            instance.seed = 0
        else:
            seed = Participant.objects.filter(tournament_id=instance.tournament_id).aggregate(Max('seed'))
            if not seed['seed__max']:
                instance.seed = 1
            else:
                instance.seed = seed['seed__max'] + 1


@receiver(post_save, sender=Participant)
def participant_absent(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.name == 'Bye' or instance.name == 'Absent':
        return
    
    last = instance.tournament.get_last_completed()
    if last:
        for rnd in instance.tournament.rounds.filter(round_no__lte=last.round_no):
            instance.mark_absent(rnd)
    