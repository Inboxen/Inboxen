from django.shortcuts import render
from django.http import Http404

def profile(request):
    
    context = {}
    
    return render(request, "profile.html", context)

def login(request):
    
    context = {}

    return render(request, "login.html", context)

def home(request):
    
    context = {
    
    }

    return render(request, "index.html", context)
