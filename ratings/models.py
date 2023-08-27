from django.db import models

class WespaRating(models.Model):
    """Represents a wespa rating.
    It would make more sense to use a foreign key to the player, but player
    records do not exists. As far are our system is concerned wespa ratings
    came first."""
    name = models.CharField(max_length=20, unique=True)
    country = models.CharField(max_length=4)
    rating = models.IntegerField()
    games = models.IntegerField()
    last = models.CharField(max_length=20)


class NationalRating(models.Model):
    """Represents a national rating.
    As above it would have made a lot more sense to use a foreign key to the
    player id but we do not have that luxury."""
    name = models.CharField(max_length=20, unique=True)
    rating  = models.IntegerField()
    last = models.CharField(max_length=20)
    country = models.CharField(max_length=3)
    games = models.IntegerField()


class Unrated(models.Model):
    """Represents a player that has not been rated yet."""
    name = models.CharField(max_length=128)
