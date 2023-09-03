import time
import random

from django.db import models
from django.contrib.auth.models import User     
from django.contrib.postgres.search import TrigramSimilarity

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


from profiles import fields

class Avatar(models.Model):
    '''
    User's profile pictures
    '''
    id = models.BigIntegerField(default = fields.make_id, primary_key=True)
    user = models.ForeignKey(User, db_column='userId', null=True, blank = True, on_delete=models.CASCADE)
    photo_link = models.CharField(max_length = 250, blank = True, null = True)
    is_main = models.BooleanField(default = False)
    
    
class Profile (models.Model):
    '''
    The profile. Isn't it bleeding obvious?

    Users have several names. First up they have a name that appears on the
    WESPA rating list. This name can be upto 20 characters only. We also 
    have a national list name, which in most cases turns out to be twenty 
    characters long.

    But some players have names that a much longer. Kavindu Malawaraarachchi
    is a great example. His name appears on the wespa list as Kavindu 
    Malawaraarac (truncated)

    Some Sri Lankan names are particularly long. Some people have three or
    four different middle names and for others their surname appears before
    all other names and can be particularly long as well.
    '''

    GENDER_CHOICES = (('M','Male'), ('F','Female'), ('U','Unspecified'))
    PRIVACY_CHOICES = ((True,'Yes'),(False,'No'));
    player_id = models.CharField(max_length=5)
    about_me = models.CharField(blank=True, null=True, max_length=512)
    website_url = models.URLField(blank=True, null=True, max_length=128)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default = 'U')
    verified = models.BooleanField(default = False)
    user = models.OneToOneField(User, primary_key = True, on_delete=models.CASCADE)
    
    is_public = models.BooleanField(verbose_name=u'Make profile public', 
                                    choices = PRIVACY_CHOICES, default = False)

    user_preferences = models.JSONField(default = dict,blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    national_list_name = models.CharField(max_length=20, blank=True, null=True)
    wespa_list_name = models.CharField(max_length=20, blank=True, null=True)

    # the users full name so that we can verify them against passports or
    # official documents if needed.
    full_name = models.CharField(max_length=128, blank=True, null=True)
    # the name as it should appear on a tourament name list.
    preferred_name = models.CharField(max_length=128, blank=True, null=True)

    beginner = models.BooleanField(default = False)
    
    organization = models.CharField(max_length=128, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """Fill the player_id field.
        The player_id is made up of the first letter of the user.first_name and 
        five letters from the user.last_name if the the player_id"""
        if not self.player_id:
            created = False
            for n in range(1, 6):
                self.player_id = self.user.first_name[0:n] + self.user.last_name[0:5-n]
                self.player_id = self.player_id.upper()
                if not Profile.objects.filter(player_id = self.player_id).exists():
                    created = True
                    break

            if not created:
                # create self.player_id to be 6 random letters
                self.player_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ',k=5))

        super(Profile,self).save(*args, **kwargs)
        
    def __str__(self):
        return self.user.username

    class Meta:
        app_label = 'profiles'
    

class PhoneNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    number = models.BigIntegerField(unique = True)
    verified = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)

    class Meta:
        unique_together = [("user", "number")]
        app_label = 'profiles'


    def __str__(self):
        return u"%s (%s)" % (self.number, self.user)

    def set_as_primary(self, conditional = False):
        old_primary = PhoneNumber.objects.get_primary(self.user)
        if old_primary:
            if old_primary.verified and not self.verified:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        self.user.save()
        return True


    def change(self, request, new_email, confirm=True):
        """
        Given a new phone number, change self and re-confirm.
        """
        with transaction.commit_on_success():
            self.verified = False
            self.save()


class Audit(models.Model):
    '''
    This class is used to keep track of deleted verification data. Sometimes a 
    hacker might break into an account and replace the phone number or email 
    address with his own. When that happens we need to know what it used to be.
    This is achieved with the aid of a trigger that gets fired on DELETE for
    phone, email, bank or postal address. Also gets fired when a record in the
    auth_user table is updated.
   
    These codes are used for kind
    1 - email changed
    4 - Password change
    '''        
    kind = models.SmallIntegerField()
    user_id = models.IntegerField();
    data = models.CharField(max_length = 255)
    
    class Meta:
       app_label = 'profiles'
    


@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):
    '''
    Creates a profile object for registered users via the
    user_registered signal
    '''
    if created:
        Profile.objects.get_or_create(user=instance)    

