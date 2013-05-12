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
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.http import HttpResponse, HttpResponseRedirect

from inboxen.models import Alias, Email, Attachment
from inboxen.helper.email import get_email 

@login_required
def download_attachment(request, attachment_id):
    try:
        attachment = Attachment.objects.get(id=attachment_id)
    except Exception:
        return HttpResponseRedirect("/")

    response = HttpResponse(attachment.data, content_type=attachment.content_type)
    response["Content-Disposition"] = "attachment; filename=bluhbluh-%s" % attachment_id

    return response

@login_required
def inbox(request, email_address="", page=1):

    error = ""

    if not email_address:
        # assuming global unified inbox
        inbox = Email.objects.filter(user=request.user).order_by('-recieved_date')

    else:
        # a specific alias
        alias, domain = email_address.split("@", 1)
        try:
            alias = Alias.objects.get(user=request.user, alias=alias, domain__domain=domain)
            inbox = Email.objects.filter(user=request.user, inbox=alias).order_by('-recieved_date')
        except:
            error = "Can't find email address"

    paginator = Paginator(inbox, 100)

    try:
        emails = paginator.page(page)
    except PageNotAnInteger:
        emails = paginator.page(1)
    except EmptyPage:
        emails = paginator.page(paginator.num_pages)

    # lets add the important headers (subject and who sent it (a.k.a. sender))
    for email in emails:
        email.sender, email.subject = "", "(No Subject)"
        for header in email.headers.all():
            if header.name == "From":
                email.sender = header.data
            elif header.name == "Subject":
                email.subject = header.data

    context = {
        "page":"%s - Inbox" % email_address,
        "error":error,
        "emails":emails,
        "email_address":email_address,
    }
    
    return render(request, "inbox.html", context)
    
@login_required
def read_email(request, email_address, emailid):

    alias, domain = email_address.split("@", 1)
    
    try:
        alias = Alias.objects.get(alias=alias, domain__domain=domain, user=request.user)
    except:
        return error_out(page="Inbox", message="Alias doesn't exist")

    try:
        email = get_email(request.user, emailid)
    except:
        raise
        return HttpResponseRedirect("")

    if "plain" in email:
        plain_message = email["plain"]
    else:
        plain_message = ""

    context = {
        "page":email["subject"],
        "email":email,
        "plain_message":plain_message,
    }
 
    return render(request, "email.html", context)
