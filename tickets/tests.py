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

        QuestionFactory.create_batch(10, author=self.user)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("tickets-index")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        params = {"subject": "hello!", "body": "This is the body of my question"}
        response = self.client.post(self.get_url(), params)
        question = models.Question.objects.latest("date")
        self.assertRedirects(response, urlresolvers.reverse("tickets-detail", kwargs={"pk": question.pk}))


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
