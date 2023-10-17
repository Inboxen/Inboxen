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

from inboxen.cms.models import HelpBasePage


def app_reverse(page, viewname, args=None, kwargs=None):
    """Reverse a URL for an app that is behind an AppPage"""
    relative_url = page.reverse(viewname, args=args, kwargs=kwargs)
    page_url = page.url
    page_url = page_url.rstrip("/")

    return page_url + relative_url


def get_root_page():
    root_pages = HelpBasePage.objects.get_cached_trees()

    assert len(root_pages) <= 1, "Expected to find a single tree, found %s" % len(root_pages)

    try:
        return root_pages[0]
    except IndexError:
        return None


def breadcrumb_iterator(page):
    if page.parent_id:
        for parent in breadcrumb_iterator(page.parent):
            yield parent

    yield page
