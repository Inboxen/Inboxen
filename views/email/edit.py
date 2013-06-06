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
from django.http import HttpResponseRedirect

from website.models import Tag
from website.helper.alias import clean_tags, find_alias

@login_required
def edit(request, email):

    alias = find_alias(email, user=request.user, deleted=False)

    if not alias:
        # display a proper error here?
        return HttpResponseRedirect("/user/profile")
    else:
        alias = alias

    if request.method == "POST":
        if "tags" in request.POST and request.POST["tags"]:
            tags = clean_tags(request.POST["tags"])

            # remove old tags
            for old_tag in Tag.objects.filter(alias=alias[0]):
                old_tag.delete()

            for i, tag in enumerate(tags):
                tags[i] = Tag(tag=tag)
                tags[i].alias = alias[0]
                tags[i].save()


        return HttpResponseRedirect("/user/profile")

    tags = Tag.objects.filter(alias=alias[0])
    display_tags = ""
    for tag in tags:
        display_tags += ", %s" % str(tag)


    context = {
        "page":"Edit %s" % email,
        "email":email,
        "alias":alias[0].alias,
        "domain":alias[1],
        "tags":display_tags[2:],
    }

    return render(request, "email/edit.html", context)
