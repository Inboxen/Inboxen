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
from django.http import HttpResponseRedirect

from inboxen.helper.inbox import clean_tags, find_inbox
from inboxen.models import Inbox

@login_required
def edit(request, email):
    inbox, domain = email.split("@")

    try:
        inbox = request.user.inbox_set.filter(deleted=False).select_related(domain).get(inbox=inbox, domain__domain=domain)
    except Inbox.DoesNotExist;
        return HttpResponseRedirect("/user/home")

    domain = inbox.domain

    if request.method == "POST":
        if "tags" in request.POST and request.POST["tags"]:
            tags = clean_tags(request.POST["tags"])

            # remove old tags
            for old_tag in inbox.tag_set.all():
                old_tag.delete()

            for i, tag in enumerate(tags):
                tags[i] = Tag(tag=tag)
                tags[i].inbox = inbox
                tags[i].save()

        return HttpResponseRedirect("/user/home")

    tags = Tag.objects.filter(inbox=inbox)
    display_tags = ""
    for tag in tags:
        display_tags += ", %s" % str(tag)

    context = {
        "page":_("Edit %s") % email,
        "email":email,
        "inbox":inbox.inbox,
        "domain":domain.domain,
        "tags":display_tags[2:],
    }

    return render(request, "email/edit.html", context)
