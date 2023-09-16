from django import forms
from django.core.validators import RegexValidator

from tournament.models import Participant

class PaymentForm(forms.Form):
    tournament = forms.IntegerField(widget=forms.HiddenInput())
    payment = forms.FileField(required=False)

class UserProfileForm(forms.Form):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'yyyy/mm/dd','class': 'form-control'}
        ),
        input_formats=['%Y-%m-%d'],
        label='Date of Birth',
    )

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Gender',
    )

    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Full Name',
    )

    display_name = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Match your ratings list name. 20 characters max."}),
        label='Display Name',
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    phone = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=17,
        label='Phone Number',
    )

    organization = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'required': False,
                   'placeholder': "Leave blank if you are not a student"}
        ),
        max_length=128, required=False,
        label='School / University (if a student)',
    )
