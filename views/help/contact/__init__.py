##
#    Copyright (C) 2013 Jessica Tallon & Matthew Molyneaux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
from datetime import datetime

from pytz import utc

from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect

from inboxen.helper.inbox import gen_inbox
from inboxen.helper.mail import send_email 
from inboxen.models import Domain, Inbox, Tag

def contact(request):

    context = {
        "page":_("Contact"),
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    if request.method == "POST":
        send_to = Inbox.objects.filter(inbox="support")[0]
        
        if request.user.is_authenticated():
            # For users of the site :)
            try:
                inbox = request.POST["inbox"]
                domain = Domain.objects.get(domain=request.POST["domain"])
                subject = request.POST["subject"]
                body = request.POST["body"]
            except KeyError:
                # really should produce an error
                return HttpResponseRedirect("/help/contact/")


            inbox = Inbox(
                inbox=inbox,
                domain=domain,
                user=request.user,
                created=datetime.now(utc)
            )

            inbox.save()

            tag = Tag(inbox=inbox, tag=_("Support Request"))
            tag.save()

            send_email(
                send_to,
                inbox,
                subject,
                body,
            )
            return HttpResponseRedirect("/help/contact/success")
        else:
            # they're not logged in.
            try:
                email = request.POST["email"]
                subject = request.POST["subject"]
                body = request.POST["body"]
            except KeyError:
                # really should produce an error
                return HttpResponseRedirect("/help/contact/")

            send_email(
                send_to,
                email,
                subject,
                body,
            )
            return HttpResponseRedirect("/help/contact/success")


    # If the user is authenticated we want to give them the option of
    # generating a auto-tagged new inbox
    if request.user.is_authenticated:
        # lets generate a new inbox for them
        new_inbox = gen_inbox(5)
        domains = Domain.objects.all()
        context["inbox"] = new_inbox
        context["domains"] = domains

    return render(request, "help/contact/contact.html", context)
