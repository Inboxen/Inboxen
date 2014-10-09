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
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import unittest

from inboxen import models
from website.forms import LiberationForm

@unittest.skipIf(settings.CELERY_ALWAYS_EAGER, "Task errors during testing, works fine in production")
class LiberateTestCase(test.TestCase):
    """Test account deleting"""
    fixtures = ['inboxen_testdata.json']

    def test_liberate(self):
        """Run through all combinations of compressions and mailbox formats"""
        user = get_user_model().objects.get(id=1)
        for storage in LiberationForm.STORAGE_TYPES:
            for compression in LiberationForm.COMPRESSION_TYPES:
                form_data = {"storage_type": storage[0], "compression_type": compression[0]}
                form = LiberationForm(user, data=form_data)
                self.assertTrue(form.is_valid())
                form.save()

                #TODO: check Liberation model actually has correct archive type

    def test_empty_user(self):
        """Test a completely new user"""
        user = get_user_model().objects.create(username="atester")
        form = LiberationForm(user, data={"storage_type": 0, "compression_type": 0})

        self.assertTrue(form.is_valid())

        form.save()
