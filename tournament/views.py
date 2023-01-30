from django.shortcuts import render, redirect
# Create your views here.

def index(request):
    frm = request.session.get('from', '')
    request.session['from'] = ''
    request.session.save()

    return render(request, 'index.html', {"from": frm})


def redirect_view(request):
    if request.path not in ['/worker.js','favicon.ico']:
        request.session['from'] = request.path or ''
    return redirect('/')