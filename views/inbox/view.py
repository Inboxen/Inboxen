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
from django.db.models import F

from inboxen.models import Email

@login_required
def view(request, email_address, emailid):
    try:
        inbox = request.user.inbox_set.from_string(email=email_address)

        email = int(emailid, 16)
        email = Email.objects.get(id=email, flags=~Email.flags.deleted)
    except (Email.DoesNotExist, Inbox.DoesNotExist):
        return Http404

    email_obj = None #TODO

    email.update(flags=F('flags').bitand(Email.flags.read))

    context = {
        "page":email_obj.subject,
        "email":email_obj,
        "plain_message":plain_message,
        "user":request.user,
    }
 
    return render(request, "inbox/email.html", context)
