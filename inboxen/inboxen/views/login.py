##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen front-end.
#
#    Inboxen front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen front-end.  If not, see <http://www.gnu.org/licenses/>.
##

from django.conf import settings
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
        "registration_enabled":settings.ENABLE_REGISTRATION,
    } 

    return render(request, "login.html", context)

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/profile")

    if not settings.ENABLE_REGISTRATION:
        return HttpResponseRedirect("/")

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
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    return render(request, "register.html", context, context_instance=RequestContext(request))
    
@login_required
def logout_user(request):
    
    logout(request)
    return HttpResponseRedirect("/")
