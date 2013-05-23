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

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect

from inboxen.helper.alias import gen_alias
from inboxen.helper.user import null_user
from inboxen.helper.email import send_email 
from inboxen.models import Domain, Alias, Tag

def contact(request):

    context = {
        "page":"Contact",
        "registration_enabled":settings.ENABLE_REGISTRATION,
    }

    if request.method == "POST":
        try:
            send_to = Alias.objects.get(alias="support")
        except Alias.MultipleObjectsReturned:
            send_to = Alias.objects.filter(alias="support")[0]
        except Alias.DoesNotExist:
            # make it.
            domains = Domain.objects.all()
            for domain in domains:
                send_to = Alias(
                    alias="support",
                    domain=domain,
                    user=null_user(),
                    created=datetime.now(utc),
                )
                send_to.save()


    if request.method == "POST" and request.user.is_authenticated():
        # For users of the site :)
        try:
            alias = request.POST["alias"]
            domain = Domain.objects.get(domain=request.POST["domain"])
            subject = request.POST["subject"]
            body = request.POST["body"]
        except KeyError:
            # really should produce an error
            return HttpResponseRedirect("/help/contact/")


        alias = Alias(
            alias=alias,
            domain=domain,
            user=request.user,
            created=datetime.now(utc)
        )

        alias.save()
        
        tag = Tag(alias=alias, tag="Support Request")
        tag.save()

        send_email(
            request.user,
            send_to,
            alias,
            subject,
            body,
        )
    elif request.method == "POST":
        # they're not logged in.
        try:
            email = request.POST["email"]
            subject = request.POST["subject"]
            body = request.POST["body"]
        except KeyError:
            # really should produce an error
            return HttpResponseRedirect("/help/contact/")

        send_email(
            null_user(), # null user
            send_to,
            email,
            subject,
            body,
        )
        return HttpResponseRedirect("/help/contact/success")


    # If the user is authenticated we want to give them the option of
    # generating a auto-tagged new alias
    if request.user.is_authenticated:
        # lets generate a new alias for them
        new_alias = gen_alias(5)
        domains = Domain.objects.all()
        context["alias"] = new_alias
        context["domains"] = domains

    return render(request, "help/contact/contact.html", context)