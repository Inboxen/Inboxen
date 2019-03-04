##
#    Copyright (C) 2018 Jessica Tallon & Matt Molyneaux
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
import urllib

from django.conf import settings

from inboxen.utils import ratelimit, ip


logger = logging.getLogger(__name__)


def make_key(request, dt):
    key = "{}{}-{}".format(
        settings.REGISTER_LIMIT_CACHE_PREFIX,
        ip.strip_ip(request.META["REMOTE_ADDR"]),
        dt.strftime("%Y%m%d%H%M"),
    )

    key = urllib.parse.quote(key.encode("utf-8"))
    return key


def full_callback(request):
    logger.warning("Registration rate-limit reached: IP %s", request.META["REMOTE_ADDR"])


register_ratelimit = ratelimit.RateLimit(
    make_key,
    full_callback,
    settings.REGISTER_LIMIT_WINDOW,
    settings.REGISTER_LIMIT_COUNT,
)


register_counter_full = register_ratelimit.counter_full
register_counter_increase = register_ratelimit.counter_increase
