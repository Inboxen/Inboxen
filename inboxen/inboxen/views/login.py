from django.shortcuts import render
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/profile")

    context = {
        "page":"Login",
    } 

    return render(request, "login.html", context)

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/profile")

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
def logout_user(request):
    
    logout(request)
    return HttpResponseRedirect("/")
