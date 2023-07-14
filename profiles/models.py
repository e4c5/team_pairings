import time
import random

from django.contrib.gis.db import models
from django.contrib.auth.models import User     

from django.core.cache import cache

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
    
    
class UserProfile (models.Model):
    '''
    The profile. Isn't it bleeding obvious?
    '''
    GENDER_CHOICES = (('M','Male'), ('F','Female'), ('U',''))
    PRIVACY_CHOICES = ((True,'Yes'),(False,'No'));
    player_id = models.CharField(max_length=5)
    about_me = models.CharField(blank=True, null=True, max_length=512)
    website_url = models.URLField(blank=True, null=True, max_length=128)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default = 'U')
    
    user = models.OneToOneField(User, primary_key = True, on_delete=models.PROTECT)
    
    is_public = models.BooleanField(verbose_name=u'Make profile public', 
                                    choices = PRIVACY_CHOICES, default = False)

    user_preferences = models.JSONField(default = dict)

    national_list_name = models.CharField(max_length=128, blank=True, null=True)
    wespa_list_name = models.CharField(max_length=128, blank=True, null=True)
                                       
    def save(self, *args, **kwargs):
        super(UserProfile,self).save(*args, **kwargs)
        
        
    def __str__(self):
        return self.user.username

    class Meta:
        app_label = 'profiles'
    

def create_user_profile(sender, user, **kwargs):
    '''
    Creates a profile object for registered users via the
    user_registered signal
    '''
    
    obj = UserProfile.objects.get_or_create(user=user)


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
    
