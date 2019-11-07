##
#    Copyright 2013, 2015 Jessica Tallon, Matt Molyneaux
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

import logging

from django.conf import settings
from django.db import DatabaseError, transaction
from salmon.routing import nolocking, route, stateless
from salmon.server import Relay, SMTPError

from inboxen.models import Inbox
from inboxen.router.app.helpers import make_email
from inboxen.utils import RESERVED_LOCAL_PARTS_REGEX

# we want to match *something*, but not something consumed by forward_to_admins
INBOX_REGEX = r"(?!^({})@).+".format(RESERVED_LOCAL_PARTS_REGEX)


log = logging.getLogger(__name__)


@route(r"(local)@(domain)", local=RESERVED_LOCAL_PARTS_REGEX, domain=r".+")
@stateless
@nolocking
def forward_to_admins(message, local=None, domain=None):
    if message.is_bounce():
        # log and swallow the message
        log.warning("Detected message bounce %s, subject: %s", message, message["Subject"])
        return

    try:
        Relay().deliver(message, To=[m[1] for m in settings.ADMINS], From=settings.SERVER_EMAIL)
    except Exception as excp:
        log.exception("Error while forwarding admin message %s: %s", id(message), excp)
        raise SMTPError(450, "Error while forwarding admin message %s" % id(message))


@route(r"(inbox)@(domain)", inbox=INBOX_REGEX, domain=r".+")
@stateless
@nolocking
def process_message(message, inbox=None, domain=None):
    try:
        with transaction.atomic():
            inbox = Inbox.objects.filter(inbox=inbox, domain__domain=domain)
            inbox = inbox.select_related("user", "user__inboxenprofile").receiving()
            inbox = inbox.get()

            make_email(message, inbox)

            inbox.new = True
            inbox.save(update_fields=["new"])

            if not inbox.exclude_from_unified:
                profile = inbox.user.inboxenprofile
                profile.unified_has_new_messages = True
                profile.save(update_fields=["unified_has_new_messages"])
    except DatabaseError as e:
        log.exception("DB error: %s", e)
        raise SMTPError(451, "Error processing message, try again later.")
    except Inbox.DoesNotExist:
        raise SMTPError(550, "No such address")
