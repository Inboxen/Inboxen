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
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from website.tasks import delete_alias
from inboxen.models import Alias

@login_required
def confirm(request, email):
    if request.method == "POST":
        if request.POST["confirm"] != email:
            raise Http404
        else:
            # set it to deleted first
            alias, domain = email.split("@", 1)
            alias = Alias.objects.get(alias=alias, domain__domain=domain)
            alias.deleted = True
            alias.save()
            # throw to queue
            delete_alias.delay(email, request.user)
            # send back to profile page
            return HttpResponseRedirect("/user/profile") 

        return HttpResponseRedirect("/user/profile")
    
    context = {
        "page":"Delete Alias",
        "alias":email
    }

    return render(request, "email/delete/confirm.html", context)
