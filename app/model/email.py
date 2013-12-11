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

from inboxen.models import Body, Email
from config.settings import datetime_format, recieved_header_name
from dateutil import parser

log = logging.getLogger(__name__)

def make_email(message, inbox):
    """Push message to the database.
    """
    user = inbox.user
    body = message.base.body
    recieved_date = datetime.now(utc)

    email = Email(inbox=inbox, user=user, recieved_date=recieved_date)
    email.save()

    ordinal = 0
    make_part(message.base, ordinal, email)

    for part in message.walk():
        ordinal = ordinal + 1
        make_part(part, ordinal, email)

def make_part(mime_part, part_ordinal, email)
    """Make a PartList object and add a body and headers
    """
    body = Body.objects.only("id").get_or_create(data=mime_part.body)[0]
    part = email.partlist_set.create(body=body, ordinal=ordinal)

    ordinal = 0
    for header in mime_part.keys():
        part.header_set.create(ordinal=ordinal, name=header, data=mime_part[header])
        ordinal = ordinal + 1
