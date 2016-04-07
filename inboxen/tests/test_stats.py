##
#    Copyright (C) 2014, 2016 Jessica Tallon & Matt Molyneaux
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

import json

from django import test
from django.core.cache import cache
from django.core.urlresolvers import reverse

from inboxen import models


class StatsViewTestCase(test.TestCase):
    def tearDown(self):
        super(StatsViewTestCase, self).tearDown()
        cache.clear()

    def test_get_blank(self):
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sorry, we don't seem to have any statistics", response.content)

    def test_get_broken(self):
        models.Statistic.objects.create(users={}, inboxes={}, emails={})
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sorry, we don't seem to have any statistics", response.content)

    def test_recent_empty(self):
        response = self.client.get(reverse("stats_recent"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertItemsEqual(["dates", "users", "inboxes", "emails", "now"], data.keys())

    def test_recent_missing_points(self):
        def format_date(date):
            r = date.isoformat()
            if date.microsecond:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r

        stat = models.Statistic.objects.create(users={"count":12}, inboxes={"inbox_count__sum": 13}, emails={"email_count__sum": 14})

        response = self.client.get(reverse("stats_recent"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)

        # remove "now" - it will be current time
        del data["now"]

        self.assertItemsEqual(
            data.items(),
            (
                ("dates", [format_date(stat.date)]),
                ("inboxes", [13]),
                ("users", [12]),
                ("emails", [14]),
            )
        )
