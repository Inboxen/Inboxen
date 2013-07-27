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
from django.contrib.auth.decorators import login_required
from django.http import Http404

from inboxen.models import Alias, Email, Domain
from website.helper.mail import get_email, clean_html

@login_required
def view(request, email_address, emailid):

    alias, domain = email_address.split("@", 1)
    support = False
    
    # support stuff
    if request.user.is_staff and alias == "support":
        alias = Alias.objects.filter(alias=alias)[0]
        support = True
    else:
        try:
            alias = Alias.objects.get(alias=alias, domain__domain=domain, user=request.user)
        except Alias.DoesNotExist:
            raise Http404
    try:
        email = get_email(request.user, emailid, read=True)
    except Email.DoesNotExist:
        raise Http404

    from_address = email["from"].split("@", 1)
    if from_address[0] == "support" and Domain.objects.filter(domain=from_address[1]).exists():
        support = True

    if email["plain"]:
        plain_message = email["body"]
    else:
        plain_message = ""
        # also because a html email lets parse
        if "body" in email:
            email["body"] = clean_html(email["body"])
        else:
            email["body"] = "" # emails can have no body

    context = {
        "page":email["subject"],
        "email":email,
        "plain_message":plain_message,
        "support":support,
    }
 
    return render(request, "inbox/email.html", context)
