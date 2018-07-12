##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
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


from django.urls.exceptions import NoReverseMatch

from inboxen.cms.utils import app_reverse, get_root_page, breadcrumb_iterator
from inboxen.cms.models import HelpBasePage, AppPage
from inboxen.cms.tests.factories import HelpBasePageFactory
from inboxen.test import InboxenTestCase


class AppReverseTestCase(InboxenTestCase):
    def setUp(self):
        self.page = AppPage()
        self.page.url = "/help/someapp/"
        self.page.app = "tickets.urls"

    def test_url_correct(self):
        url = app_reverse(self.page, "tickets-index")

        self.assertEqual(url, "/help/someapp/")

    def test_bad_viewname(self):
        with self.assertRaises(NoReverseMatch):
            app_reverse(self.page, "noop")

    def test_args_kwargs(self):
        url = app_reverse(self.page, "tickets-list", kwargs={"status": "test"})

        self.assertEqual(url, "/help/someapp/status/test/")


class GetRootPageTestCase(InboxenTestCase):
    def test_get_root(self):
        root_page = HelpBasePage.objects.get(parent__isnull=True)
        page = get_root_page()
        self.assertEqual(page, root_page)

    def test_no_root(self):
        HelpBasePage.objects.all().delete()
        page = get_root_page()
        self.assertEqual(page, None)

    def test_multiple_roots(self):
        root_page = HelpBasePage.objects.get(parent__isnull=True)

        # create a second parallel tree, which should be ignored
        HelpBasePageFactory(
            tree_id=2,
            parent=None,
            lft=root_page.lft,
            rght=root_page.rght,
            level=root_page.level,
        )
        page = get_root_page()
        self.assertEqual(page, root_page)

        # force a broken tree
        HelpBasePageFactory(
            tree_id=1,
            parent=None,
            lft=root_page.lft,
            rght=root_page.rght,
            level=root_page.level,
        )

        with self.assertRaises(AssertionError):
            get_root_page()


class BreadcrumbTestCase(InboxenTestCase):
    def test_iterators(self):
        root_page = get_root_page()
        self.assertEqual([root_page], [i for i in breadcrumb_iterator(root_page)])

        sub_page = root_page.get_children()[0]
        self.assertEqual([root_page, sub_page], [i for i in breadcrumb_iterator(sub_page)])
