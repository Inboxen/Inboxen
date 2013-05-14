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

from django.core.exceptions import ObjectDoesNotExist
from inboxen.models import Email, Tag, Alias, Domain
import traceback

def delete_alias(email, user=None):
    """ Deletes the email and all the data """
    try:
        alias, domain = email.split("@", 1)
        domain = Domain.objects.get(domain=domain)
        if user:
            alias = Alias.objects.get(alias=alias, domain=domain, deleted=False, user=user)
        else:
            alias = Alias.objects.get(alias=alias, domain=domain, deleted=False)

    except ObjectDoesNotExist:
        traceback.print_exc()
        return False

    alias.deleted = True
    alias.save()

    # okay now we need to look up the emails
    # we don't want to keep emails for that alias
    emails = Email.objects.filter(inbox=alias)
    for email in emails:
        email.delete()

    # Also delete any tags
    tags = Tag.objects.filter(alias=alias)
    for tag in tags:
        tag.delete()

    return True
