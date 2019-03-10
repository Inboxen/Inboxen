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

from watson.models import SearchEntry

from inboxen import tasks
from inboxen.tests import factories
from inboxen.test import InboxenTestCase


class SearchTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()

    def test_search_empty(self):
        result = tasks.search(self.user.id, "bizz")
        self.assertCountEqual(result.keys(), ["results", "has_next", "has_previous"])
        self.assertEqual(result["results"], [])
        self.assertEqual(result["has_next"], False)
        self.assertEqual(result["has_previous"], False)

    def test_search_results(self):
        inboxes = factories.InboxFactory.create_batch(tasks.SEARCH_PAGE_SIZE, user=self.user, description="bizz")
        factories.InboxFactory.create_batch(tasks.SEARCH_PAGE_SIZE, user=self.user, description="fuzz")
        result = tasks.search(self.user.id, "bizz")
        expected_results = list(SearchEntry.objects.filter(object_id_int__in=[i.id for i in inboxes])
                                .order_by("-id").values_list("id", flat=True))
        self.assertEqual(result["results"], expected_results)
        self.assertEqual(result["has_next"], False)
        self.assertEqual(result["has_previous"], False)
        # just assert that it's some value
        self.assertTrue(result["last"])
        self.assertTrue(result["first"])

        factories.InboxFactory(user=self.user, description="bizz")
        result_2nd = tasks.search(self.user.id, "bizz")
        self.assertNotEqual(result_2nd["results"], expected_results)
        self.assertEqual(result_2nd["has_next"], True)
        self.assertEqual(result_2nd["has_previous"], False)
        # just assert that it's some value
        self.assertTrue(result_2nd["last"])
        self.assertNotEqual(result["last"], result_2nd["last"])
        self.assertTrue(result_2nd["first"])
        self.assertNotEqual(result["first"], result_2nd["first"])

    def test_search_no_results(self):
        factories.InboxFactory.create_batch(tasks.SEARCH_PAGE_SIZE, user=self.user, description="bizz")
        result = tasks.search(self.user.id, "bazz")
        self.assertEqual(result["results"], [])

        # FieldError happens if you try to order by watson_rank when no results were found
        result = tasks.search(self.user.id, "")
        self.assertEqual(result["results"], [])

    def test_after_and_before(self):
        inboxes = factories.InboxFactory.create_batch(tasks.SEARCH_PAGE_SIZE + 3, user=self.user, description="bizz")
        result = tasks.search(self.user.id, "bizz")
        expected_results = list(SearchEntry.objects.filter(object_id_int__in=[i.id for i in inboxes])
                                .order_by("-id").values_list("id", flat=True))

        self.assertEqual(result["results"], expected_results[:-3])
        self.assertEqual(result["has_next"], True)
        self.assertEqual(result["has_previous"], False)
        self.assertNotEqual(result["last"], None)
        self.assertNotEqual(result["first"], None)

        result_2nd = tasks.search(self.user.id, "bizz", after=result["last"])
        self.assertEqual(result_2nd["results"], expected_results[-3:])
        self.assertEqual(result_2nd["has_next"], False)
        self.assertEqual(result_2nd["has_previous"], True)
        self.assertTrue(result_2nd["last"])
        self.assertNotEqual(result["last"], result_2nd["last"])
        self.assertTrue(result_2nd["first"])
        self.assertNotEqual(result["first"], result_2nd["first"])

        result_3rd = tasks.search(self.user.id, "bizz", before=result_2nd["first"])
        self.assertEqual(result_3rd["results"], expected_results[:-3])
        self.assertEqual(result_3rd["has_next"], True)
        self.assertEqual(result_3rd["has_previous"], False)

        self.assertEqual(result["first"], result_3rd["first"])
        self.assertEqual(result["last"], result_3rd["last"])

        # finally, test that we can't use before before and after
        with self.assertRaises(ValueError):
            tasks.search(self.user.id, "bizz", after=result_2nd["first"], before=result["last"])
