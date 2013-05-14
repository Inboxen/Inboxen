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

from inboxen.models import Email, Domain, Alias, Tag, Request
from inboxen.helper.alias import delete_alias, find_alias, clean_tags, alias_available
from inboxen.helper.user import user_profile

def gen_alias(count, alias=""):
    if count <= 0:
        return alias
    
    alias += random.choice(string.ascii_lowercase)
    
    return gen_alias(count-1, alias)

@login_required
def request(request):
    available = alias_available(request.user)
    prior_requests = Request.objects.filter(requester=request.user).order_by('-date')

    if available > 10:
        context = {
            "error":"You need to have less than 10 aliases available to request more, you currently have %s available." % available,
            "page":"Request",
            "request":None,
            "prior_requests":prior_requests,
        }

        return render(request, 'email/request.html', context)

    if request.method == "POST":
        # lets first deduce what amount to request
        profile = user_profile(request.user)
        amount = profile.pool_amount + 500
        current_request = Request(amount=amount, date=datetime.now())
        current_request.requester = request.user
        current_request.save()

        return HttpResponseRedirect("/email/request/")


    if prior_requests.filter(succeeded=None):
        current_request = False
    else:
        current_request = True

    context = {
        "page":"Request",
        "request":current_request,
        "prior_requests":prior_requests,
    }

    return render(request, "email/request.html", context)

@login_required
def add_alias(request):

    available = alias_available(request.user)
    if not available:
        return HttpResponseRedirect("/email/request")

    if request.method == "POST":
        alias = request.POST["alias"]
        domain = Domain.objects.get(domain=request.POST["domain"])
        tags = request.POST["tag"]

        # if there are no , then we'll assume a space sporated list
        
        try:
            alias_test = Alias.objects.get(alias=alias, domain=domain)
            return HttpResponseRedirect("/user/profile")
        except Alias.DoesNotExist:
            pass 

        new_alias = Alias(alias=alias, domain=domain, user=request.user, created=datetime.now())
        new_alias.save()
        
        tags = clean_tags(tags)
        for i, tag in enumerate(tags):
            tag = Tag(tag=tag)
            tag.alias = new_alias
            tag.save()
            tags[i] = tag

 
        return HttpResponseRedirect("/user/profile")

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
    
    return render(request, "email/add.html", context)

@login_required
def edit(request, email):

    alias = find_alias(email, user=request.user, deleted=False)

    if not alias:
        # display a proper error here?
        return HttpResponseRedirect("/user/profile")
    else:
        alias = alias

    if request.method == "POST":
        if "tags" in request.POST and request.POST["tags"]:
            tags = clean_tags(request.POST["tags"])

            # remove old tags
            for old_tag in Tag.objects.filter(alias=alias[0]):
                old_tag.delete()

            for i, tag in enumerate(tags):
                tags[i] = Tag(tag=tag)
                tags[i].alias = alias[0]
                tags[i].save()


        return HttpResponseRedirect("/user/profile")

    tags = Tag.objects.filter(alias=alias[0])
    display_tags = ""
    for tag in tags:
        display_tags += ", %s" % str(tag)


    context = {
        "page":"Edit %s" % email,
        "email":email,
        "alias":alias[0].alias,
        "domain":alias[1],
        "tags":display_tags[2:],
    }

    return render(request, "email/edit.html", context)

@login_required
def confirm_delete(request, email):
    if request.method == "POST":
        if request.POST["confirm"] != email:
            raise Http404
        else:
            if not delete_alias(email, request.user):
                raise Http404

        return HttpResponseRedirect("/user/profile")
    
    context = {
        "page":"Delete Alias",
        "alias":email
    }

    return render(request, "email/delete/confirm.html", context)
