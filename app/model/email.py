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
from pytz import utc
import logging

from inboxen.models import Body, Email, PartList
from config.settings import datetime_format, recieved_header_name
from dateutil import parser

log = logging.getLogger(__name__)

def make_email(message, inbox):
    """Push message to the database.
    """
    user = inbox.user
    body = message.base.body
    recieved_date = datetime.now(utc)

    body = Body.objects.only("id").get_or_create(data=mime_part.body)[0]

    part = PartList(body=body)
    part.save()

    parents = {message.base: part.id}

    for header in message.keys():
        ordinal = message.keys().index(header)
        Header.objects.create(name=header, data=message[header], ordinal=ordinal, part=part)

    email = Email(id=part.email, inbox=inbox, recieved_date=recieved_date)
    email.save()

    for part in message.walk():
        body = Body.objects.only("id").get_or_create(data=mime_part.body)[0]
        part_item = PartList(body=body, parent=parents[part.parent])
        part_item.save()
        parents[part] = part_item.id

        for header in part.keys():
            ordinal = part.keys().index(header)
            Header.objects.create(name=header, data=part[header], ordinal=ordinal, part=part_item)
