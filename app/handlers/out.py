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

from salmon.routing import route, stateless
from salmon.queue import Queue

from django.db import DatabaseError

from config.settings import DEBUG, accepted_queue_dir, accepted_queue_opts_in
from app.model.email import make_email

import logging

@route("(inbox)@(domain)", inbox=".+", domain=".+")
@stateless
def START(message, inbox=None, domain=None):
    RETRY = "x-queue-retry"
    # inbox should have already have been checked before the email entered the
    # queue
    try:
        make_email(message, inbox, domain)
    except Exception, e:
        logging.debug("DB error: %s " % str(e))
        if RETRY in message:
            if int(message[RETRY]) > 2:
                # tried to many times, dump the message
                logging.error("Retried too many times")
                raise
            message[RETRY] = str(int(message[RETRY]) + 1)
        else:
            message[RETRY] = "0"

        queue = Queue(accepted_queue_dir, **accepted_queue_opts_in)
        queue.push(message)
