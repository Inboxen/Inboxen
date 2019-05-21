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

from django.http import Http404
from django.urls import reverse

from inboxen.cms import models, views
from inboxen.test import InboxenTestCase, MockRequest, grant_otp, grant_sudo
from inboxen.tests import factories


class PageTestCase(InboxenTestCase):
    def setUp(self):
        models.HelpBasePage.objects.update(live=True)
        self.user = factories.UserFactory()

    def test_view(self):
        request = MockRequest(user=self.user)

        response = views.page(request, "")
        self.assertEqual(response.status_code, 200)

        response = views.page(request, "questions/")
        self.assertEqual(response.status_code, 200)

    def test_integration(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
                "Could not log in"

        response = self.client.get(reverse("cms-index", args=("",)))
        self.assertEqual(response.resolver_match.func, views.page)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("cms-index", args=("questions/",)))
        self.assertEqual(response.resolver_match.func, views.page)
        self.assertEqual(response.status_code, 200)


class AdminIndexTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        """Check URLs are attached to the correct view"""
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
            "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.resolver_match.func, views.index)
        self.assertEqual(response.status_code, 200)

        # admin index can drill down into page tree
        page = models.HelpIndex.objects.get()
        response = self.client.get(reverse("admin:index", kwargs={"page_pk": page.pk}))
        self.assertEqual(response.resolver_match.func, views.index)
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)

        response = views.index(request)
        self.assertEqual(response.status_code, 200)

        expected_page = models.HelpBasePage.objects.filter(parent__isnull=True).get()
        self.assertEqual(response.context_data["page"], expected_page)

        breadcrumbs = [p for p in response.context_data["breadcrumbs"]]
        self.assertEqual(breadcrumbs, [expected_page])

        # with root page as kwarg
        response = views.index(request, page_pk=expected_page.pk)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context_data["page"], expected_page)

        breadcrumbs = [p for p in response.context_data["breadcrumbs"]]
        self.assertEqual(breadcrumbs, [expected_page])

    def test_child_page(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()

        response = views.index(request, page_pk=page.pk)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context_data["page"], page)

        breadcrumbs = [p for p in response.context_data["breadcrumbs"]]
        self.assertEqual(breadcrumbs, [page.parent, page])

    def test_404(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)

        with self.assertRaises(Http404):
            views.index(request, page_pk="123")

    def test_decorated(self):
        self.assertIn(views.is_secure_admin, views.index._inboxen_decorators)


class ChoosePageTypeTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        """Check URLs are attached to the correct view"""
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
            "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        parent_pk = models.HelpIndex.objects.get().pk
        response = self.client.get(reverse("admin:choose-page-type", kwargs={"parent_pk": parent_pk}))
        self.assertEqual(response.resolver_match.func, views.choose_page_type)
        self.assertEqual(response.status_code, 200)

    def test_choose_type_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        page = models.HelpBasePage.objects.filter(parent__isnull=True).get()

        response = views.choose_page_type(request, parent_pk=page.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["parent_pk"], page.pk)
        self.assertEqual(response.context_data["models"],
                         [models.HelpIndex._meta, models.AppPage._meta, models.HelpPage._meta])

        breadcrumbs = [p for p in response.context_data["breadcrumbs"]]
        self.assertEqual(breadcrumbs, [page])

    def test_404(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)

        with self.assertRaises(Http404):
            views.choose_page_type(request, parent_pk=123)

    def test_decorated(self):
        self.assertIn(views.is_secure_admin, views.choose_page_type._inboxen_decorators)


class CreatePageTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        """Check URLs are attached to the correct view"""
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
            "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        parent_pk = models.HelpIndex.objects.get().pk
        response = self.client.get(reverse("admin:create-page", kwargs={"model": "helpindex", "parent_pk": parent_pk}))
        self.assertEqual(response.resolver_match.func, views.create_page)
        self.assertEqual(response.status_code, 200)

    def test_create_page_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)

        page = models.HelpBasePage.objects.filter(parent__isnull=True).get()
        response = views.create_page(request, "helppage", page.pk)
        self.assertEqual(response.status_code, 200)

    def test_create_page_post(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"title": "Test Page", "slug": "test-page"}

        page = models.HelpBasePage.objects.filter(parent__isnull=True).get()
        response = views.create_page(request, "helppage", page.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.HelpPage.objects.count(), 0)

        request.POST["body"] = "body"
        response = views.create_page(request, "helppage", page.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("admin:index", kwargs={"page_pk": page.pk}))

        new_page = models.HelpBasePage.objects.get(slug="test-page", parent_id=page.pk)
        self.assertEqual(new_page.specific_class, models.HelpPage)

    def test_404(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        page = models.HelpBasePage.objects.filter(parent__isnull=True).get()

        with self.assertRaises(Http404):
            views.create_page(request, "helppage", 123)

        with self.assertRaises(Http404):
            views.create_page(request, "notpage", page.pk)

        with self.assertRaises(Http404):
            views.create_page(request, "notpage", 123)

    def test_decorated(self):
        self.assertIn(views.is_secure_admin, views.create_page._inboxen_decorators)


class EditPageTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        """Check URLs are attached to the correct view"""
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
            "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        parent_pk = models.HelpIndex.objects.get().pk
        response = self.client.get(reverse("admin:edit-page", kwargs={"page_pk": parent_pk}))
        self.assertEqual(response.resolver_match.func, views.edit_page)
        self.assertEqual(response.status_code, 200)

    def test_edit_page_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()

        response = views.edit_page(request, page_pk=page.pk)
        self.assertEqual(response.status_code, 200)

    def test_edit_page_post(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {"title": "Test Page", "slug": "test-page"}
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()

        response = views.edit_page(request, page_pk=page.pk)
        self.assertEqual(response.status_code, 200)

        request.POST["app"] = "tickets.urls"
        response = views.edit_page(request, page_pk=page.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("admin:index", kwargs={"page_pk": page.pk}))

        page.refresh_from_db()
        self.assertEqual(page.title, "Test Page")
        self.assertEqual(page.slug, "test-page")

    def test_404(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)

        with self.assertRaises(Http404):
            views.edit_page(request, page_pk="123")

    def test_decorated(self):
        self.assertIn(views.is_secure_admin, views.edit_page._inboxen_decorators)


class DeletePageTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        """Check URLs are attached to the correct view"""
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
            "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        response = self.client.get(reverse("admin:delete-page", kwargs={"page_pk": 1}))
        self.assertEqual(response.resolver_match.func, views.delete_page)
        self.assertEqual(response.status_code, 404)

    def test_delete_page_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()

        response = views.delete_page(request, page_pk=page.pk)
        self.assertEqual(response.status_code, 200)

    def test_delete_page_post(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {}

        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()

        response = views.delete_page(request, page_pk=page.pk)
        self.assertEqual(response.status_code, 200)

        # page still exists
        page.refresh_from_db()

        request.POST["yes_delete"] = True
        response = views.delete_page(request, page_pk=page.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("admin:index", kwargs={"page_pk": page.parent_id}))

        # page was deleted
        with self.assertRaises(models.HelpBasePage.DoesNotExist):
            page.refresh_from_db()

    def test_404(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()

        # page parent can't be deleted yet
        with self.assertRaises(Http404):
            views.delete_page(request, page_pk=page.parent_id)

        # not a page
        with self.assertRaises(Http404):
            views.delete_page(request, page_pk="123")

    def test_decorated(self):
        self.assertIn(views.is_secure_admin, views.delete_page._inboxen_decorators)
