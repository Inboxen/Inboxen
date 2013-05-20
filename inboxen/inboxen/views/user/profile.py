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

from inboxen.models import Alias, Tag, Email
from inboxen.helper.alias import alias_available
    
@login_required
def profile(request, page=1):

    aliases = Alias.objects.filter(user=request.user).order_by('-created')
    available = alias_available(request.user, aliases=aliases)
    used = aliases.count()
    aliases = aliases.filter(deleted=False)

    try:
        for alias in aliases:
            tag = Tag.objects.filter(alias=alias)
            alias.tags = ", ".join([t.tag for t in tag])
    except Tag.DoesNotExist:
        pass

    paginator = Paginator(aliases, 20)

    try:
        aliases = paginator.page(page)
    except PageNotAnInteger: # sometimes it's None
        aliases = paginator.page(1)
    except EmptyPage: # sometimes the user will try different numbers
        aliases = paginator.page(paginator.num_pages)

    # now we need to deduce how many unread emails there are
    total = 0
    for alias in aliases.object_list:
        alias.email_count = Email.objects.filter(inbox=alias, read=False).count()
        total += alias.email_count

    context = {
        "page":"Profile",
        "aliases":Paginator(aliases, 20).page(page),
        "available":available,
        "total_email_count":total,
    }
    
    return render(request, "user/profile.html", context)
    

