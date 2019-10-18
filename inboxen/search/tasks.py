##
#    Copyright (C) 2019 Jessica Tallon & Matt Molyneaux
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

from inboxen import models
from inboxen.celery import app
from inboxen.search.utils import create_search_cache_key, search


@app.task(rate_limit="100/s")
def search_home_page(user_id, search_term, before=None, after=None):
    key = create_search_cache_key(user_id, search_term, "home", before, after)
    search_qs = models.Inbox.objects.viewable(user_id).search(search_term)
    return search(key, search_qs, before, after)


@app.task(rate_limit="100/s")
def search_unified_inbox(user_id, search_term, before=None, after=None):
    key = create_search_cache_key(user_id, search_term, "inbox:unified", before, after)
    search_qs = models.Email.objects.filter(inbox__exclude_from_unified=False).viewable(user_id).search(search_term)
    return search(key, search_qs, before, after)


@app.task(rate_limit="100/s")
def search_single_inbox(user_id, search_term, inbox, before=None, after=None):
    key = create_search_cache_key(user_id, search_term, "inbox:{}".format(inbox), before, after)
    inbox = models.Inbox.objects.from_string(inbox, user=user_id)
    search_qs = models.Email.objects.viewable(user_id).filter(inbox=inbox).search(search_term)
    return search(key, search_qs, before, after)
