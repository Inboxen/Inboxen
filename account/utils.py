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

from datetime import timedelta
import logging

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from inboxen.utils.ip import strip_ip


logger = logging.getLogger(__name__)


def make_key(request, dt):
    return "{}{}-{}".format(
        settings.REGISTER_LIMIT_CACHE_PREFIX,
        strip_ip(request.META["REMOTE_ADDR"]),
        dt.strftime("%Y%m%d%H%M"),
    )


def register_counter_full(request):
    now = timezone.now()

    keys = [make_key(request, now - timedelta(minutes=i)) for i in range(settings.REGISTER_LIMIT_WINDOW)]
    counters = cache.get_many(keys)
    if sum(counters.values()) >= settings.REGISTER_LIMIT_COUNT:
        logger.warning("Registration rate-limit reached: IP %s", request.META["REMOTE_ADDR"])
        register_counter_increase(request)
        return True

    return False


def register_counter_increase(request):
    now = timezone.now()

    key = make_key(request, now)
    # key probably won't exist, so it's ok if this isn't atomic
    cache.set(key, cache.get(key, 0) + 1, settings.REGISTER_LIMIT_CACHE_EXPIRES)
