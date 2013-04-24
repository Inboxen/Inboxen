from django.shortcuts import render
from django.http import HttpResponseRedirect

def contact(request):
    context ={
        "page":"Contact",
    }

    return render(request, "contact.html", context)

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/profile")

    context = {
        "page":"Home",
    }

    return render(request, "index.html", context)
