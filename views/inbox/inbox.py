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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q

from inboxen.models import Inbox, Email
from queue.tasks import delete_email
from website.helper.paginator import page as paginator_page

@login_required
def inbox(request, email_address="", page=1):
    if request.method == "POST":
        # deal with tasks, then show the page as normal
        mass_tasks(request)

    if not email_address:
        # assuming global unified inbox
        inbox = Email.objects.filter(user=request.user, deleted=False).defer('body').order_by('-recieved_date')

    else:
        # a specific inbox
        inbox, domain = email_address.split("@", 1)
        try:
            inbox = Inbox.objects.get(user=request.user, inbox=inbox, domain__domain=domain)
            inbox = Email.objects.filter(user=request.user, inbox=inbox, deleted=False).defer('body').order_by('-recieved_date')
        except ObjectDoesNotExist:
            context = {
                "page":_("%s - Inbox") % email_address,
                "error":_("Can't find email address"),
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
        email.sender, email.subject = "", _("(No Subject)")
        for header in email.headers.all():
            if header.name == "From":
                email.sender = header.data
            elif header.name == "Subject" and header.data:
                email.subject = header.data

    if email_address:
        page = _("%s - Inbox") % email_address
    else:
        page = _("Inbox")

    context = {
        "page":page,
        "error":"",
        "emails":emails,
        "email_address":email_address,
        "pages":paginator_page(emails),
    }
    
    return render(request, "inbox/inbox.html", context)

@transaction.commit_on_success
def mass_tasks(request):
    emails = Q()
    for email in request.POST:
        if request.POST[email] == "email":
            try:
                email_id = int(email, 16)
                emails = emails | Q(id=email_id)
            except (Email.DoesNotExist, ValueError):
                # TODO: non-silent failure?
                return

    # update() & delete() like to do a select first for some reason :s
    emails = Email.objects.filter(emails, user=request.user).only('id','read')

    if "read" in request.POST:
        emails.update(read=True)
    elif "unread" in request.POST:
        emails.update(read=False)
    elif "delete" in request.POST:
        emails.update(deleted=True)
        for email in emails:
            delete_email.apply_async(email.id)
