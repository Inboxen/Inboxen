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

from unittest import mock

from django.conf import settings

from inboxen.models import Email, Inbox
from inboxen.search import tasks, utils
from inboxen.test import InboxenTestCase
from inboxen.tests import factories


class SearchTasksTestCase(InboxenTestCase):
    def setUp(self):
        patch = mock.patch("inboxen.search.tasks.search")
        self.addCleanup(patch.stop)
        self.search_function = patch.start()

    def test_search_home_page(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        user_id = 12
        search_term = "bizz"

        expected_key = utils.create_search_cache_key(user_id, search_term, "home", None, None)
        expected_sql = str(Inbox.objects.viewable(user_id).search(search_term).query)

        result = tasks.search_home_page(user_id, search_term)
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (None, None))
        self.assertEqual(self.search_function.call_args[1], {})

    def test_search_home_page_before(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        user_id = 12
        search_term = "bizz"
        before = "hii"

        expected_key = utils.create_search_cache_key(user_id, search_term, "home", before, None)
        expected_sql = str(Inbox.objects.viewable(user_id).search(search_term).query)

        result = tasks.search_home_page(user_id, search_term, before=before)
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (before, None))
        self.assertEqual(self.search_function.call_args[1], {})

    def test_search_home_page_after(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        user_id = 12
        search_term = "bizz"
        after = "hello"

        expected_key = utils.create_search_cache_key(user_id, search_term, "home", None, after)
        expected_sql = str(Inbox.objects.viewable(user_id).search(search_term).query)

        result = tasks.search_home_page(user_id, search_term, after=after)
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (None, after))
        self.assertEqual(self.search_function.call_args[1], {})

    def test_search_unified_inbox(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        user_id = 12
        search_term = "bizz"

        expected_key = utils.create_search_cache_key(user_id, search_term, "inbox:unified", None, None)
        expected_sql = str(Email.objects.filter(inbox__exclude_from_unified=False)
                           .viewable(user_id).search(search_term).query)

        result = tasks.search_unified_inbox(user_id, search_term)
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (None, None))
        self.assertEqual(self.search_function.call_args[1], {})

    def test_search_unified_inbox_before(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        user_id = 12
        search_term = "bizz"
        before = "hii"

        expected_key = utils.create_search_cache_key(user_id, search_term, "inbox:unified", before, None)
        expected_sql = str(Email.objects.filter(inbox__exclude_from_unified=False)
                           .viewable(user_id).search(search_term).query)

        result = tasks.search_unified_inbox(user_id, search_term, before=before)
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (before, None))
        self.assertEqual(self.search_function.call_args[1], {})

    def test_search_unified_inbox_after(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        user_id = 12
        search_term = "bizz"
        after = "hello"

        expected_key = utils.create_search_cache_key(user_id, search_term, "inbox:unified", None, after)
        expected_sql = str(Email.objects.filter(inbox__exclude_from_unified=False)
                           .viewable(user_id).search(search_term).query)

        result = tasks.search_unified_inbox(user_id, search_term, after=after)
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (None, after))
        self.assertEqual(self.search_function.call_args[1], {})

    def test_search_single_inbox(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        search_term = "bizz"
        inbox = factories.InboxFactory(description="bizz")

        expected_key = utils.create_search_cache_key(inbox.user_id, search_term, "inbox:{}".format(inbox), None, None)
        expected_sql = str(Email.objects.viewable(inbox.user_id).filter(inbox=inbox).search(search_term).query)

        result = tasks.search_single_inbox(inbox.user_id, search_term, str(inbox))
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (None, None))
        self.assertEqual(self.search_function.call_args[1], {})

    def test_search_single_inbox_before(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        search_term = "bizz"
        inbox = factories.InboxFactory(description="bizz")
        before = "hii"

        expected_key = utils.create_search_cache_key(inbox.user_id, search_term, "inbox:{}".format(inbox), before, None)
        expected_sql = str(Email.objects.viewable(inbox.user_id).filter(inbox=inbox).search(search_term).query)

        result = tasks.search_single_inbox(inbox.user_id, search_term, str(inbox), before=before)
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (before, None))
        self.assertEqual(self.search_function.call_args[1], {})

    def test_search_single_inbox_after(self):
        mock_result = mock.Mock()
        self.search_function.return_value = mock_result

        search_term = "bizz"
        inbox = factories.InboxFactory(description="bizz")
        after = "hello"

        expected_key = utils.create_search_cache_key(inbox.user_id, search_term, "inbox:{}".format(inbox), None, after)
        expected_sql = str(Email.objects.viewable(inbox.user_id).filter(inbox=inbox).search(search_term).query)

        result = tasks.search_single_inbox(inbox.user_id, search_term, str(inbox), after=after)
        self.assertEqual(result, mock_result)
        self.assertEqual(self.search_function.call_count, 1)
        self.assertEqual(self.search_function.call_args[0][0], expected_key)
        self.assertEqual(str(self.search_function.call_args[0][1].query), expected_sql)
        self.assertEqual(self.search_function.call_args[0][2:], (None, after))
        self.assertEqual(self.search_function.call_args[1], {})


class SearchFunctionTestCase(InboxenTestCase):
    def setUp(self):
        self.key = "blahblahkey"

    def test_search_empty(self):
        result = utils.search(self.key, Inbox.objects.search(""), None, None)
        self.assertCountEqual(result.keys(), ["results", "has_next", "has_previous"])
        self.assertEqual(result["results"], [])
        self.assertEqual(result["has_next"], False)
        self.assertEqual(result["has_previous"], False)

    def test_search_results(self):
        user = factories.UserFactory()
        inboxes = factories.InboxFactory.create_batch(settings.SEARCH_PAGE_SIZE, user=user, description="bizz")
        result = utils.search(self.key, Inbox.objects.search("bizz"), None, None)
        expected_results = [i.id for i in inboxes]
        expected_results.reverse()
        self.assertEqual(result["results"], expected_results)
        self.assertEqual(result["has_next"], False)
        self.assertEqual(result["has_previous"], False)
        # just assert that it's some value
        self.assertTrue(result["last"])
        self.assertTrue(result["first"])

        factories.InboxFactory(user=user, description="bizz")
        result_2nd = utils.search(self.key, Inbox.objects.search("bizz"), None, None)
        self.assertNotEqual(result_2nd["results"], expected_results)
        self.assertEqual(result_2nd["has_next"], True)
        self.assertEqual(result_2nd["has_previous"], False)
        # just assert that it's some value
        self.assertTrue(result_2nd["last"])
        self.assertNotEqual(result["last"], result_2nd["last"])
        self.assertTrue(result_2nd["first"])
        self.assertNotEqual(result["first"], result_2nd["first"])

    def test_after_and_before(self):
        user = factories.UserFactory()
        inboxes = factories.InboxFactory.create_batch(settings.SEARCH_PAGE_SIZE + 3, user=user, description="bizz")
        result = utils.search(self.key, Inbox.objects.search("bizz"), None, None)
        expected_results = [i.id for i in inboxes]
        expected_results.reverse()

        self.assertEqual(result["results"], expected_results[:-3])
        self.assertEqual(result["has_next"], True)
        self.assertEqual(result["has_previous"], False)
        self.assertNotEqual(result["last"], None)
        self.assertNotEqual(result["first"], None)

        result_2nd = utils.search(self.key, Inbox.objects.search("bizz"), None, result["last"])
        self.assertEqual(result_2nd["results"], expected_results[-3:])
        self.assertEqual(result_2nd["has_next"], False)
        self.assertEqual(result_2nd["has_previous"], True)
        self.assertTrue(result_2nd["last"])
        self.assertNotEqual(result["last"], result_2nd["last"])
        self.assertTrue(result_2nd["first"])
        self.assertNotEqual(result["first"], result_2nd["first"])

        result_3rd = utils.search(self.key, Inbox.objects.search("bizz"), result_2nd["first"], None)
        self.assertEqual(result_3rd["results"], expected_results[:-3])
        self.assertEqual(result_3rd["has_next"], True)
        self.assertEqual(result_3rd["has_previous"], False)

        self.assertEqual(result["first"], result_3rd["first"])
        self.assertEqual(result["last"], result_3rd["last"])

    def test_both_after_and_before(self):
        with self.assertRaises(ValueError):
            utils.search(self.key, Inbox.objects.search(""), "bluh", "blah")
