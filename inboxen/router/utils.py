##
#    Copyright 2013, 2015, 2020 Jessica Tallon, Matt Molyneaux
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

from functools import wraps
import logging

from django.conf import settings
from django.utils import timezone
from salmon import encoding

from inboxen.models import Body, Email, Header, PartList
from inboxen.monitor.models import Check

log = logging.getLogger(__name__)

LAST_EMAIL_RECEIVED = None


def make_email(message, inbox):
    """Push message to the database.
    """
    base = message.base
    received_date = timezone.now()

    email = Email(inbox=inbox, received_date=received_date)
    email.save()

    data = encode_body(base)
    body, _ = Body.objects.only("id").get_or_create(data=data)

    part = PartList(body=body, email=email)
    part.save()

    parents = {base: part.id}

    for header in message.keys():
        ordinal = message.keys().index(header)
        Header.objects.create(name=header, data=message[header], ordinal=ordinal, part=part)

    for part in message.walk():
        data = encode_body(part)
        body, _ = Body.objects.only("id").get_or_create(data=data)
        part_item = PartList(body=body, email=email, parent_id=parents[part.parent])
        part_item.save()
        parents[part] = part_item.id

        for header in part.keys():
            ordinal = part.keys().index(header)
            header_data = part[header]
            Header.objects.create(name=header, data=header_data, ordinal=ordinal, part=part_item)

    email.update_search()
    email.save()


def encode_body(part):
    """Make certain that the body of a part is bytes and not unicode"""
    if isinstance(part.body, str):
        ctype, params = part.content_encoding['Content-Type']
        try:
            data = part.body.encode(params.get("charset", "ascii"))
        except (UnicodeError, LookupError):
            # I have no time for your bullshit
            data = part.body.encode("utf-8")
    else:
        data = part.body

    if not data:
        data = b''

    return data


def email_received_check(func):
    """
    Creates a Check object if and only if the handler has not errored and a
    check hasn't been done within SALMON_CHECK_WINDOW
    """
    @wraps(func)
    def inner(message, *args, **kwargs):
        # this is ugly and i don't like it, but it's the best i could come up with
        global LAST_EMAIL_RECEIVED
        state = func(message, *args, **kwargs)
        now = timezone.now()
        if LAST_EMAIL_RECEIVED is None or LAST_EMAIL_RECEIVED < now - settings.SALMON_CHECK_WINDOW:
            LAST_EMAIL_RECEIVED = now
            Check.objects.create_check(Check.SALMON)
        return state
    return inner


def set_salmon_encoding_error_policy():
    old_func = encoding.guess_encoding_and_decode

    def inboxen_guess_encoding_and_decode(original, data):
        return old_func(original, data, "replace")

    encoding.guess_encoding_and_decode = inboxen_guess_encoding_and_decode
