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

from inboxen.models import Domain, Inbox, Tag

@login_required
def add(request):

    available = request.user.userprofile.available_inboxes()
    if available > 0:
        msg = _("You have used too many Inboxes")
        request.session["messages"] = [msg]

        return HttpResponseRedirect("/user/home")

    if request.method == "POST":
        domain = Domain.objects.get(domain=request.POST["domain"])
        tags = request.POST["tags"]

        new_inbox = request.user.inbox_set.create(domain=domain)

        tags = Tag.objects.from_string(tags=tags, inbox=new_inbox)

        msg = _("You have successfully created %s!") % new_inbox

        request.session["messages"] = [msg]

        return HttpResponseRedirect("/user/home")

    domains = Domain.objects.all()

    context = {
        "page":_("Add Inbox"),
        "domains":domains,
    }

    return render(request, "email/add.html", context)
