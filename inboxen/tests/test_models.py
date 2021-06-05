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

from unittest import mock
import datetime
import itertools

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone

from inboxen import models
from inboxen.test import InboxenTestCase
from inboxen.tests import factories

User = get_user_model()


class ModelTestCase(InboxenTestCase):
    """Test our custom methods"""
    def test_domain_queryset_methods(self):
        user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        # all the permutations of Domains
        for args in itertools.product([True, False], [user, other_user, None]):
            factories.DomainFactory(enabled=args[0], owner=args[1])

        self.assertEqual(models.Domain.objects.available(user).count(), 2)
        self.assertEqual(models.Domain.objects.receiving().count(), 3)

    def test_inbox_create(self):
        user = factories.UserFactory()
        domain = factories.DomainFactory()

        with self.assertRaises(models.Domain.DoesNotExist):
            models.Inbox.objects.create()

        inbox = models.Inbox.objects.create(domain=domain, user=user)

        self.assertIsInstance(inbox.created, datetime.datetime)
        self.assertEqual(inbox.user, user)

    def test_inbox_create_reserved(self):
        user = factories.UserFactory()
        domain = factories.DomainFactory()

        def reserved_mock():
            # return True and then False, regardless of input
            ret_vals = [False, True]

            def inner(*args, **kwargs):
                return ret_vals.pop()

            return inner

        with mock.patch("inboxen.managers.is_reserved") as r_mock:
            r_mock.side_effect = reserved_mock()
            models.Inbox.objects.create(domain=domain, user=user)

            self.assertEqual(r_mock.call_count, 2)

    def test_inbox_create_integrity_error(self):
        user = factories.UserFactory()
        domain = factories.DomainFactory()
        inbox = models.Inbox.objects.create(domain=domain, user=user)

        def get_random_string_mock():
            # list of inboxes to be returned, in reverse order
            inboxes = ["a" * len(inbox.inbox), inbox.inbox]

            def inner(*args, **kwargs):
                return inboxes.pop()

            return inner

        with mock.patch("inboxen.managers.get_random_string") as r_mock:
            r_mock.side_effect = get_random_string_mock()
            new_inbox = models.Inbox.objects.create(domain=domain, user=user)

            self.assertEqual(new_inbox.inbox, "a" * len(inbox.inbox))
            self.assertEqual(r_mock.call_count, 2)

    def test_inbox_create_length(self):
        user = factories.UserFactory()
        domain = factories.DomainFactory()
        default_length = settings.INBOX_LENGTH

        with override_settings(INBOX_LENGTH=default_length + 1):
            inbox = models.Inbox.objects.create(user=user, domain=domain)
            self.assertEqual(len(inbox.inbox), default_length + 1)

            inbox = models.Inbox.objects.create(user=user, domain=domain, length=default_length + 3)
            self.assertEqual(len(inbox.inbox), default_length + 3)

        with self.assertRaises(AssertionError):
            inbox = models.Inbox.objects.create(user=user, domain=domain, length=-1)

    def test_inbox_from_string(self):
        user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        inbox = factories.InboxFactory(user=user)
        email = "%s@%s" % (inbox.inbox, inbox.domain.domain)

        inbox2 = user.inbox_set.from_string(email=email)

        self.assertEqual(inbox, inbox2)

        with self.assertRaises(models.Inbox.DoesNotExist):
            other_user.inbox_set.from_string(email=email)

    def test_inbox_receiving(self):
        # all the permutations of Inboxes that can receive
        params = (
            [True, False],  # domain enabled
            [True, False],  # deleted
            [True, False],  # disabled
            [factories.UserFactory, None],   # user
            [models.UserProfile.REJECT_MAIL,
             models.UserProfile.DELETE_MAIL],  # quota options
            [99, 100, 101],  # quota percent
            [True, False],  # receiving_emails
        )
        for args in itertools.product(*params):
            if args[3] is not None:
                user = args[3]()
                user.inboxenprofile.quota_options = args[4]
                user.inboxenprofile.quota_percent_usage = args[5]
                user.inboxenprofile.receiving_emails = args[6]
                user.inboxenprofile.save()
            else:
                user = None

            factories.InboxFactory(domain__enabled=args[0], deleted=args[1], disabled=args[1], user=user)

        for inbox in models.Inbox.objects.receiving():
            self.assertFalse(inbox.deleted)
            self.assertFalse(inbox.disabled)
            self.assertTrue(inbox.domain.enabled)
            self.assertNotEqual(inbox.user, None)
            self.assertEqual(inbox.user.inboxenprofile.quota_percent_usage, 99)
            self.assertEqual(inbox.user.inboxenprofile.receiving_emails, True)

        for inbox in models.Inbox.objects.exclude(id__in=models.Inbox.objects.receiving()):
            truth_values = [inbox.deleted, inbox.disabled, not inbox.domain.enabled, inbox.user is None,
                            inbox.user is not None and inbox.user.inboxenprofile.quota_percent_usage > 99,
                            inbox.user is not None and not inbox.user.inboxenprofile.receiving_emails]

            self.assertTrue(any(truth_values), truth_values)

        self.assertEqual(models.Inbox.objects.receiving().count(), 4)

    def test_inbox_viewable(self):
        user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        # all the permutations of Inboxes that can be viewed
        params = (
            [True, False],             # deleted
            [True, False],             # disabled
            [user, other_user, None],  # user
        )
        for args in itertools.product(*params):
            factories.InboxFactory(deleted=args[0], disabled=args[1], user=args[2])

        count = models.Inbox.objects.viewable(user).count()
        self.assertEqual(count, 2)

    def test_inbox_disowned(self):
        factories.InboxFactory(user=factories.UserFactory())
        disowned = factories.InboxFactory(user=None)

        qs = models.Inbox.objects.disowned()
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0].id, disowned.id)

    def test_email_viewable(self):
        user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        # all the permutations of Emailss that can be viewed
        params = (
            [True, False],             # inbox deleted
            [True, False],             # inbox disabled
            [user, other_user, None],  # user
            [True, False],             # email deleted
            [True, False],             # email read (i.e. any other bool has been set)
        )
        for args in itertools.product(*params):
            factories.EmailFactory(
                inbox__deleted=args[0],
                inbox__disabled=args[1],
                inbox__user=args[2],
                deleted=args[3],
                read=args[4],
            )

        count = models.Email.objects.viewable(user).count()
        self.assertEqual(count, 4)

    def test_add_last_activity(self):
        now = timezone.now()

        email = factories.EmailFactory(received_date=now)
        email.inbox.created = now - datetime.timedelta(2)
        email.inbox.save()

        inbox = factories.InboxFactory()
        inbox.created = now - datetime.timedelta(1)
        inbox.save()

        inboxes = list(models.Inbox.objects.all().add_last_activity().order_by("-last_activity"))
        self.assertEqual(inboxes[0].last_activity, now)
        self.assertEqual(inboxes[1].last_activity, now - datetime.timedelta(1))

    def test_last_activity_deleted_mail(self):
        now = timezone.now()

        email = factories.EmailFactory(received_date=now, deleted=True)
        email.inbox.created = now - datetime.timedelta(2)
        email.inbox.save()

        inbox = factories.InboxFactory()
        inbox.created = now - datetime.timedelta(1)
        inbox.save()

        inboxes = list(models.Inbox.objects.all().add_last_activity().order_by("-last_activity"))
        self.assertEqual(inboxes[0].last_activity, now - datetime.timedelta(1))
        self.assertEqual(inboxes[1].last_activity, now - datetime.timedelta(2))

    def test_header_create(self):
        name = "X-Hello"
        data = "Hewwo"
        body = models.Body.objects.create(data=b"Hello", hashed="fakehash")
        part = models.PartList.objects.create(email=factories.EmailFactory(), body=body)

        header1 = part.header_set.create(name=name, data=data, ordinal=0)
        header2 = part.header_set.create(name=name, data=data, ordinal=1)

        self.assertEqual(header1[0].name_id, header2[0].name_id)
        self.assertEqual(header1[0].data_id, header2[0].data_id)
        self.assertEqual(header1[0].name.name, name)
        self.assertEqual(header1[0].data.data, data)
        self.assertTrue(header1[1])
        self.assertFalse(header2[1])

    def test_header_null_bytes(self):
        name = "X-Hello"
        data = "Hewwo \x00 test"
        body = models.Body.objects.create(data=b"Hello", hashed="fakehash")
        part = models.PartList.objects.create(email=factories.EmailFactory(), body=body)

        header, _ = part.header_set.create(name=name, data=data, ordinal=0)
        self.assertNotEqual(header.data.data, data)
        self.assertEqual(header.data.data, "Hewwo  test")

    def test_body_get_or_create(self):
        body_data = b"Hello"

        body1 = models.Body.objects.get_or_create(data=body_data)
        body2 = models.Body.objects.get_or_create(data=body_data)

        self.assertEqual(body1[0].id, body2[0].id)
        self.assertTrue(body1[1])
        self.assertFalse(body2[1])

    def test_liberation_can_request_another(self):
        # it's just a smoke test for now
        now = timezone.now()
        user = factories.UserFactory()
        params = (
            [True, False],  # running
            [None, now - datetime.timedelta(days=8), now - datetime.timedelta(days=6)],  # started
            [None, now - datetime.timedelta(days=8), now - datetime.timedelta(days=6)],  # last_finished
        )
        results = []
        for args in itertools.product(*params):
            lib = models.Liberation(
                user=user,
                running=args[0],
                started=args[1],
                last_finished=args[2],
            )
            results.append(lib.can_request_another)

        self.assertEqual(len(results), 18)
        self.assertEqual(results.count(True), 6)
        self.assertEqual(results.count(False), 12)


class ModelReprTestCase(InboxenTestCase):
    """Repr is very useful when debugging via the shell"""

    def test_body(self):
        body = models.Body(hashed="1234")
        self.assertEqual(repr(body), "<Body: 1234>")

    def test_domain(self):
        domain = models.Domain(domain="example.com")
        self.assertEqual(repr(domain), "<Domain: example.com>")

    def test_email(self):
        email = models.Email(id=1234)
        self.assertEqual(repr(email), "<Email: 4d2>")

    def test_header(self):
        header = models.Header(name=models.HeaderName(name="example"))
        self.assertEqual(repr(header), "<Header: example>")

    def test_header_data(self):
        data = models.HeaderData(hashed="1234")
        self.assertEqual(repr(data), "<HeaderData: 1234>")

    def test_header_name(self):
        name = models.HeaderName(name="example")
        self.assertEqual(repr(name), "<HeaderName: example>")

    def test_inbox(self):
        inbox = models.Inbox(inbox="inbox", domain=models.Domain(domain="example.com"))
        self.assertEqual(repr(inbox), "<Inbox: inbox@example.com>")
        inbox.deleted = True
        self.assertEqual(repr(inbox), "<Inbox: inbox@example.com (deleted)>")

    def test_liberation(self):
        liberation = models.Liberation(user=User(username="example"))
        self.assertEqual(repr(liberation), "<Liberation: Liberation for example>")

    def test_partlist(self):
        part = models.PartList(id="1234")
        self.assertEqual(repr(part), "<PartList: 1234>")

    def test_statistic(self):
        now = timezone.now()
        stat = models.Statistic(date=now)
        self.assertEqual(repr(stat), "<Statistic: %s>" % now)

    def test_inboxenprofile(self):
        profile = models.UserProfile(user=User(username="example"))
        self.assertEqual(repr(profile), "<UserProfile: Profile for example>")
