from django.shortcuts import render
from django.http import Http404

from django.contrib.auth import logout
from django.template import RequestContext
from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm

def register(request):
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

def add_alias(request):
    context = {
        "page":"Add Alias",
    }
    
    return render(request, "add_alias.html", context)

def settings(request):
    context = {
        "page":"Settings",
    }
    return render(request, "settings.html", context)

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

def profile(request): 
    context = {
        "page":"Profile",
    }
    
    return render(request, "profile.html", context)

def login(request):
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
    context = {
        "page":"Home",
    }

    return render(request, "index.html", context)
