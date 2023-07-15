"""
Views for creating, editing and viewing site-specific user profiles.

"""
import json

from django.db.models.signals import post_save
from django.db.models.aggregates import Count
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from django.conf import settings
from django.dispatch.dispatcher import receiver

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.urls import reverse, reverse_lazy

from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect

from allauth.account.models import EmailAddress

from profiles.models import UserProfile, Avatar, PhoneNumber, SnailMail,\
    BankAccount


from profiles.forms import ProfileForm, DpForm, AddNumberForm, VerifyNumberForm,\
    PostalForm, BankForm, NotificationForm


def resend_confirmation(request):
    '''
    Sends an email address confirmation link. 
    Intended to be invoked over ajax
    '''
    if request.method == 'POST' and request.user.is_authenticated() :
        user = request.user
        if user.emailaddress_set.count() == 0 :
            EmailAddress.objects.create(user = user, email = user.email)

        em = user.emailaddress_set.filter(verified = False)[0]
        em.send_confirmation(request)
        return HttpResponse(json.dumps({'status': 'Ok'}))
        
    return HttpResponse(json.dumps({'status': 'error'}))


@login_required
def edit_profile(request,     template_name='edit_profile.html'):
    """
    Edit the current user's profile.
    """
    user = request.user
    profile_obj = user.userprofile
    
    if request.method == 'POST':
        #
        # See the comment in create_profile() for discussion of why
        # success_url is set up here, rather than as a default value for
        # the argument.
        #
        
        success_url = reverse('profiles_profile_detail',
                                  kwargs={ 'username': user.username })
        form = ProfileForm(data=request.POST, files=request.FILES, instance=profile_obj)

        if form.is_valid():
            form.save();

            u = user;            
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.save()

            return HttpResponseRedirect(success_url)

    else:
        form = ProfileForm(instance=profile_obj)
    
    avatars = Avatar.objects.filter(user_id = user.id).order_by('-is_main','-id') 
    if not avatars :
        avatars = [ {'id': 'default','is_main': True, 
                      'photo_link': profile_pic(request.user, no_html = True, no_resize = True) } ]
        
    extra_f = request.GET.get('selenium_patch') == 'BaDskype' and settings.DEBUG
    
    return render_to_response(template_name,
                                  { 'form': form, 'avatars': avatars, 'extra_file_input': extra_f,
                                'profile': profile_obj, 'cb': sso_util.generate_callback_string(user.id)},
                              context_instance = RequestContext(request))
    

def profile_link(request, username):
    '''
    To avoid complications like javascript injection etc, the link 
    is always to this place which will do a redirect
    '''
    
    try:
        profile = UserProfile.objects.get(user__username = username)
        if profile.website_url :
            return HttpResponseRedirect(profile.website_url)
        else :
            raise Exception

    except ObjectDoesNotExist:
        raise Http404
    except Exception:
        return render_to_response('invalid_link.html', {'user': profile.user},
                                   context_instance = RequestContext(request))

def reset_verifications_cache(user):
    '''
    List, when an email address is updated in the db the cache should be reset
    '''
    key = 'uSr:vrfy:{0}'.format(user.id)
    cache.delete(key)
    
    
def get_verifications(user):
    key = 'uSr:vrfy:{0}'.format(user.id)
    verifications = cache.get(key)
    if not verifications :
        verifications = {'email': user.emailaddress_set.filter(verified = True).count() > 0,
                 'phone': user.phonenumber_set.filter(verified = True).count() > 0,
                 'bank': user.bankaccount_set.filter(verified = True).count() > 0,
                 'snailmail': user.snailmail_set.filter(verified = True).count() > 0 }
    
        cache.set(key, verifications)
        
    return verifications
    

def profile_detail(request, username):
    """
    Detail view of a user's profile.
    There are two possibilities. 
      1) THe user wants to see his profile: All the dirty details will be exposed
      2) A user wants to see someone else's profile - only a limited amount of info shown.
      3) the user requests his public profile which will be the same as item number 2
    """
    try :
        user = User.objects.filter(username = username).select_related('userprofile')[0]
    except Exception:
        raise Http404


    context = {'profile': user.userprofile,
               'accounts' : user.socialaccount_set.all(),
               'verifications' : get_verifications(user) }
    
    if request.user.username != username or request.GET.get('public'):
        # trying to see someone else's profile
        return render_to_response('profile_public.html', context, context_instance = RequestContext(request))
    else :
        context['phone'] = user.phonenumber_set.all()    
        return render_to_response('profile_detail.html', context, context_instance = RequestContext(request))
  


def profile_list(request):
    if request.user.is_authenticated() :
        return HttpResponseRedirect("/profile/%s/" % request.user.username);
    else :
        return HttpResponseRedirect('/badges/scores/')
    
   
def dp_select(request):
    if request.method == 'POST':
        try :
            av = Avatar.objects.get(user_id = request.user.id, id = request.POST.get('id'))
            if av :
                Avatar.objects.filter(user_id = request.user.id).exclude(id = av.id).update(is_main = False)
                av.is_main = True
                av.save()
                return HttpResponse(json.dumps({'status':'Ok'}))
        except Exception:
            pass
        
    return HttpResponse(json.dumps({'status':'error'}))


def dp_add(request):
    '''
    Adds a new profile picture
    '''
    f = DpForm(request.POST)
            
    try :
        if request.user.is_authenticated() and f.is_valid():

            image_url = f.cleaned_data['image_url']
            if image_url.startswith('https') :
                # only https urls are allowed 
            
                av = Avatar.objects.create(user = request.user, photo_link = image_url, is_main = True)
                Avatar.objects.filter(user = request.user).exclude(id = av.id).update(is_main = False)
                
                message = render_to_string('profile_pics.html', {'avatars': [av] }  )
                return HttpResponse(json.dumps({'status': 'Ok', 'message': message}))
        
    except Exception:
        import traceback
        traceback.print_exc
        pass
    
    return HttpResponse(json.dumps({'status': 'error'}))
    
    
def profile_pics(uid):
    '''
    Shows a collection of the current user's profile pics (any of which
    he may choose as his default profile pic)
    '''
    
    avatars = Avatar.objects.filter(user_id = uid)
    return render_to_string('profile_pics.html',{ 'avatars': avatars })


def dp_change(request):
    '''
    Endoint for mobiles where the dp change is a separate page on it's own but
    the functionality is a subset of edit_profile() so let's call it with the
    right params 
    '''
    return edit_profile(request, template_name='dp_selector.html')


@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request,
                    template_name='account/password_change.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = "/profile/{0}/".format(request.user.username)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@login_required
def change_settings(request):
    '''
    Changes the user's settings. 
    Which at the moment just means the notification settings
    '''
    if request.method == 'GET':
        initial = request.user.userprofile.user_preferences
        
        
        return render_to_response('profiles/settings.html', { 'form': form, 'show': initial['send_mail']},
                                  context_instance = RequestContext(request))
    
    else :
        try :
            prefs = request.user.userprofile.user_preferences
            prefs.set_notifications(request.POST.get('send_mail'))
            prefs.set_promotional(request.POST.get('promotional','') == 'on')
            request.user.userprofile.user_preferences = prefs
            request.user.userprofile.save()
        
            return HttpResponseRedirect('/profile/edit/')
        except :
            return render_to_response('profiles/settings.html', { 'form': form },
                                  context_instance = RequestContext(request))
