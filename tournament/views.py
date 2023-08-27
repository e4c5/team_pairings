from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, BooleanField, Q
from django.utils import timezone

from tournament.models import Tournament, Participant

def index(request):
    frm = request.session.get('from', '')
    request.session['from'] = ''
    request.session.save()

    return render(request, 'index.html', {"from": frm})


def redirect_view(request):
    if request.path not in ['/worker.js','favicon.ico']:
        request.session['from'] = request.path or ''
    return redirect('/')

@login_required
def register(request):
    if request.method == "POST":
        t = Tournament.objects.get(pk=request.POST.get('tournament'))
        if "Junior" in t.name:
            tournaments = Tournament.objects.filter(name__icontains="Junior")
            if Participant.objects.filter(
                    Q(user=request.user) &  Q(tournament__in=tournaments)
            ).exists():
                
                tournaments = Tournament.objects.filter(start_date__gte=timezone.now()
                ).annotate(
                    registered=Case(
                        When(participants__user=request.user, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    )
                )
                return render(request, 'profiles/index.html', {"tournaments": tournaments, "error": "You are already registered"})
            
        Participant.objects.create(
            user=request.user, tournament=t,name=request.user.profile.preferred_name,
        )
        return redirect('/profile/')
    
    
    t = Tournament.objects.filter(registration_open=True)
    return render(request, 'profiles/index.html', {"tournaments": t})