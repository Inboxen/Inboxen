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

from django.core.cache import cache
from django.urls import reverse

from inboxen import models
from inboxen.test import InboxenTestCase


class StatsViewTestCase(InboxenTestCase):
    def tearDown(self):
        super(StatsViewTestCase, self).tearDown()
        cache.clear()

    def test_get_blank(self):
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sorry, we don't seem to have any statistics", response.content.decode("utf-8"))

    def test_get_broken(self):
        models.Statistic.objects.create(users={}, inboxes={}, emails={})
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sorry, we don't seem to have any statistics", response.content.decode("utf-8"))

    def test_recent_empty(self):
        response = self.client.get(reverse("stats_recent"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        expected_keys = ["dates", "users", "inboxes", "emails", "now", "read_emails", "active_users", "active_inboxes"]
        self.assertCountEqual(data.keys(), expected_keys)

    def test_recent_missing_points(self):
        def format_date(date):
            r = date.isoformat()
            if date.microsecond:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r

        stat1 = models.Statistic.objects.create(users={"count": 12}, inboxes={"inbox_count__sum": 13},
                                                emails={"email_count__sum": 14})
        stat2 = models.Statistic.objects.create(users={"count": 12}, inboxes={}, emails={"email_count__sum": 14})

        response = self.client.get(reverse("stats_recent"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)

        # remove "now" - it will be current time
        del data["now"]

        self.assertCountEqual(
            data.items(),
            (
                ("dates", [format_date(stat1.date), format_date(stat2.date)]),
                ("inboxes", [13, None]),
                ("users", [12, 12]),
                ("emails", [14, 14]),
                ("read_emails", [None, None]),
                ("active_users", [None, None]),
                ("active_inboxes", [None, None]),
            )
        )

    def test_csp(self):
        # test a normal view
        response = self.client.get(reverse("index"))
        self.assertIn("style-src 'self';", response["content-security-policy"])

        # stats view
        response = self.client.get(reverse("stats"))
        self.assertIn("style-src 'self' 'unsafe-inline';", response["content-security-policy"])
