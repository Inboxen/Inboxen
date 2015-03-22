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
from django.core import mail, urlresolvers

import factory
import factory.fuzzy

from inboxen.tests import factories
from tickets import models


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Question

    subject = factory.fuzzy.FuzzyText()
    body = factory.fuzzy.FuzzyText()


class ResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Response

    body = factory.fuzzy.FuzzyText()


class QuestionViewTestCase(test.TestCase):
    def setUp(self):
        super(QuestionViewTestCase, self).setUp()
        self.user = factories.UserFactory()
        self.other_user = factories.UserFactory(username="tester")

        QuestionFactory.create_batch(11, author=self.user, status=models.Question.NEW)
        QuestionFactory.create_batch(3, author=self.other_user, status=models.Question.RESOLVED)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("tickets-index")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        self.assertIn("More Open Tickets", response.content)
        self.assertNotIn("More Closed Tickets", response.content)

    def test_switch_open_closed(self):
        models.Question.objects.filter(status=models.Question.NEW).update(author=self.other_user)
        models.Question.objects.filter(status=models.Question.RESOLVED).update(author=self.user)

        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        self.assertNotIn("More Open Tickets", response.content)
        self.assertIn("More Closed Tickets", response.content)

    def test_post(self):
        params = {"subject": "hello!", "body": "This is the body of my question"}
        response = self.client.post(self.get_url(), params)
        question = models.Question.objects.latest("date")
        self.assertRedirects(response, urlresolvers.reverse("tickets-detail", kwargs={"pk": question.pk}))


class QuestionListTestCase(test.TestCase):
    def setUp(self):
        super(QuestionListTestCase, self).setUp()
        self.user = factories.UserFactory()

        QuestionFactory.create_batch(75, author=self.user, status=models.Question.NEW)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("tickets-list", kwargs={"status":"!resolved"})

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.get_url() + "2/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.get_url() + "3/")
        self.assertEqual(response.status_code, 404)


@test.utils.override_settings(ADMINS=(("admin", "root@localhost"),))
class QuestionNoticeTestCase(test.TestCase):
    def setUp(self):
        super(QuestionNoticeTestCase, self).setUp()
        self.user = factories.UserFactory()

    def test_admins_emailed(self):
        question = models.Question()
        question.author = self.user
        question.subject = "Hey"
        question.body = "Sort it out!"

        question.save()

        self.assertEqual(len(mail.outbox), 1)

        question2 = models.Question.objects.get(id=question.id)
        question2.save()

        self.assertEqual(len(mail.outbox), 1)
