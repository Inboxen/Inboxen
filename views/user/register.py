##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm

def status(request):
    context = {
        "page":_("We're not stable!"),
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    return render(request, "user/software-status.html", context)

def success(request):

    context = {
        "page":_("Welcome!")
    }

    return render(request, "user/register/success.html", context)

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/user/home")

    if not settings.ENABLE_REGISTRATION:
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/user/register/success")
    else:
        form = UserCreationForm()
    
    context = {
        "form":form,
        "page":_("Register"),
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    return render(request, "user/register/register.html", context, context_instance=RequestContext(request))

