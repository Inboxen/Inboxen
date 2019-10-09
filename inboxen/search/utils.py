##
#    Copyright (C) 2014-2015 Jessica Tallon & Matt Molyneaux
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

import base64

from cursor_pagination import CursorPaginator
from django.conf import settings
from django.core.cache import cache

SEARCH_VERSION = 1  # bump this any time you change how the cache key words


def create_search_cache_key(user_id, query, identifier, before, after):
    key = "{version}{user}{identifier}{before}{after}{query}".format(
        version=SEARCH_VERSION,
        user=user_id,
        identifier=identifier,
        before=before,
        after=after,
        query=query,
    )
    key = base64.b64encode(key.encode()).decode()

    return key


def search(key, search_qs, before, after):
    if before and after:
        raise ValueError("You can't do this.")

    page_kwargs = {
        "after": after,
        "before": before,
    }
    if before:
        page_kwargs["last"] = settings.SEARCH_PAGE_SIZE
    else:
        page_kwargs["first"] = settings.SEARCH_PAGE_SIZE

    paginator = CursorPaginator(search_qs, ordering=('-rank', '-id'))

    page = paginator.page(**page_kwargs)
    results = {
        "results": [p.id for p in page],
        "has_next": page.has_next,
        "has_previous": page.has_previous,
    }

    if len(results["results"]) > 0:
        results["last"] = paginator.cursor(page[-1])
        results["first"] = paginator.cursor(page[0])

    cache.set(key, results, settings.SEARCH_TIMEOUT)

    return results
