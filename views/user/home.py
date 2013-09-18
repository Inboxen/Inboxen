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

from inboxen.helper.inbox import inbox_available
from inboxen.helper.paginator import page as page_paginator
from inboxen.models import Inbox, Tag, Email

@login_required
def home(request, page=1):

    inboxes = Inbox.objects.filter(user=request.user).order_by('-created')
    available = inbox_available(request.user, inboxes=inboxes)
    used = inboxes.count()
    inboxes = inboxes.filter(deleted=False)

    total = 0
    for inbox in inboxes:
        try:
            tag = Tag.objects.filter(inbox=inbox)
            inbox.tags = ", ".join([t.tag for t in tag])
        except Tag.DoesNotExist:
            inbox.tags = ''
        inbox.email_count = Email.objects.filter(inbox=inbox, read=False, deleted=False).count()
        total += inbox.email_count

    paginator = Paginator(inboxes, 20)

    try:
        inboxes = paginator.page(page)
    except PageNotAnInteger: # sometimes it's None
        inboxes = paginator.page(1)
    except EmptyPage: # sometimes the user will try different numbers
        inboxes = paginator.page(paginator.num_pages)

    messages = ""
    if "messages" in request.session and request.session["messages"]:
        messages = request.session["messages"].pop()
        request.session["messages"] = []

    context = {
        "page":_("Home"),
        "inboxes":inboxes,
        "available":available,
        "total_email_count":total,
        "pages":page_paginator(inboxes),
        "notify_messages":messages,
        "user":request.user,
    }

    
    return render(request, "user/home.html", context)
    

