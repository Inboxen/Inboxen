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

from pytz import utc

from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from website.helper.inbox import inbox_available, clean_tags, gen_inbox
from inboxen.models import Domain, Inbox, Tag

@login_required
def add(request):

    available = inbox_available(request.user)
    if not available:
        return HttpResponseRedirect("/email/request")

    if request.method == "POST":
        inbox = request.POST["inbox"]
        domain = Domain.objects.get(domain=request.POST["domain"])
        tags = request.POST["tag"]
        
        if Inbox.objects.filter(inbox=inbox, domain=domain).exists():
            return HttpResponseRedirect("/user/home")

        new_inbox = Inbox(inbox=inbox, domain=domain, user=request.user, created=datetime.now(utc))
        new_inbox.save()
        
        tags = clean_tags(tags)
        for i, tag in enumerate(tags):
            tag = Tag(tag=tag)
            tag.inbox = new_inbox
            tag.save()
            tags[i] = tag

        msg = _("You have successfully created %s!") % new_inbox

        request.session["messages"] = [msg]

        return HttpResponseRedirect("/user/home")

    domains = Domain.objects.all()
    
    inbox = gen_inbox(5)
            
    context = {
        "page":_("Add Inbox"),
        "domains":domains,
        "inbox":inbox,
    }
    
    return render(request, "email/add.html", context)
