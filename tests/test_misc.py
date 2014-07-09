##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

from django import test
from django.conf import settings as dj_settings
from django.core import urlresolvers

from inboxen import models
from queue import tasks

class StatsTestCase(test.TestCase):
    """Test flag tasks"""
    # only testing that it doesn't raise an exception atm
    fixtures = ['inboxen_testdata.json']

    def test_no_exceptions(self):
        tasks.statistics.delay()


class FlagTestCase(test.TestCase):
    """Test flag tasks"""
    # only testing that it doesn't raise an exception atm
    # TODO: actually test
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        super(FlagTestCase, self).setUp()
        self.user = models.User.objects.get(username="isdabizda")
        self.emails = [email.id for email in models.Email.objects.filter(inbox__user=self.user)[:10]]

    def test_flags_from_unified(self):
        tasks.deal_with_flags.delay(self.emails, user_id=self.user.id)

    def test_flags_from_single_inbox(self):
        inbox = models.Inbox.objects.filter(email__id=self.emails[0]).only("id").get()
        tasks.deal_with_flags.delay(self.emails, user_id=self.user.id, inbox_id=inbox.id)
