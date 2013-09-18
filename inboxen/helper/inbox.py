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

from inboxen.helper.user import user_profile
from inboxen.models import Email, Tag, Inbox, Domain

def gen_inbox(count, inbox="", ocount=5):

    if count <= 0:
        # now we need to check if it's taken.
        try:
            Inbox.objects.get(inbox=inbox, deleted=False)
            return gen_inbox(ocount)

        except Inbox.DoesNotExist:
            return inbox
    
    inbox += choice(ascii_lowercase)
    
    return gen_inbox(count-1, inbox, ocount)

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

def find_inbox(email, user=None, deleted=False):
    """ Returns a inbox object from an email """
    inbox, domain = email.split("@", 1)

    try:
        domain = Domain.objects.get(domain=domain)
        if user:
            inbox = Inbox.objects.get(inbox=inbox, domain=domain, deleted=deleted, user=user)
        else:
            inbox = Inbox.objects.get(inbox=inbox, domain=domain, deleted=deleted)
    except ObjectDoesNotExist:
        return None

    return (inbox, domain)

def inbox_available(user, inboxes=None):
    """ Returns the amount of inboxes available """

    profile = user_profile(user)
    pool = profile.pool_amount

    if inboxes:
        used = inboxes.count()
    else:
        inboxes = Inbox.objects.filter(user=user)
        used = inboxes.count()

    return pool - used

