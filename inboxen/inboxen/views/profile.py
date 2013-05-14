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


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator

from django.contrib.auth.models import Group
from inboxen.models import Alias, Tag
from inboxen.helper.user import user_profile

@login_required
def settings(request):
    error = ""
    
    # check their html preferences
    profile = user_profile(request.user)
    
    # they submitting it?
    if request.method == "POST":
        try:
            spamfiltering = request.POST["spam_filtering"]
        except KeyError:
            spamfiltering = False

        sfg = Group.objects.get(name="SpamFiltering") # spam filtering group

        if spamfiltering and not request.user.groups.filter(name="SpamFiltering").exists():
            request.user.groups.add(sfg)
        elif not spamfiltering and request.user.groups.filter(name="SpamFiltering").exists():
            request.user.groups.remove(sfg)

        request.user.save()

        # Check if they wanted to change the password
        if "password1" in request.POST and "password2" in request.POST and request.POST["password1"]:
            if request.POST["password1"] == request.POST["password2"]:
                request.user.set_password(request.POST["password1"])
                request.user.save()
            else:
                # oh dear lets quickly say no
                error = "Passwords don't match"
        
        profile.html_preference = int(request.POST["html-preference"])
        profile.save()        
        
        if not error:
            # now redirect back to their profile
            return HttpResponseRedirect("/user/profile")


    # okay they're viewing the settings page
    # we need to load their settings first.
    if request.user.groups.filter(name="SpamFiltering").exists():
        sf = True
    else:
        sf = False

    context = {
        "page":"Settings",
        "spamfiltering":sf,
        "error":error,
        "htmlpreference":int(profile.html_preference),
    }

    return render(request, "user/settings.html", context)
    
@login_required
def profile(request, page=1):

    try:
        aliases = Alias.objects.filter(user=request.user).order_by('-created')
        used = aliases.count()
        aliases = aliases.filter(deleted=False)
    except Alias.DoesNotExist:
        raise
        aliases = []

    try:
        for alias in aliases:
            tag = Tag.objects.filter(alias=alias)
            alias.tags = ", ".join([t.tag for t in tag])
    except Tag.DoesNotExist:
        pass

    # work out alias stats
    pool = user_profile(request.user).pool_amount
    available = pool-used

    context = {
        "page":"Profile",
        "aliases":Paginator(aliases, 100).page(page),
        "available":available,
    }
    
    return render(request, "user/profile.html", context)
    

