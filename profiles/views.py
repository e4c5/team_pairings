"""
Views for creating, editing and viewing user profiles.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Case, When, Value, BooleanField, Q
from django.utils import timezone

from profiles.forms import UserProfileForm, PaymentForm
from ratings.models import Unrated, WespaRating, NationalRating
from tournament.models import Tournament, Participant

@login_required
def edit(request):
    profile = request.user.profile
    
    if request.method == "GET":
        form = UserProfileForm(
            initial = {'full_name': profile.full_name,
                      'phone': profile.phone,
                      'gender': profile.gender,
                      'display_name': profile.preferred_name,
                      'date_of_birth': profile.date_of_birth,
                      'organization' : profile.organization
            }
        )
    else:
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile.full_name = form.cleaned_data['full_name']
            profile.phone = form.cleaned_data['phone']
            profile.gender = form.cleaned_data['gender']
            profile.preferred_name = form.cleaned_data['display_name']
            profile.date_of_birth = form.cleaned_data['date_of_birth']
            profile.organization = form.cleaned_data['organization']
            profile.save()

            return redirect('/profile/connect/')
    return render(request, 'profiles/names.html', {
        "form": form}) 


@login_required
def index(request):
    """Wait till confirmation is recieved"""
    profile = request.user.profile
    if not profile.full_name:
        return edit(request)   
    else:
        tournaments = list(Tournament.objects.filter(
            Q(start_date__gte=timezone.now()) & Q(registration_open=True)
        ))
        user_participation = Participant.objects.filter(user=request.user).values_list('tournament', flat=True)

        # Annotate the queryset with a 'registered' field
        for tournament in tournaments:
            tournament.registered = tournament.id in user_participation
            if 'Galle' in tournament.name or 'Colombo' in tournament.name:
                tournament.closed = True
                
        return render(request, 'profiles/index.html', {'tournaments': tournaments})


def search_names(rtype, name):
    if rtype == "wespa":
        qs = WespaRating.objects
    elif rtype == "national":
        qs = NationalRating.objects
    else:
        qs = Unrated.objects

    return qs.annotate(
            similarity=TrigramSimilarity('name', name)
    ).filter(similarity__gt=0.75).order_by('-similarity')


@login_required
def connect(request):
    profile = request.user.profile

    if request.method == "GET":
        if not profile.full_name:
            redirect('/profile/')

        wespa = search_names("wespa", profile.preferred_name)
        national = search_names("national", profile.preferred_name)
        unrated = search_names("unrated", profile.preferred_name)
        
        return render(request, 'profiles/connect.html', 
                { "wespa": wespa, "national": national, "unrated": unrated }
        )
    
    else:
        wespa = request.POST.get('wespa')
        national = request.POST.get('national')
        unrated = request.POST.get('unrated')

        if not wespa and not national and not unrated:
            request.user.profile.beginner = True
        else:
            request.user.profile.wespa_list_name = wespa
            request.user.profile.national_list_name = national
            request.user.profile.beginner = False
        
        request.user.profile.save()
        return redirect('/profile/')

@login_required
def payment(request):
    """Display payment information for a tournament.
    
    For this release, it's assumed that there's only one tournament for which 
    payment is being collected, but going forward there needs to be support for
    multiple tournaments.
    """
    
    participants = Participant.objects.filter(user=request.user)

    if request.method == 'POST':
        instance = participants.exclude(approval='V').first()
        
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            instance.payment = form.cleaned_data['payment']
            instance.approval = 'P'
            instance.save()
            return redirect('/profile/payment/')
    else:
        form = PaymentForm()
    
    return render(request, 'profiles/payment.html', 
                    {'participants': participants, 'form': form}
            )
    
    