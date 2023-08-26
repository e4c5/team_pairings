"""
Views for creating, editing and viewing user profiles.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from profiles.forms import UserProfileForm
from django.contrib.postgres.search import TrigramSimilarity
from ratings.models import Unrated, WespaRating, NationalRating
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

                return redirect('/profile/connect')
        return render(request, 'profiles/names.html', {
            "form": form})    
    else:
        return render(request, 'profiles/index.html')


def search_names(rtype, name):
    if rtype == "wespa":
        qs = WespaRating.objects
    elif rtype == "national":
        qs = NationalRating.objects
    else:
        qs = Unrated.objects

    return qs.annotate(
            similarity=TrigramSimilarity('name', name)
    ).filter(similarity__gt=0.8).order_by('-similarity')


@login_required
def connect(request):
    profile = request.user.profile
    if not profile.full_name:
        redirect('/profile/')
    wespa = search_names("wespa", profile.preferred_name)
    national = search_names("national", profile.preferred_name)
    unrated = search_names("unrated", profile.preferred_name)
    
    return render(request, 'profiles/connect.html', 
            { "wespa": wespa, "national": national, "unrated": unrated }
    )

