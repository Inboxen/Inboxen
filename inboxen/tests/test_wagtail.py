##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
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

import mock

from django import test
from django.core import urlresolvers

from inboxen.tests import factories
from inboxen import models
from inboxen.wagtail_hooks import DomainPermissionHelper, RequestPermissionHelper


class MiddlewareMock(object):
    pass


class WagtailHooksTestCase(test.TestCase):
    def setUp(self):
        super(WagtailHooksTestCase, self).setUp()
        self.user = factories.UserFactory(is_superuser=True)
        self.domain = factories.DomainFactory()
        self.request = models.Request.objects.create(requester=factories.UserFactory(), amount=100)

        login = self.client.login(username=self.user.username, password="123456")

        self.admin_middleware_mock = mock.patch("inboxen.middleware.WagtailAdminProtectionMiddleware", MiddlewareMock)

        if not login:
            raise Exception("Could not log in")

        self.admin_middleware_mock.start()

    def tearDown(self):
        super(WagtailHooksTestCase, self).tearDown()
        self.admin_middleware_mock.stop()

    def test_domain_index_allowed(self):
        url = urlresolvers.reverse("inboxen_domain_modeladmin_index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_domain_create_allowed(self):
        url = urlresolvers.reverse("inboxen_domain_modeladmin_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_domain_delete_denied(self):
        url = urlresolvers.reverse("inboxen_domain_modeladmin_delete", kwargs={"instance_pk": self.domain.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_domain_permission_helper(self):
        helper = DomainPermissionHelper(models.Domain)

        # check that user_can_create always returns None
        self.assertEqual(helper.user_can_create(self.user), True)

        # check that user_can_delete_obj always returns None
        self.assertEqual(helper.user_can_delete_obj(self.user, self.domain), False)
        # it shouldn't even check args
        self.assertEqual(helper.user_can_delete_obj(None, None), False)

    def test_request_index_allowed(self):
        url = urlresolvers.reverse("inboxen_request_modeladmin_index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_request_create_allowed(self):
        url = urlresolvers.reverse("inboxen_request_modeladmin_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_request_delete_denied(self):
        url = urlresolvers.reverse("inboxen_request_modeladmin_delete", kwargs={"instance_pk": self.request.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_request_permission_helper(self):
        helper = RequestPermissionHelper(models.Domain)

        # check that user_can_create always returns None
        self.assertEqual(helper.user_can_create(self.user), False)
        # it shouldn't even check args
        self.assertEqual(helper.user_can_create(None), False)

        # check that user_can_delete_obj always returns None
        self.assertEqual(helper.user_can_delete_obj(self.user, self.request), False)
        # it shouldn't even check args
        self.assertEqual(helper.user_can_delete_obj(None, None), False)
