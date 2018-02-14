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

from django.core import urlresolvers
from django.http import Http404
import factory

from cms.decorators import is_secure_admin
from inboxen import models
from inboxen.test import InboxenTestCase, MockRequest, grant_otp, grant_sudo
from inboxen.tests import factories
from inboxen.views import admin


class DomainAdminIndexTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)),\
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        response = self.client.get(urlresolvers.reverse("admin:domains:index"))
        self.assertEqual(response.resolver_match.func, admin.domain_admin_index)
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        factories.DomainFactory.create_batch(2, enabled=factory.Iterator([True, False]))

        response = admin.domain_admin_index(request)
        self.assertEqual(response.status_code, 200)

        expected_domains = models.Domain.objects.all()
        self.assertEqual(list(response.context_data["domains"]), list(expected_domains))

    def test_decorated(self):
        self.assertIn(is_secure_admin, admin.domain_admin_index._inboxen_decorators)


class DomainAdminCreateTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)),\
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        response = self.client.get(urlresolvers.reverse("admin:domains:create"))
        self.assertEqual(response.resolver_match.func, admin.domain_admin_create)
        self.assertEqual(response.status_code, 200)

    def test_create_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        self.assertEqual(models.Domain.objects.count(), 0)

        response = admin.domain_admin_create(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Domain.objects.count(), 0)

    def test_create_post(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"domain": "example.com"}

        self.assertEqual(models.Domain.objects.count(), 0)

        response = admin.domain_admin_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urlresolvers.reverse("admin:domains:index"))

        domain = models.Domain.objects.get()
        self.assertEqual(domain.owner, None)
        self.assertEqual(domain.enabled, True)
        self.assertEqual(domain.domain, "example.com")

    def test_create_post_invalid(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {}

        self.assertEqual(models.Domain.objects.count(), 0)

        response = admin.domain_admin_create(request)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(models.Domain.objects.count(), 0)

    def test_create_post_with_owner(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"domain": "example.com", "owner": self.user.pk}

        self.assertEqual(models.Domain.objects.count(), 0)

        response = admin.domain_admin_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urlresolvers.reverse("admin:domains:index"))

        domain = models.Domain.objects.get()
        self.assertEqual(domain.owner, self.user)
        self.assertEqual(domain.enabled, True)
        self.assertEqual(domain.domain, "example.com")

    def test_decorated(self):
        self.assertIn(is_secure_admin, admin.domain_admin_create._inboxen_decorators)


class DomainAdminEditTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)
        self.domain = factories.DomainFactory()

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)),\
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        response = self.client.get(urlresolvers.reverse("admin:domains:edit", kwargs={"domain_pk": self.domain.pk}))
        self.assertEqual(response.resolver_match.func, admin.domain_admin_edit)
        self.assertEqual(response.status_code, 200)

    def test_edit_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)

        with self.assertRaises(Http404):
            admin.domain_admin_edit(request, 0)

        response = admin.domain_admin_edit(request, self.domain.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["form"].instance, self.domain)

    def test_edit_post(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"domain": self.domain.domain, "enabled": False}

        response = admin.domain_admin_edit(request, self.domain.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urlresolvers.reverse("admin:domains:index"))

        self.domain.refresh_from_db()
        self.assertEqual(self.domain.enabled, False)
        self.assertEqual(models.Domain.objects.count(), 1)

    def test_edit_post_invalid_owner(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"domain": self.domain.domain, "enabled": False, "owner": 0}

        response = admin.domain_admin_edit(request, self.domain.pk)
        self.assertEqual(response.status_code, 200)
        self.domain.refresh_from_db()
        self.assertEqual(self.domain.enabled, True)
        self.assertEqual(self.domain.owner, None)
        self.assertEqual(models.Domain.objects.count(), 1)

    def test_edit_post_blank(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {}
        self.domain.owner = self.user
        self.domain.save()

        response = admin.domain_admin_edit(request, self.domain.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urlresolvers.reverse("admin:domains:index"))
        self.assertEqual(models.Domain.objects.count(), 1)

        self.domain.refresh_from_db()
        self.assertEqual(self.domain.owner, self.user)

    def test_decorated(self):
        self.assertIn(is_secure_admin, admin.domain_admin_edit._inboxen_decorators)


class RequestAdminIndexTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)),\
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        response = self.client.get(urlresolvers.reverse("admin:requests:index"))
        self.assertEqual(response.resolver_match.func, admin.request_admin_index)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        factories.RequestFactory.create_batch(3, authorizer=self.user, succeeded=factory.Iterator([True, False, None]))

        response = admin.request_admin_index(request)
        self.assertEqual(response.status_code, 200)

        request_objs = response.context_data["requests"]
        request_objs = list(request_objs)
        self.assertEqual(len(request_objs), 3)

        # first object should be undecided
        self.assertEqual(request_objs[0].succeeded, None)
        # other two should be not None
        self.assertNotEqual(request_objs[1].succeeded, None)
        self.assertNotEqual(request_objs[2].succeeded, None)

    def test_decorated(self):
        self.assertIn(is_secure_admin, admin.request_admin_index._inboxen_decorators)


class RequestAdminEditTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)),\
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)
        request_obj = factories.RequestFactory()

        response = self.client.get(urlresolvers.reverse("admin:requests:edit", kwargs={"request_pk": request_obj.pk}))
        self.assertEqual(response.resolver_match.func, admin.request_admin_edit)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request_obj = factories.RequestFactory()

        response = admin.request_admin_edit(request, request_obj.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["form"].instance, request_obj)
        self.assertEqual(models.Request.objects.count(), 1)

        with self.assertRaises(Http404):
            admin.request_admin_edit(request, 0)

        self.assertEqual(models.Request.objects.count(), 1)

    def test_post_invalid(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"succeeded": None}
        request_obj = factories.RequestFactory(requester=self.user)

        response = admin.request_admin_edit(request, request_obj.pk)
        self.assertEqual(response.status_code, 200)

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.succeeded, None)
        self.assertEqual(request_obj.authorizer, None)
        self.assertEqual(request_obj.date_decided, None)

    def test_post_succeeded(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"succeeded": True}
        request_obj = factories.RequestFactory(requester=self.user)
        # also pre-create profile
        pool_amount = request_obj.requester.inboxenprofile.pool_amount

        response = admin.request_admin_edit(request, request_obj.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urlresolvers.reverse("admin:requests:index"))

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.succeeded, True)
        self.assertEqual(request_obj.authorizer, self.user)
        self.assertNotEqual(request_obj.date_decided, None)

        request_obj.requester.inboxenprofile.refresh_from_db()
        self.assertEqual(request_obj.requester.inboxenprofile.pool_amount, pool_amount + request_obj.amount)

    def test_post_rejected(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"succeeded": False}
        request_obj = factories.RequestFactory(requester=self.user)
        # also pre-create profile
        pool_amount = request_obj.requester.inboxenprofile.pool_amount

        response = admin.request_admin_edit(request, request_obj.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urlresolvers.reverse("admin:requests:index"))

        request_obj.refresh_from_db()
        self.assertEqual(request_obj.succeeded, False)
        self.assertEqual(request_obj.authorizer, self.user)
        self.assertNotEqual(request_obj.date_decided, None)

        self.user.inboxenprofile.refresh_from_db()
        self.assertEqual(self.user.inboxenprofile.pool_amount, pool_amount)

    def test_decorated(self):
        self.assertIn(is_secure_admin, admin.request_admin_edit._inboxen_decorators)
