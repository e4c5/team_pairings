from django.contrib.auth.models import User

from django import forms
from django.forms import widgets

from django.utils.translation import ugettext_lazy as _


from profiles.models import UserProfile, PhoneNumber, SMSConfirmation, SnailMail,\
    BankAccount
from main.forms import UserForm

class DpForm(forms.Form):
    '''
    Images are uploaded to a separate server. We only save a link here
    '''
    image_url = forms.URLField(required = True)
    

class ProfileForm(forms.ModelForm):
    '''
    This form is to update the user profile. 
    profiles can be imported from facebook as well.
    
    '''
     
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        try:
            for n,field in self.fields.iteritems() :
                field.widget.attrs.update({'class': 'form-control'})
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        except User.DoesNotExist:

            pass
    
    
    first_name = forms.CharField(max_length=30, label=u'First Name')
    last_name = forms.CharField(max_length=30, label=u'Last Name')
    #alerts_via = forms.ChoiceField(required = False, choices = UserProfile.ALERT_CHOICES);
    
    gender = forms.ChoiceField(choices = UserProfile.GENDER_CHOICES, required = False)
    
    
    class Meta:
        model = UserProfile
        exclude = ('user','alerts_via','user_preferences','is_public','date_of_birth')    
        widgets = {
                    'website_url': forms.TextInput(attrs = {'type': 'url'}),
                     
                  }    
    
    ''' 
    I was previously saving the user object at this point (in the save method)
    however on sep20, 2013 I felt that it may not be the best and the most secure
    way of doing it and that code was moved to the view
    '''
        
class VerifyNumberForm(UserForm):
    verification_code = forms.IntegerField(label = _("Verification code"))
        
    def clean_verification_code(self):
        value = self.cleaned_data['verification_code']
        try :
            confirm = SMSConfirmation.objects.get(key = value, number__verified = False,
                                             number__user = self.user)
            confirm.number.verified = True
            if PhoneNumber.objects.filter(user = self.user, primary = True).count() == 0:
                confirm.number.primary = True
                
            confirm.number.save()
            
            
        except Exception, e :
            print e
            raise forms.ValidationError("We could not find a number associated with that verification code")
    
    
class NotificationForm(forms.Form):
    CHOICES = ( (1, 'Each time you recieved a message on road.lk'),
                (2, 'Rideshare matches, status changes and payments'),
                (3, 'Rideshare status changes and payments'),
                (4, "Don't send me any notifications."))
    
    send_mail = forms.ChoiceField(widget = forms.RadioSelect, choices = CHOICES)
    promotional = forms.ChoiceField(widget = forms.CheckboxInput, 
                    label = "Send me emails about special offers, new features and updates (At most once per month)")
    
class AddNumberForm(UserForm):

    number = forms.IntegerField(label=_("Phone Number"), # number type probably doesn't look right here
                             required=True, widget=forms.TextInput(attrs={"size": "30"}), 
                             min_value = 99999,
                             error_messages = {'invalid' : 'Please type the number without spaces or dashes'}
                             )

    def clean_number(self):
        value = self.cleaned_data["number"]

        errors = {
            "this_account": _("This number is already associated"
                              " with this account."),
            "different_account": _("This number is already associated"
                                   " with another account."),
        }
        emails = PhoneNumber.objects.filter(number = value)
        if emails.filter(user=self.user).exists():
            raise forms.ValidationError(errors["this_account"])
        if emails.exclude(user=self.user).exists():
                raise forms.ValidationError(errors["different_account"])
        return value

    def save(self, request):
        return PhoneNumber.objects.add_number(request, self.user, self.cleaned_data["number"], confirm=True)


class PostalForm(UserForm):
    def __init__(self, *args, **kwargs):
        super(PostalForm, self).__init__(*args, **kwargs)
        self.initial['country'] = self.request.session.get('country')
        
    address = forms.CharField(widget = forms.Textarea)
    post_code = forms.CharField(required = False)
    country = forms.ChoiceField(choices = ())
    
    def save(self, request):
        f = self.cleaned_data
        if SnailMail.objects.filter(user = self.user).count() == 0 :
            primary = True
        else :
            primary = False
            
        sm = SnailMail(user = self.user, address = f['address'], primary = primary,  
                       postal_code = f['post_code'], country = f['country'])
        sm.save()
        
class BankForm(UserForm):
    account_name = forms.CharField()
    bank_name = forms.CharField()
    account_number = forms.IntegerField()
    bank_branch = forms.CharField()
    
    def save(self, request):
        f = self.cleaned_data
        if BankAccount.objects.filter(user = self.user).count() == 0 :
            primary = True
        else :
            primary = False
            
        sm = BankAccount(user = self.user, account_name = f['account_name'], primary = primary,  
                       bank_name = f['bank_name'], bank_branch = f['bank_branch'],
                       account_number = f['account_number'])
        sm.save()