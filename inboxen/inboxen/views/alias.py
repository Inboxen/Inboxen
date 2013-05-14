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

import time, string, random
from datetime import datetime

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from inboxen.models import Email, Domain, Alias, Tag
from inboxen.helper.alias import delete_alias

def gen_alias(count, alias=""):
    if count <= 0:
        return alias
    
    alias += random.choice(string.ascii_lowercase)
    
    return gen_alias(count-1, alias)

@login_required
def add_alias(request):
    
    if request.method == "POST":
        alias = request.POST["alias"]
        domain = Domain.objects.get(domain=request.POST["domain"])
        tags = request.POST["tag"]

        # if there are no , then we'll assume a space sporated list
        if "," in tags:
            tags = tags.split(", ")
        else:
            tags = tags.split() # split on space
        
        try:
            alias_test = Alias.objects.get(alias=alias, domain=domain)
            return HttpResponseRedirect("/profile")
        except Alias.DoesNotExist:
            pass 

        new_alias = Alias(alias=alias, domain=domain, user=request.user, created=datetime.now())
        new_alias.save()
        
        for i, tag in enumerate(tags):
            tag = tag.rstrip(" ").lstrip(" ")
            tags[i] = Tag(tag=tag)
            tags[i].alias = new_alias
            tags[i].save()
 
        return HttpResponseRedirect("/profile")

    domains = Domain.objects.all()
    
    alias = ""
    count = 0
    
    min_length = 5 # minimum length of alias
    
    while not alias and count < 15:
        alias = gen_alias(count+min_length)
        try:
            Alias.objects.get(alias=alias)
            alias = ""
            count += 1
        except Alias.DoesNotExist:
            pass
            
    context = {
        "page":"Add Alias",
        "domains":domains,
        "alias":alias,
    }
    
    return render(request, "add_alias.html", context)
    
@login_required
def confirm_delete(request, email):
    if request.method == "POST":
        if request.POST["confirm"] != email:
            raise Http404
        else:
            if not delete_alias(email, request.user):
                raise Http404

        return HttpResponseRedirect("/profile")
    
    context = {
        "page":"Delete Alias",
        "alias":email
    }

    return render(request, "confirm.html", context)
