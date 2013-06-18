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

from datetime import datetime

from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from website.helper.alias import alias_available, clean_tags, gen_alias
from inboxen.models import Domain, Alias, Tag

@login_required
def add(request):

    available = alias_available(request.user)
    if not available:
        return HttpResponseRedirect("/email/request")

    if request.method == "POST":
        alias = request.POST["alias"]
        domain = Domain.objects.get(domain=request.POST["domain"])
        tags = request.POST["tag"]
        
        try:
            alias_test = Alias.objects.get(alias=alias, domain=domain)
            return HttpResponseRedirect("/user/profile")
        except Alias.DoesNotExist:
            pass 

        new_alias = Alias(alias=alias, domain=domain, user=request.user, created=datetime.now(utc))
        new_alias.save()
        
        tags = clean_tags(tags)
        for i, tag in enumerate(tags):
            tag = Tag(tag=tag)
            tag.alias = new_alias
            tag.save()
            tags[i] = tag

        msg = _("You have successfully created %s!") % new_alias

        request.session["messages"] = [msg]

        return HttpResponseRedirect("/user/profile")

    domains = Domain.objects.all()
    
    alias = gen_alias(5)
            
    context = {
        "page":_("Add Alias"),
        "domains":domains,
        "alias":alias,
    }
    
    return render(request, "email/add.html", context)
