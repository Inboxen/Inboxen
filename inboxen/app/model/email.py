##
#
# Copyright 2013 Jessica Tallon, Matt Molyneaux
# 
# This file is part of Inboxen back-end.
#
# Inboxen back-end is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Inboxen back-end is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inboxen back-end.  If not, see <http://www.gnu.org/licenses/>.
#
##

from inboxen.models import Alias, Attachment, Email, Header
from config.settings import datetime_format, recieved_header_name
from dateutil import parser

def make_email(message, alias, domain):
    """Push message to the database.

    Will throw an Alias.DoesNotExist exception if alias and domain are not valid"""

    inbox = Alias.objects.get(alias=alias, domain__domain=domain) # will exist
    user = inbox.user
    body = message.base.body
    recieved_date = parser.parse(message[recieved_header_name])
    del message[recieved_header_name]

    email = Email(inbox=inbox, user=user, body=body, recieved_date=recieved_date)
    email.save()

    head_list = []
    for name in message.keys():
        header = Header(name=name, data=message[name])
        header.save()
        head_list.append(header)
    # add all the headers at once should save us some queries
    email.headers.add(*head_list)

    attach_list = []
    for part in message.walk():
        if not part.body:
            part.body = u''
        attachment = Attachment(
                        content_type=part.content_encoding['Content-Type'][0],
                        content_disposition=part.content_encoding['Content-Disposition'][0],
                        data=part.body
                        )
        attachment.save()
        attach_list.append(attachment)
    # as with headers above
    email.attachments.add(*attach_list)
