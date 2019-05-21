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
import urllib

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class RateLimit(object):
    def __init__(self, make_key, full_callback, window, max_count):
        self.make_key = make_key
        self.full_callback = full_callback
        self.window = window
        self.max_count = max_count
        self.cache_expires = (window + 1) * 60

    def counter_full(self, request):
        now = timezone.now()

        keys = [self.make_key(request, now - timedelta(minutes=i)) for i in range(self.window)]
        counters = cache.get_many(keys)
        if sum(counters.values()) >= self.max_count:
            self.full_callback(request)
            self.counter_increase(request)
            return True

        return False

    def counter_increase(self, request):
        now = timezone.now()

        key = self.make_key(request, now)
        # key probably won't exist, so it's ok if this isn't atomic
        cache.set(key, cache.get(key, 0) + 1, self.cache_expires)


def make_key(request, dt):
    key = "{}{}-{}".format(
        settings.INBOX_LIMIT_CACHE_PREFIX,
        request.user.id,
        dt.strftime("%Y%m%d%H%M"),
    )

    key = urllib.parse.quote(key.encode("utf-8"))
    return key


def full_callback(request):
    logger.warning("Inbox rate-limit reached: USER %s", request.user)


inbox_ratelimit = RateLimit(
    make_key,
    full_callback,
    settings.INBOX_LIMIT_WINDOW,
    settings.INBOX_LIMIT_COUNT,
)
