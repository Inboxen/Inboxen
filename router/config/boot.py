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

from config import settings

__all__ = ["settings"]

try:
    os.mkdir("logs", 0700)
except OSError:
    pass

try:
    os.mkdir("run", 0710)  # group can access files in "run"
except OSError:
    pass

logconfig_path = os.path.join(dj_settings.BASE_DIR, "router", "config", "logging.conf")
if not os.path.exists(logconfig_path):
    logconfig_path = os.path.join(dj_settings.BASE_DIR, "router", "config", "logging.conf.default")

logging.config.fileConfig(logconfig_path)

Router.load(['app.server'])
Router.RELOAD = False
Router.LOG_EXCEPTIONS = True
Router.UNDELIVERABLE_QUEUE = queue.Queue("run/undeliverable")
