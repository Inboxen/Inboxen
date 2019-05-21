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

from django.core.checks import Error

from inboxen.checks import DOMAIN_ERROR_MSG, domains_available_check
from inboxen.test import InboxenTestCase
from inboxen.tests import factories


class DomainCheckTestCase(InboxenTestCase):
    def test_no_domain(self):
        self.assertEqual(domains_available_check(None), [Error(DOMAIN_ERROR_MSG)])

    def test_domain_enabled(self):
        factories.DomainFactory(enabled=True)
        self.assertEqual(domains_available_check(None), [])

    def test_domain_disabled(self):
        factories.DomainFactory(enabled=False)
        self.assertEqual(domains_available_check(None), [Error(DOMAIN_ERROR_MSG)])
