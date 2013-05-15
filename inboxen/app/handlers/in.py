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
from pytz import utc

from lamson.routing import route, stateless, nolocking
from lamson.queue import Queue
from config.settings import DEBUG, reject_dir, accepted_queue_dir, accepted_queue_opts_in, datetime_format, recieved_header_n
from app.model.alias import alias_exists
from datetime import datetime
import logging

# We don't change state based on who the sender is, so we're stateless and
# don't return any other state. Locking is done by the queue (on the filesystem
# at the time of writing)
@route("(alias)@(domain)", alias=".+", domain=".+")
@stateless
@nolocking
def START(message, alias=None, domain=None):
    """Does this alias exist? If yes, queue it. If no, drop it."""
    if alias_exists(alias, domain):
        message[recieved_header_name] = datetime.now(utc).strftime(datetime_format)

        # the queue needs to know who the message is for
        message['x-original-to'] = message['to']
        message['to'] = "%s@%s" % (alias, domain)

        #if spam filtering is enabled, do so

        #if not spam, or not filter:
        accept_queue = Queue(accepted_queue_dir, **accepted_queue_opts_in)
        accept_queue.push(message)
        logging.debug("APPROVED alias %s on domain %s" % (alias, domain))
    elif DEBUG:
        queue = Queue(reject_dir, **accepted_queue_opts_in)
        queue.push(message)
        logging.debug("REJECTED alias %s on domain %s" % (alias, domain))

