##
#    Copyright (C) 201 Jessica Tallon & Matt Molyneaux
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

from cursor_pagination import CursorPaginator
from django.apps import apps
from django.core.cache import cache

from inboxen.celery import app
from inboxen.search.utils import create_search_cache_key

SEARCH_TIMEOUT = 60 * 30
SEARCH_PAGE_SIZE = 25


@app.task(rate_limit="100/s")
def search(user_id, search_term, model, before=None, after=None):
    """Offload the expensive part of search to avoid blocking the web interface"""
    if not search_term:
        return {
            "results": [],
            "has_next": False
        }

    if before and after:
        raise ValueError("You can't do this.")

    _app, _model = model.split(".")
    _model = apps.get_app_config(_app).get_model(_model)

    search_qs = _model.objects.viewable(user_id).search(search_term)

    page_kwargs = {
        "after": after,
        "before": before,
    }
    if before:
        page_kwargs["last"] = SEARCH_PAGE_SIZE
    else:
        page_kwargs["first"] = SEARCH_PAGE_SIZE

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

    key = create_search_cache_key(user_id, search_term, before, after)
    cache.set(key, results, SEARCH_TIMEOUT)

    return results
