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
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from queue.delete.tasks import delete_inbox
from inboxen.models import Inbox

@login_required
def confirm(request, email):
    if request.method == "POST":
        if request.POST["confirm"] != email:
            raise Http404
        else:
            # set it to deleted first
            inbox, domain = email.split("@", 1)
            try:
                inbox = request.user.inbox_set.get(inbox=inbox, domain__domain=domain)
            except Inbox.DoesNotExist:
                raise Http404

            inbox.deleted = True
            inbox.save()

            delete_inbox.delay(email, request.user)
            message = _("The inbox %s@%s has now been deleted.") % (inbox.inbox, inbox.domain)
            request.session["messages"] = [message]

            return HttpResponseRedirect("/user/home") 

        return HttpResponseRedirect("/user/home")
    
    context = {
        "page":_("Delete Inbox"),
        "inbox":email
    }

    return render(request, "email/delete/confirm.html", context)
