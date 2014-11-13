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

from salmon.routing import nolocking, route, stateless
from salmon.server import SMTPError

from django.db import DatabaseError, transaction
import watson

from app.helpers import make_email
from inboxen.models import Inbox

import logging

log = logging.getLogger(__name__)

@route("(inbox)@(domain)", inbox=".+", domain=".+")
@stateless
@nolocking
@transaction.atomic()
def START(message, inbox=None, domain=None):
    try:
        inbox = Inbox.objects.select_related("user", "user__userprofile")
        inbox = inbox.receiving().get(inbox=inbox, domain__domain=domain)

        make_email(message, inbox)

        with watson.skip_index_update():
            inbox.flags.new = True
            inbox.save(update_fields=["flags"])

        if not inbox.flags.exclude_from_unified:
            profile = inbox.user.userprofile
            profile.flags.unified_has_new_messages = True
            profile.save(update_fields=["flags"])

    except DatabaseError, e:
        log.debug("DB error: %s", e)
        raise SMTPError(451, "Error processing message, try again later.")
    except Inbox.DoesNotExist:
        raise SMTPError(550, "No such address")
