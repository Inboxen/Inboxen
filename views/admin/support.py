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
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from inboxen.models import Email, Inbox, Header


@login_required
@staff_member_required
def support(request, page=1):
    inbox = Inbox.objects.filter(inbox="support")
    q_inbox = Q()
    for a in inbox:
        q_inbox = q_inbox | Q(inbox=a)

    emails = Email.objects.filter(q_inbox, deleted=False).defer('body').order_by('-recieved_date')
    
    paginator = Paginator(emails, 100)
    try:
        emails = paginator.page(page)
    except PageNotAnInteger:
        emails = paginator.page(1)
    except EmptyPage:
        emails = paginator.page(paginator.num_pages)

    for email in emails.object_list:
        email.sender = email.headers.get(name="From").data
        try:
            email.subject = email.headers.get(name="Subject").data
        except Header.DoesNotExist:
            email.subject = _("(No Subject)")

    context = {
        "page":_("Support Inbox"),
        "emails":emails,
    }

    return render(request, "admin/support.html", context)
