##
#    Copyright (C) 2018 Jessica Tallon & Matt Molyneaux
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

from datetime import datetime, timedelta
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import urlresolvers, cache
from django.utils import timezone

from inboxen.account import utils
from inboxen.test import InboxenTestCase, MockRequest


class RegisterRateLimitTestCase(InboxenTestCase):
    def get_url(self):
        return urlresolvers.reverse("user-registration")

    def test_sum_counters(self):
        login_data = {"password1": "qwerty123456", "password2": "qwerty123456"}
        counter = 0

        for i in range(10):
            login_data["username"] = "myuser%s" % i
            response = self.client.post(self.get_url(), login_data)
            counter += 1
            if response["Location"] == self.get_url():
                break

        # registration should be rejected on the REGISTER_LIMIT_COUNT + 1 try
        self.assertEqual(counter, settings.REGISTER_LIMIT_COUNT + 1)
        self.assertEqual(get_user_model().objects.count(), settings.REGISTER_LIMIT_COUNT)

        cache.cache.clear()

        # registration should be accepted again
        response = self.client.post(self.get_url(), login_data)
        self.assertNotEqual(response["Location"], self.get_url())

    def test_sum_counters_spreadout(self):
        now = timezone.now()
        request = MockRequest()
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        for i in range(settings.REGISTER_LIMIT_COUNT - 1):
            key = utils.make_key(request, now - timedelta(minutes=i * 2))
            cache.cache.set(key, 1)

        request.META["REMOTE_ADDR"] = "127.0.0.2"
        for i in range(settings.REGISTER_LIMIT_COUNT - 1):
            key = utils.make_key(request, now - timedelta(minutes=i * 2))
            cache.cache.set(key, 1)

        login_data = {"username": "myuser", "password1": "qwerty123456", "password2": "qwerty123456"}
        response = self.client.post(self.get_url(), login_data)
        self.assertNotEqual(response["Location"], self.get_url())
        self.assertEqual(get_user_model().objects.count(), 1)

        # next attempt should be rejected
        response = self.client.post(self.get_url(), login_data)
        self.assertEqual(response["Location"], self.get_url())
        self.assertEqual(get_user_model().objects.count(), 1)


class RegisterRateLimitUtilsTestCase(InboxenTestCase):
    @mock.patch("inboxen.account.utils.ratelimit.timezone.now")
    def test_check_doesnt_increase_count_if_not_full(self, now_mock):
        now_mock.return_value = datetime.utcnow()
        cache.cache.clear()
        request = MockRequest()
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        utils.register_counter_full(request)

        self.assertEqual(len(cache.cache._cache), 0)

    @mock.patch("inboxen.account.utils.ratelimit.timezone.now")
    def test_check_does_increase_count_if_full(self, now_mock):
        now_mock.return_value = datetime.utcnow()
        cache.cache.clear()
        request = MockRequest()
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        for i in range(settings.REGISTER_LIMIT_COUNT):
            utils.register_counter_increase(request)

        self.assertEqual(len(cache.cache._cache), 1)
        self.assertEqual(cache.cache.get(utils.make_key(request, now_mock())), settings.REGISTER_LIMIT_COUNT)

        utils.register_counter_full(request)

        self.assertEqual(len(cache.cache._cache), 1)
        self.assertEqual(cache.cache.get(utils.make_key(request, now_mock())), settings.REGISTER_LIMIT_COUNT + 1)

    def test_make_key_ipv4(self):
        now = timezone.now()
        now.replace(second=15)
        request = MockRequest()
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        key1 = utils.make_key(request, now)

        # IPv4 addresses are one per host
        request.META["REMOTE_ADDR"] = "127.0.0.2"
        key2 = utils.make_key(request, now)

        self.assertNotEqual(key1, key2)

        # seconds don't matter
        now.replace(second=45)
        key3 = utils.make_key(request, now)

        self.assertEqual(key2, key3)

    def test_make_key_ipv6(self):
        now = timezone.now()
        now.replace(second=15)
        request = MockRequest()
        request.META["REMOTE_ADDR"] = "2001:ba8:1f1:f315:216:5eff:fe00:379"

        key1 = utils.make_key(request, now)

        # a /64 addresses is one per host
        request.META["REMOTE_ADDR"] = "2001:ba8:1f1:f315:216:5eff:fe00:380"
        key2 = utils.make_key(request, now)

        self.assertEqual(key1, key2)

        request.META["REMOTE_ADDR"] = "2001:ba8:1f1:f311:216:5eff:fe00:380"
        key3 = utils.make_key(request, now)

        self.assertNotEqual(key2, key3)

        # seconds don't matter
        now.replace(second=45)
        key4 = utils.make_key(request, now)

        self.assertEqual(key3, key4)
