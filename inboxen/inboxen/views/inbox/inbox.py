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
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist

from inboxen.models import Alias, Email
from inboxen.helper.paginator import page as paginator_page

@login_required
def inbox(request, email_address="", page=1):
    if not email_address:
        # assuming global unified inbox
        inbox = Email.objects.filter(user=request.user).order_by('-recieved_date')

    else:
        # a specific alias
        alias, domain = email_address.split("@", 1)
        try:
            alias = Alias.objects.get(user=request.user, alias=alias, domain__domain=domain)
            inbox = Email.objects.filter(user=request.user, inbox=alias).order_by('-recieved_date')
        except ObjectDoesNotExist:
            context = {
                "page":"%s - Inbox" % email_address,
                "error":"Can't find email address",
                "emails":[],
                "email_address":email_address,
            }
            
            return render(request, "inbox/inbox.html", context)

    paginator = Paginator(inbox, 100)

    try:
        emails = paginator.page(page)
    except PageNotAnInteger: # sometimes it's None
        emails = paginator.page(1)
    except EmptyPage: # sometimes the user will try different numbers
        emails = paginator.page(paginator.num_pages)

    # lets add the important headers (subject and who sent it (a.k.a. sender))
    for email in emails.object_list:
        email.sender, email.subject = "", "(No Subject)"
        for header in email.headers.all():
            if header.name == "From":
                email.sender = header.data
            elif header.name == "Subject":
                email.subject = header.data

    if email_address:
        page = "%s - Inbox" % email_address
    else:
        page = "Inbox"

    context = {
        "page":page,
        "error":"",
        "emails":emails,
        "email_address":email_address,
        "pages":paginator_page(emails),
    }
    
    return render(request, "inbox/inbox.html", context)
