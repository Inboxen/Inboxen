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

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings

from inboxen.models import Alias

@login_required
@require_POST
def reply(request):

    context = {
        "page":_("Contact"),
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    if "inbox" in request.POST and "from" in request.POST:
        to_address = request.POST["inbox"]
        from_address = request.POST["from"]

        context["reply"] = True
        context["reply_to"] = to_address
        context["reply_from"] = from_address

        return render(request, "help/contact/contact.html", context)

    elif "reply-to" in request.POST and "reply-from" in request.POST:
        reply_to = request.POST["reply-to"].split('@')
        reply_from = request.POST["reply-from"]i.split('@')
        try:
            subject = request.POST["subject"]
            body = request.POST["body"]
        except KeyError:
            return HttpResponseRedirect("/help/contact/reply")

        reply_to = Alias.objects.get(
                alias = reply_to[0]
                domain__domain = reply_to[1]
                )
        reply_from = Alias.objects.get(
                alias = reply_from[0]
                domain__domain = reply_from[1]
                )

        send_email(
            reply_from,
            reply_to,
            subject,
            body
            )

        return HttpResponseRedirect("/help/contact/success")

    else:
        return HttpResponseRedirect("/")
