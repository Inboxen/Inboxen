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

from unittest import expectedFailure

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import Http404
from django.urls.exceptions import NoReverseMatch

from inboxen.cms import models
from inboxen.cms.tests import factories
from inboxen.test import InboxenTestCase, MockRequest
from inboxen.tickets import views as ticket_views


class HelpQuerySetTestCase(InboxenTestCase):
    def setUp(self):
        # delete pages that are set up by migrations
        models.HelpBasePage.objects.all().delete()

    def test_in_menu(self):
        is_menu = factories.HelpBasePageFactory(in_menu=True)
        factories.HelpBasePageFactory(in_menu=False)

        qs = models.HelpBasePage.objects.in_menu()
        self.assertEqual(list(qs), [is_menu])

    def test_live(self):
        is_live = factories.HelpBasePageFactory(live=True)
        factories.HelpBasePageFactory(live=False)

        qs = models.HelpBasePage.objects.live()
        self.assertEqual(list(qs), [is_live])


class HelpBasePageTestCase(InboxenTestCase):
    def test_url_property(self):
        page = models.HelpBasePage.objects.get(parent__isnull=False)
        old_url = page.url

        # check that property is cached
        page.url_cache = "bluh"
        self.assertEqual(page.url, old_url)

        # check that url_cache is prefered over generate_url
        del page.url
        self.assertEqual(page.url, "bluh")

        # check that generate_url is actually called
        page.slug = "test"
        del page.url
        page.url_cache = ""
        self.assertEqual(page.url, "/help/test/")

        # check that nothing was saved
        page = models.HelpBasePage.objects.get(pk=page.pk)
        self.assertEqual(page.url, old_url)

    def test_generate_url(self):
        root_page = models.HelpBasePage.objects.get(parent__isnull=True)
        child_page = models.HelpBasePage.objects.get(parent__isnull=False)

        self.assertEqual(root_page.generate_url(), settings.CMS_ROOT_URL)
        root_page.slug = "test"
        # root pages ignore their slug
        self.assertEqual(root_page.generate_url(), settings.CMS_ROOT_URL)

        self.assertEqual(child_page.generate_url(), settings.CMS_ROOT_URL + child_page.slug + "/")
        # child pages don't
        child_page.slug = "test"
        self.assertEqual(child_page.generate_url(), settings.CMS_ROOT_URL + "test" + "/")

    def test_specific_property(self):
        specific_page = models.HelpIndex.objects.get()
        base_page = models.HelpBasePage.objects.get(pk=specific_page.pk)

        self.assertEqual(specific_page.specific, specific_page)
        self.assertEqual(base_page.specific, specific_page)
        self.assertNotEqual(base_page.specific, base_page)  # make sure that we're not just checking PKs

    def test_specific_class(self):
        specific_page = models.HelpIndex.objects.get()
        base_page = models.HelpBasePage.objects.get(pk=specific_page.pk)

        self.assertEqual(specific_page.specific_class, models.HelpIndex)
        self.assertEqual(base_page.specific_class, models.HelpIndex)

    def test_route(self):
        root_page = models.HelpBasePage.objects.get(parent__isnull=True)
        child_page = models.HelpBasePage.objects.get(parent__isnull=False)
        request = MockRequest()

        self.assertEqual(root_page.route(request, []), (root_page, [], {}))

        with self.assertRaises(Http404):
            root_page.route(request, ["notapage"])

        root_page.live = False
        root_page.save()
        with self.assertRaises(Http404):
            root_page.route(request, [])

        self.assertEqual(root_page.route(request, [child_page.slug]), (child_page.specific, (), {}))
        self.assertEqual(child_page.route(request, []), (child_page, [], {}))

    def test_serve(self):
        request = MockRequest()
        # you can't call this method on the base class
        with self.assertRaises(AssertionError):
            models.HelpBasePage().serve(request)

    def test_get_context(self):
        page = models.HelpBasePage.objects.first()
        request = MockRequest()

        ctx = page.get_context(request)
        self.assertEqual(ctx, {"page": page})

    def test_save(self):
        root_page = models.HelpBasePage.objects.get(parent__isnull=True)
        child_page = models.HelpBasePage.objects.get(parent__isnull=False)

        self.assertEqual(root_page.url_cache, "")
        root_page.save()
        root_page.refresh_from_db()
        self.assertEqual(root_page.url_cache, root_page.generate_url())

        self.assertEqual(child_page.url_cache, "")
        child_page.save()
        child_page.refresh_from_db()
        self.assertEqual(child_page.url_cache, child_page.generate_url())

    def test_manager(self):
        # test correct manager inherited
        self.assertEqual(models.HelpBasePage.objects._built_with_as_manager, True)
        self.assertEqual(models.HelpBasePage.objects._queryset_class, models.HelpQuerySet)

    def test_unique_columns(self):
        root_page = models.HelpBasePage.objects.get(parent__isnull=True)
        child_page = models.HelpBasePage.objects.get(parent__isnull=False)
        second_child = factories.HelpBasePageFactory(parent=root_page)

        with transaction.atomic(), self.assertRaises(IntegrityError):
            second_child.slug = child_page.slug
            second_child.save()

        second_child.slug = child_page.slug
        second_child.parent = child_page
        second_child.save()


class HelpIndexTestCase(InboxenTestCase):
    def test_get_context(self):
        page = models.HelpIndex.objects.get()
        request = MockRequest()

        ctx = page.get_context(request)
        self.assertCountEqual(ctx.keys(), ["page", "menu"])
        self.assertEqual(ctx["page"], page)
        self.assertEqual(list(ctx["menu"]), [models.HelpBasePage.objects.get(parent__pk=page.pk)])

    def test_serve(self):
        page = models.HelpIndex.objects.get()
        request = MockRequest()

        response = page.serve(request)

        self.assertEqual(response.status_code, 200)

    def test_manager(self):
        # test correct manager inherited
        self.assertEqual(models.HelpIndex.objects._built_with_as_manager, True)
        self.assertEqual(models.HelpIndex.objects._queryset_class, models.HelpQuerySet)


class AppPageTestCase(InboxenTestCase):
    def test_route(self):
        page = models.AppPage.objects.get()
        request = MockRequest()

        pg, args, kwargs = page.route(request, [])
        self.assertEqual(pg, page)
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {})
        self.assertEqual(page._view.view_class, ticket_views.QuestionHomeView)

        request.path = "/help/questions/ticket/12/"
        pg, args, kwargs = page.route(request, ["ticket", "12"])
        self.assertEqual(pg, page)
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {"pk": "12"})
        self.assertEqual(page._view.view_class, ticket_views.QuestionDetailView)

        page.live = False
        page.save()
        with self.assertRaises(Http404):
            page.route(request, ["ticket", "12"])

    def test_serve(self):
        page = models.AppPage.objects.get()
        page._view = lambda x: "this is a test"
        request = MockRequest()

        response = page.serve(request)
        self.assertEqual(response, "this is a test")

    def test_reverse(self):
        page = models.AppPage.objects.get()

        self.assertEqual(page.reverse("tickets-index"), "/")

        with self.assertRaises(NoReverseMatch):
            # url name not preset in tickets.urls
            page.reverse("stats")

        self.assertEqual(page.reverse("tickets-detail", kwargs={"pk": 12}), "/ticket/12/")

    def test_manager(self):
        # test correct manager inherited
        self.assertEqual(models.AppPage.objects._built_with_as_manager, True)
        self.assertEqual(models.AppPage.objects._queryset_class, models.HelpQuerySet)


class HelpPageTestCase(InboxenTestCase):
    def test_serve(self):
        page = models.HelpIndex.objects.get()
        request = MockRequest()

        response = page.serve(request)

        self.assertEqual(response.status_code, 200)

    def test_manager(self):
        # test correct manager inherited
        self.assertEqual(models.HelpPage.objects._built_with_as_manager, True)
        self.assertEqual(models.HelpPage.objects._queryset_class, models.HelpQuerySet)


@expectedFailure
class PeoplePageTestCase(InboxenTestCase):
    pass


@expectedFailure
class PersonInfoTestCase(InboxenTestCase):
    pass


@expectedFailure
class ImageTestCase(InboxenTestCase):
    pass
