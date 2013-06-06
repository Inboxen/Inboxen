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

from random import choice
from string import ascii_lowercase

from django.core.exceptions import ObjectDoesNotExist

from website.models import Email, Tag, Alias, Domain
from website.helper.user import user_profile

def gen_alias(count, alias="", ocount=5):

    if count <= 0:
        # now we need to check if it's taken.
        try:
            Alias.objects.get(alias=alias, deleted=False)
            return gen_alias(ocount)

        except Alias.DoesNotExist:
            return alias
    
    alias += choice(ascii_lowercase)
    
    return gen_alias(count-1, alias, ocount)

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

def find_alias(email, user=None, deleted=False):
    """ Returns a alias object from an email """
    alias, domain = email.split("@", 1)

    try:
        domain = Domain.objects.get(domain=domain)
        if user:
            alias = Alias.objects.get(alias=alias, domain=domain, deleted=deleted, user=user)
        else:
            alias = Alias.objects.get(alias=alias, domain=domain, deleted=deleted)
    except ObjectDoesNotExist:
        return None

    return (alias, domain)

def alias_available(user, aliases=None):
    """ Returns the amount of aliases available """

    profile = user_profile(user)
    pool = profile.pool_amount

    if aliases:
        used = aliases.count()
    else:
        aliases = Alias.objects.filter(user=user)
        used = aliases.count()

    return pool - used

