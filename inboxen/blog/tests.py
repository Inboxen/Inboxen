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

from django import urls
from django.http import Http404
import factory
import factory.fuzzy

from inboxen.blog import forms, models, views
from inboxen.blog.templatetags import blog_admin_tags
from inboxen.cms.decorators import is_secure_admin
from inboxen.test import InboxenTestCase, MockRequest, grant_otp, grant_sudo
from inboxen.tests import factories

BODY = """
Hey there!
==========

This is a test post:

* A list item
* And another

Bye!
"""
SUBJECT = """A Test Post For You And Me"""


class BlogPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BlogPost

    subject = factory.fuzzy.FuzzyText()
    body = factory.fuzzy.FuzzyText()


class BlogTestCase(InboxenTestCase):
    def test_blog_index(self):
        user = factories.UserFactory()
        BlogPostFactory.create_batch(10, draft=False, author=user)

        url = urls.reverse("blog")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = urls.reverse("blog", kwargs={"page": "2"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_blog_post(self):
        user = factories.UserFactory()
        user.is_staff = True
        user.save()

        models.BlogPost.objects.create(author=user, subject=SUBJECT, draft=True, body=BODY)
        post = models.BlogPost.objects.get()
        self.assertEqual(post.subject, SUBJECT)
        self.assertEqual(post.body, BODY)
        self.assertEqual(post.date, None)
        self.assertEqual(str(post), "{} (draft)".format(post.subject))

        url = urls.reverse('blog-post', kwargs={"slug": post.slug})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        old_mod = post.modified
        post.draft = False
        post.save()
        post = models.BlogPost.objects.get()
        self.assertNotEqual(post.date, None)
        self.assertNotEqual(post.modified, old_mod)
        self.assertEqual(str(post), "{}".format(post.subject))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_feeds(self):
        user = factories.UserFactory()
        BlogPostFactory.create_batch(10, draft=False, author=user)

        response_rss = self.client.get(urls.reverse("blog-feed-rss"))
        response_atom = self.client.get(urls.reverse("blog-feed-atom"))

        self.assertEqual(response_rss.status_code, 200)
        self.assertEqual(response_atom.status_code, 200)
        self.assertNotEqual(response_rss.content, response_atom.content)

    def test_admin_forms_for_null(self):
        user = factories.UserFactory()

        form = forms.CreateForm(user=user, data={"subject": "sub\x00ject", "body": "body"})
        self.assertFalse(form.is_valid())

        form = forms.CreateForm(user=user, data={"subject": "subject", "body": "bod\x00y"})
        self.assertFalse(form.is_valid())

        form = forms.CreateForm(user=user, data={"subject": "subject", "body": "body"})
        self.assertTrue(form.is_valid())

        post = form.save(commit=False)

        form = forms.EditForm(instance=post, data={"subject": "sub\x00ject", "body": "body"})
        self.assertFalse(form.is_valid())

        form = forms.EditForm(instance=post, data={"subject": "subject", "body": "bod\x00y"})
        self.assertFalse(form.is_valid())

        form = forms.EditForm(instance=post, data={"subject": "subject", "body": "body"})
        self.assertTrue(form.is_valid())

    def test_templatetag(self):
        output = blog_admin_tags.render_draft(True)
        self.assertIn('<span class="label label-primary"', output)
        self.assertIn("Draft", output)
        self.assertNotIn("Live", output)

        output = blog_admin_tags.render_draft(False)
        self.assertIn('<span class="label label-default"', output)
        self.assertIn("Live", output)
        self.assertNotIn("Draft", output)


class BlogAdminIndexTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        response = self.client.get(urls.reverse("admin:blog:index"))
        self.assertEqual(response.resolver_match.func, views.blog_admin_index)
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        BlogPostFactory.create_batch(2, draft=factory.Iterator([True, False]), author=self.user)

        response = views.blog_admin_index(request)
        self.assertEqual(response.status_code, 200)

        expected_posts = models.BlogPost.objects.all()
        self.assertEqual(list(response.context_data["posts"]), list(expected_posts))

    def test_decorated(self):
        self.assertIn(is_secure_admin, views.blog_admin_index._inboxen_decorators)


class BlogAdminCreateTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        response = self.client.get(urls.reverse("admin:blog:create"))
        self.assertEqual(response.resolver_match.func, views.blog_admin_create)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)

        response = views.blog_admin_create(request)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {}

        response = views.blog_admin_create(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.BlogPost.objects.count(), 0)

        request.POST = {"subject": "Test", "body": "Hello"}

        response = views.blog_admin_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urls.reverse("admin:blog:index"))

        self.assertEqual(models.BlogPost.objects.count(), 1)
        post = models.BlogPost.objects.get()
        self.assertEqual(post.subject, "Test")
        self.assertEqual(post.body, "Hello")
        self.assertEqual(post.draft, True)

    def test_decorated(self):
        self.assertIn(is_secure_admin, views.blog_admin_create._inboxen_decorators)


class BlogAdminEditTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        post = BlogPostFactory(author=self.user)

        response = self.client.get(urls.reverse("admin:blog:edit", kwargs={"blog_pk": post.pk}))
        self.assertEqual(response.resolver_match.func, views.blog_admin_edit)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        post = BlogPostFactory(author=self.user)

        with self.assertRaises(Http404):
            views.blog_admin_edit(request, 0)

        response = views.blog_admin_edit(request, post.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["form"].instance, post)

    def test_post(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {}
        post = BlogPostFactory(author=self.user, draft=True, subject="no", body="no")

        response = views.blog_admin_edit(request, post.pk)
        self.assertEqual(response.status_code, 200)

        request.POST = {"subject": "Test", "body": "Hello"}

        response = views.blog_admin_edit(request, post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urls.reverse("admin:blog:index"))

        self.assertEqual(models.BlogPost.objects.count(), 1)
        post = models.BlogPost.objects.get()
        self.assertEqual(post.subject, "Test")
        self.assertEqual(post.body, "Hello")
        self.assertEqual(post.draft, False)

    def test_decorated(self):
        self.assertIn(is_secure_admin, views.blog_admin_edit._inboxen_decorators)


class BlogAdminDeleteTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(is_superuser=True)

    def test_url(self):
        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user)), \
                "Could not log in"

        grant_otp(self.client, self.user)
        grant_sudo(self.client)

        post = BlogPostFactory(author=self.user)

        response = self.client.get(urls.reverse("admin:blog:delete", kwargs={"blog_pk": post.pk}))
        self.assertEqual(response.resolver_match.func, views.blog_admin_delete)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        post = BlogPostFactory(author=self.user)

        with self.assertRaises(Http404):
            views.blog_admin_delete(request, 0)

        response = views.blog_admin_delete(request, post.pk)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        request.method = "POST"
        request.POST = {}
        post = BlogPostFactory(author=self.user)
        other_post = BlogPostFactory(author=self.user)

        response = views.blog_admin_delete(request, post.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.BlogPost.objects.count(), 2)

        request.POST = {"yes_delete": True}

        response = views.blog_admin_delete(request, post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urls.reverse("admin:blog:index"))

        self.assertEqual(models.BlogPost.objects.count(), 1)
        self.assertEqual(models.BlogPost.objects.get(), other_post)

    def test_decorated(self):
        self.assertIn(is_secure_admin, views.blog_admin_delete._inboxen_decorators)
