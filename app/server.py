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
        inbox = Inbox.objects.get(inbox=inbox, domain__domain=domain)

        if inbox.deleted:
            raise SMTPError(550, "No such address")

        make_email(message, inbox)
    except DatabaseError, e:
        log.debug("DB error: %s", e)
        raise SMTPError(451, "Error processing message, try again later.")
    except Inbox.DoesNotExist:
        raise SMTPError(450, "No such address")
