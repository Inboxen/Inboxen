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
from django.db import transaction
from django.db.models import F, Q

from inboxen.helper.paginator import page as paginator_page
from inboxen.models import Inbox, Email
from queue.delete.tasks import delete_email

INBOX_ORDER = {
                '+date':    'received_date',
                '-date':    '-received_date',
}

@login_required
def inbox(request, email_address="", page=1):
    if request.method == "POST":
        # deal with tasks, then show the page as normal
        mass_tasks(request)

    order = request.GET.get('sort','-date')
    emails = Email.objects.filter(inbox__user=request.user, flags=~Email.flags.deleted)

    if len(email_address):
        # a specific inbox
        inbox, domain = email_address.split("@", 1)
        emails = emails.filter(inbox__inbox=inbox, inbox__domain__domain=domain)

    emails.order_by(INBOX_ORDER[order])

    paginator = Paginator(emails, 100)

    try:
        emails = paginator.page(page)
    except PageNotAnInteger: # sometimes it's None
        emails = paginator.page(1)
    except EmptyPage: # sometimes the user will try different numbers
        emails = paginator.page(paginator.num_pages)

    # lets add the important headers (subject and who sent it (a.k.a. sender))
    headers = Header.objects.filter(part__ordinal=0, part__email__in=emails.object_list)
    headers = headers.filter(Q(header_name_name="Subject")|Q(header__name__name="From"))
    headers = headers.values_list("part__email__id", "name__name", "data__data")

    sort_headers = {}
    for header in headers:
        items = sorted_headers.get(header[0], {})
        items[header[1]] = header[2]
        sort_headers[header[0]] = items

    for email in emails.object_list:
        headers = sort_headers[email.id]
        email.subject = headers["Subject"]
        email.sender = headers["From"]

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
        "user":request.user,
    }

    return render(request, "inbox/inbox.html", context)

@transaction.atomic()
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
        emails.update(flags=F('flags').bitor(Email.flags.read))
    elif "unread" in request.POST:
        emails.update(flags=F('flags').bitand(~Email.flags.read))
    elif "delete" in request.POST:
        emails.update(flags=F('flags').bitor(Email.flags.deleted))
        for email in emails:
            delete_email.delay(email.id)
