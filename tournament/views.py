from django.shortcuts import render, redirect
# Create your views here.

def index(request):
    frm = request.session.get('from')
    request.session['from'] = ''
    return render(request, 'index.html', {"from": frm})


def redirect_view(request):
    print(request.path)
    request.session['from'] = request.path or ''
    return redirect('/')