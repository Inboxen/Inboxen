##
#
# Copyright 2013 Jessica Tallon, Matt Molyneaux
# 
# This file is part of Inboxen.
#
# Inboxen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Inboxen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
#
##

from datetime import datetime
import logging

from pytz import utc

from inboxen.models import Body, Email, Header, PartList

log = logging.getLogger(__name__)

def make_email(message, inbox):
    """Push message to the database.
    """
    user = inbox.user
    base = message.base
    received_date = datetime.now(utc)

    email = Email(inbox=inbox, received_date=received_date)
    email.save()

    body = Body.objects.only("id").get_or_create(data=base.body)[0]

    part = PartList(body=body, email=email)
    part.save()

    parents = {base: part.id}

    for header in message.keys():
        ordinal = message.keys().index(header)
        Header.objects.create(name=header, data=message[header], ordinal=ordinal, part=part)


    for part in message.walk():
        body = Body.objects.only("id").get_or_create(data=part.body)[0]
        part_item = PartList(body=body, email=email, parent_id=parents[part.parent])
        part_item.save()
        parents[part] = part_item.id

        for header in part.keys():
            ordinal = part.keys().index(header)
            Header.objects.create(name=header, data=part[header], ordinal=ordinal, part=part_item)
