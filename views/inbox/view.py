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

from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from inboxen.models import Alias, Email
from website.helper.mail import get_email, clean_html

@login_required
def view(request, email_address, emailid):

    alias, domain = email_address.split("@", 1)
    
    # support stuff
    if request.user.is_staff and alias == "support":
        alias = Alias.objects.filter(alias=alias)[0]
    else:
        try:
            alias = Alias.objects.get(alias=alias, domain__domain=domain, user=request.user)
        except Alias.DoesNotExist:
            pass
    try:
        email = get_email(request.user, emailid, read=True)
    except Email.DoesNotExist:
        raise
        return HttpResponseRedirect("")

    if "plain" in email:
        plain_message = email["plain"]
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
    }
 
    return render(request, "inbox/email.html", context)
