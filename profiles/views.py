"""
Views for creating, editing and viewing user profiles.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Case, When, Value, BooleanField, Q
from django.utils import timezone

from profiles.forms import UserProfileForm
from ratings.models import Unrated, WespaRating, NationalRating
from tournament.models import Tournament, Participant

@login_required
def index(request):
    """Wait till confirmation is recieved"""
    profile = request.user.profile
    if not profile.full_name:
        if request.method == "GET":
            form = UserProfileForm()
            
        else:
            form = UserProfileForm(request.POST)
            if form.is_valid():
                profile.full_name = form.cleaned_data['full_name']
                profile.phone_number = form.cleaned_data['phone']
                profile.gender = form.cleaned_data['gender']
                profile.preferred_name = form.cleaned_data['display_name']
                profile.date_of_birth = form.cleaned_data['date_of_birth']
                profile.save()

                return redirect('/profile/connect/')
        return render(request, 'profiles/names.html', {
            "form": form})    
    else:
        tournaments = list(Tournament.objects.filter(
            Q(start_date__gte=timezone.now()) & Q(registration_open=True)
        ))
        user_participation = Participant.objects.filter(user=request.user).values_list('tournament', flat=True)

        # Annotate the queryset with a 'registered' field
        for tournament in tournaments:
            tournament.registered = tournament.id in user_participation
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
