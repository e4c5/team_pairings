"""
Views for creating, editing and viewing site-specific user profiles.

"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from profiles.forms import UserProfileForm

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
                print("Looks good")
        return render(request, 'profiles/names.html', {
            "form": form})    
    else:
        return render(request, 'profiles/index.html')
