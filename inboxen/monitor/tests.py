##
#    Copyright (C) 2020 Jessica Tallon & Matt Molyneaux
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

from datetime import timedelta
from unittest import mock

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from inboxen.monitor.models import Check
from inboxen.monitor.tasks import check_tasks
from inboxen.test import InboxenTestCase


class CheckModelTestCase(InboxenTestCase):
    def test_creation(self):
        check = Check.objects.create_check(Check.SALMON)
        self.assertEqual(check.good, True)
        self.assertEqual(check.check, Check.SALMON)

    def test_creation_bad_check(self):
        with self.assertRaises(ValueError):
            Check.objects.create_check("test")

    def test_creation_invalid_check(self):
        with self.assertRaises(ValueError):
            Check.objects.create_check(120)

    def test_check_not_today(self):
        check = Check.objects.create(check=Check.SALMON)
        check.when = timezone.now() - timedelta(days=2)
        check.save()
        self.assertEqual(Check.objects.check_ok(Check.SALMON), False)

    def test_check_not_good(self):
        Check.objects.create(check=Check.SALMON, good=False)
        self.assertEqual(Check.objects.check_ok(Check.SALMON), False)

    def test_check_wrong_type(self):
        Check.objects.create(check=Check.CELERY)
        self.assertEqual(Check.objects.check_ok(Check.SALMON), False)

    def test_check_good(self):
        Check.objects.create_check(Check.SALMON)
        self.assertEqual(Check.objects.check_ok(Check.SALMON), True)


class CheckTaskTestCase(InboxenTestCase):
    def test_task(self):
        check_tasks.apply_async()
        self.assertEqual(Check.objects.check_ok(Check.CELERY), True)

    def test_cron(self):
        self.assertEqual(settings.CELERY_BEAT_SCHEDULE["monitor"]["task"], "inboxen.monitor.tasks.check_tasks")


class CheckSalmonViewTestCase(InboxenTestCase):
    def test_good(self):
        Check.objects.create_check(Check.SALMON)
        response = self.client.get(reverse("monitor:salmon"))
        self.assertEqual(response.status_code, 200)

    def test_bad(self):
        Check.objects.create_check(Check.CELERY)
        response = self.client.get(reverse("monitor:salmon"))
        self.assertEqual(response.status_code, 404)


class CheckCeleryViewTestCase(InboxenTestCase):
    @mock.patch("inboxen.monitor.views.app")
    def test_no_rabbit(self, app_mock):
        app_mock.control.broadcast.side_effect = Exception
        Check.objects.create_check(Check.CELERY)
        response = self.client.get(reverse("monitor:celery"))
        self.assertEqual(response.status_code, 500)

    @mock.patch("inboxen.monitor.views.app")
    def test_no_workers(self, app_mock):
        app_mock.control.broadcast.return_value = None
        Check.objects.create_check(Check.CELERY)
        response = self.client.get(reverse("monitor:celery"))
        self.assertEqual(response.status_code, 502)

    @mock.patch("inboxen.monitor.views.app")
    def test_bad(self, app_mock):
        app_mock.control.broadcast.return_value = {}
        Check.objects.create_check(Check.SALMON)
        response = self.client.get(reverse("monitor:celery"))
        self.assertEqual(response.status_code, 404)

    @mock.patch("inboxen.monitor.views.app")
    def test_good(self, app_mock):
        app_mock.control.broadcast.return_value = {}
        Check.objects.create_check(Check.CELERY)
        response = self.client.get(reverse("monitor:celery"))
        self.assertEqual(response.status_code, 200)
