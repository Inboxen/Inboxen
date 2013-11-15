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

from config.settings import (DEBUG,
                            reject_dir,
                            accepted_queue_dir,
                            accepted_queue_opts_in,
                            datetime_format,
                            recieved_header_name)

from salmon.routing import route, stateless, nolocking
from salmon.server import SMTPError
from salmon.queue import Queue
from django.db import DatabaseError
from app.model.inbox import inbox_exists
from datetime import datetime
from pytz import utc
import logging

# We don't change state based on who the sender is, so we're stateless and
# don't return any other state. Locking is done by the queue (on the filesystem
# at the time of writing)
@route("(inbox)@(domain)", inbox=".+", domain=".+")
@stateless
@nolocking
def START(message, inbox=None, domain=None):
    """Does this inbox exist? If yes, queue it. If no, drop it."""
    try:
        exists, deleted = inbox_exists(inbox, domain)
    except DatabaseError, e:
        logging.debug("DB error: %s", e)
        raise SMTPError(451, "Oops, melon exploded")

    if exists:
        message[recieved_header_name] = datetime.now(utc).strftime(datetime_format)

        # the queue needs to know who the message is for
        message['x-original-to'] = message['to']
        message['to'] = "%s@%s" % (inbox, domain)

        #if spam filtering is enabled, do so

        #if not spam, or not filter:
        accept_queue = Queue(accepted_queue_dir, **accepted_queue_opts_in)
        accept_queue.push(message)
        logging.debug("APPROVED inbox %s on domain %s", inbox, domain)
    else:
        if DEBUG:
            queue = Queue(reject_dir, **accepted_queue_opts_in)
            queue.push(message)
            logging.debug("REJECTED inbox %s on domain %s", inbox, domain)

        # Raise an error, tell server whether to try again or not
        if deleted:
            code = 550
        else:
            code = 450
        raise SMTPError(code, 'Inbox %s@%s does not exist')

