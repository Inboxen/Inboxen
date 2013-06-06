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

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from website.models import Request
from website.helper.user import user_profile
from website.helper.alias import alias_available


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
