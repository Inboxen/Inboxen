##
#    Copyright (C) 2013, 2014, 2015, 2016, 2017 Jessica Tallon & Matt Molyneaux
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
import logging.config
import os

from django.conf import settings as dj_settings
from salmon import queue
from salmon.routing import Router
from salmon.server import LMTPReceiver, SMTPReceiver

from inboxen.router.config import settings

__all__ = ["settings"]

try:
    os.mkdir("logs", 0o700)
except OSError:
    pass

try:
    os.mkdir("run", 0o710)  # group can access files in "run"
except OSError:
    pass

logging.config.dictConfig(dj_settings.SALMON_LOGGING)

# where to listen for incoming messages
if dj_settings.SALMON_SERVER["type"] == "lmtp":
    settings.receiver = LMTPReceiver(socket=dj_settings.SALMON_SERVER["path"])
elif dj_settings.SALMON_SERVER["type"] == "smtp":
    settings.receiver = SMTPReceiver(dj_settings.SALMON_SERVER['host'],
                                     dj_settings.SALMON_SERVER['port'])

Router.load(['inboxen.router.app.server'])
Router.RELOAD = False
Router.LOG_EXCEPTIONS = True
Router.UNDELIVERABLE_QUEUE = queue.Queue("run/undeliverable")
