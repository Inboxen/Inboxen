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

from website.helper.alias import alias_available
from website.helper.paginator import page as page_paginator
from inboxen.models import Alias, Tag, Email

@login_required
def profile(request, page=1):

    aliases = Alias.objects.filter(user=request.user).order_by('-created')
    available = alias_available(request.user, aliases=aliases)
    used = aliases.count()
    aliases = aliases.filter(deleted=False)

    total = 0
    for alias in aliases:
        try:
            tag = Tag.objects.filter(alias=alias)
            alias.tags = ", ".join([t.tag for t in tag])
        except Tag.DoesNotExist:
            alias.tags = ''
        alias.email_count = Email.objects.filter(inbox=alias, read=False).count()
        total += alias.email_count

    paginator = Paginator(aliases, 20)

    try:
        aliases = paginator.page(page)
    except PageNotAnInteger: # sometimes it's None
        aliases = paginator.page(1)
    except EmptyPage: # sometimes the user will try different numbers
        aliases = paginator.page(paginator.num_pages)

    messages = ""
    if "messages" in request.session and request.session["messages"]:
        messages = request.session["messages"].pop()
        request.session["messages"] = []

    context = {
        "page":_("Profile"),
        "aliases":aliases,
        "available":available,
        "total_email_count":total,
        "pages":page_paginator(aliases),
        "notify_messages":messages,
    }

    
    return render(request, "user/profile.html", context)
    

