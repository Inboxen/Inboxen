import hashlib, time, random

from django.shortcuts import render
from django.http import Http404
from django.contrib.auth import logout
from django.template import RequestContext
from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from inboxen.models import Domain, Alias

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect('/profile')
    else:
        form = UserCreationForm()
    
    context = {
        "form":form,
        "page":"Register",
    }

    return render(request, "register.html", context, context_instance=RequestContext(request))

@login_required
def add_alias(request):
    alias = "%s-%s" % (time.time(), request.user.username) 
    domains = Domain.objects.all()
    
    alias = ""
    count = 0
    while not alias and count < 10:
        alias = "%s-%s" % (time.time(), request.user.username)
        alias = hashlib.sha1(alias).hexdigest()[:count+5]
        try:
            Alias.objects.get(alias=alias)
            alias = ""
            count += 1
        except:
            pass
    context = {
        "page":"Add Alias",
        "domains":domains,
        "alias":alias,
    }
    
    return render(request, "add_alias.html", context)

@login_required
def settings(request):
   
    context = {
        "page":"Settings",
    }

    return render(request, "settings.html", context)

@login_required
def logout_user(request):
    
    logout(request)
    return HttpResponseRedirect("/")

@login_required
def profile(request):

    context = {
        "page":"Profile",
    }
    
    return render(request, "profile.html", context)

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    context = {
        "page":"Login",
    } 

    return render(request, "login.html", context)

def contact(request):
    context ={
        "page":"Contact",
    }

    return render(request, "contact.html", context)

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    context = {
        "page":"Home",
    }

    return render(request, "index.html", context)
