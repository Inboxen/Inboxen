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

from inboxen.search.models import SearchTestModel
from inboxen.test import InboxenTestCase


class SearchModelTestCase(InboxenTestCase):
    def test_update_search(self):
        obj = SearchTestModel(field1="thing", field2="blob")
        self.assertEqual(obj.search_tsv, None)

        obj.update_search()
        self.assertNotEqual(obj.search_tsv, None)

    def test_queryset(self):
        obj1 = SearchTestModel(field1="thing", field2="blob")
        obj1.update_search()
        obj1.save()
        # obj2 has its fields reversed
        obj2 = SearchTestModel(field2="thing", field1="blob")
        obj2.update_search()
        obj2.save()
        # obj3 shouldn't turn up at all
        obj3 = SearchTestModel(field1="bob", field2="blob")
        obj3.update_search()
        obj3.save()
        # obj4 should rank higher as it has thing in both fields
        obj4 = SearchTestModel(field1="thing", field2="thing")
        obj4.update_search()
        obj4.save()

        results = list(SearchTestModel.objects.search("thing"))

        self.assertEqual(results, [obj4, obj1, obj2])

    def test_operators(self):
        # operators make our "rank" annotation set to 1e-20 for some reason
        obj = SearchTestModel(field1="thing", field2="blob")
        obj.update_search()
        obj.save()

        results = SearchTestModel.objects.search("hit | miss")
        self.assertEqual(len(results), 0)
