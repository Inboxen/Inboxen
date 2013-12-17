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

from random import choice
from string import ascii_lowercase

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from inboxen.helper.user import user_profile
from inboxen.models import Email, Tag, Inbox, Domain, Request

def clean_tags(tags):
    """ Tags some tags from user input """
    if "," in tags:
        tags = tags.split(",")
    else:
        tags = tags.split()

    for i, tag in enumerate(tags):
        tag = tag.rstrip(" ").lstrip(" ")
        tags[i] = tag

    return tags

def inbox_available(user, inboxes=None):
    """ Returns the amount of inboxes available """

    profile = user_profile(user)
    pool = profile.pool_amount

    if inboxes:
        used = inboxes.count()
    else:
        inboxes = Inbox.objects.filter(user=user)
        used = inboxes.count()

    left = pool - used

    if left < 10:
        with transaction.atomic():
            try:
                last_request = Request.objects.filter(user=user).orderby('-date').only('succeeded')[0].succeeded
            except IndexError:
                last_request = True

            if last_request:
                profile = user_profile(request.user)
                amount = profile.pool_amount + 500
                current_request = Request(amount=amount, date=datetime.now(utc))
                current_request.requester = user
                current_request.save()

    return left

