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

from django.conf import settings as dj_settings
from django.core import urlresolvers

from inboxen import models
from inboxen.tests import factories
from inboxen.test import InboxenTestCase, MockRequest


class HomeViewTestCase(InboxenTestCase):
    def setUp(self):
        super(HomeViewTestCase, self).setUp()
        self.user = factories.UserFactory()
        domain = factories.DomainFactory()
        self.inboxes = factories.InboxFactory.create_batch(150, domain=domain, user=self.user)

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-home")

    def test_context(self):
        response = self.client.get(self.get_url())
        context_settings = response.context['settings']

        # test that something is getting set
        self.assertEqual(dj_settings.SITE_NAME, context_settings["SITE_NAME"])

        # test that INBOXEN_COMMIT_ID is actually working
        self.assertNotEqual("UNKNOWN", context_settings["INBOXEN_COMMIT_ID"])

        try:
            int(context_settings["INBOXEN_COMMIT_ID"], 16)
        except ValueError:
            self.fail("context_settings[\"INBOXEN_COMMIT_ID\"] is not a valid commit ID")

        # Please add any settings that may contain passwords or secrets:
        self.assertNotIn("SECRET_KEY", context_settings)
        self.assertNotIn("DATABASES", context_settings)

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_pinned_first(self):
        # Mark some specific inboxes based on activity. One for most recent, one
        # in the middel and then the least recent.
        ordered_inboxes = models.Inbox.objects.all().add_last_activity()
        ordered_inboxes = ordered_inboxes.order_by("-last_activity")

        # Most recent activity
        latest = ordered_inboxes[0]
        latest.flags.pinned = True
        latest.save()

        # Around (or exactly) the middle in activity.
        middle = ordered_inboxes[int(len(ordered_inboxes) / 2)]
        middle.flags.pinned = True
        middle.save()

        # Finally the least active (NB: negative indexing isn't supported).
        least = ordered_inboxes[len(ordered_inboxes)-1]
        least.flags.pinned = True
        least.save()

        response = self.client.get(self.get_url())
        objs = response.context["page_obj"].object_list[:5]

        # Check the top inboxes three inboxes are pinned.
        self.assertEqual(
            [bool(obj.flags.pinned) for obj in objs],
            [True, True, True, False, False]
        )

        # Check the pinned inboxes are ordered amongst themselves.
        self.assertEqual(
            [obj.id for obj in objs][:3],
            [latest.id, middle.id, least.id]
        )

    def test_disabled_sink(self):
        """ Check disabled inboxes sink to the bottom """
        # Find three inboxes, the inbox with: the most recent activity, least
        # recent activity and then pick one from the middle. This insures that
        # they sink to the bottom but keep their order within the disabled.
        ordered_inboxes = models.Inbox.objects.all().add_last_activity()
        ordered_inboxes = ordered_inboxes.order_by("-last_activity")

        # The inbox with the latest activity.
        latest = ordered_inboxes[0]
        latest.flags.disabled = True
        latest.save()

        # One from the middle
        middle = ordered_inboxes[int(len(ordered_inboxes) / 2)]
        middle.flags.disabled = True
        middle.save()

        # Finally the least active (NB: negative indexing isn't supported).
        least = ordered_inboxes[len(ordered_inboxes)-1]
        least.flags.disabled = True
        least.save()

        # Get the page, they should have been pushed to the second page.
        response = self.client.get(self.get_url() + "2/")
        objs = response.context["page_obj"].object_list[45:]

        # Check the last three are disabled
        self.assertEqual(
            [bool(obj.flags.disabled) for obj in objs],
            [False, False, True, True, True]
        )

        # Check the three are in order amongst themselves.
        self.assertEqual(
            [obj.id for obj in objs[2:]],
            [latest.id, middle.id, least.id]
        )

    def test_pagin(self):
        # there should be 150 inboxes in the test fixtures
        # and pages are paginated by 100 items
        response = self.client.get(self.get_url() + "2/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.get_url() + "3/")
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        inbox = self.inboxes[0]
        was_pinned = bool(inbox.flags.pinned)

        # pin
        response = self.client.post(self.get_url(), {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 302)

        inbox.refresh_from_db()
        self.assertNotEqual(bool(inbox.flags.pinned), was_pinned)

        # toggle
        response = self.client.post(self.get_url(), {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 302)

        inbox.refresh_from_db()
        self.assertEqual(bool(inbox.flags.pinned), was_pinned)

        # invalid
        response = self.client.post(self.get_url(), {"pin-inbox": "aagfdsgsfdg"})
        self.assertEqual(response.status_code, 404)

        # disabled
        inbox.flags.disabled = True
        inbox.save()
        response = self.client.post(self.get_url(), {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 404)

    def test_post_form_view(self):
        url = urlresolvers.reverse("form-home")

        inbox = self.inboxes[0]
        was_pinned = bool(inbox.flags.pinned)

        # pin
        response = self.client.post(url, {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 204)

        inbox.refresh_from_db()
        self.assertNotEqual(bool(inbox.flags.pinned), was_pinned)

        # toggle
        response = self.client.post(url, {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 204)

        inbox.refresh_from_db()
        self.assertEqual(bool(inbox.flags.pinned), was_pinned)

        # invalid
        response = self.client.post(url, {"pin-inbox": "aagfdsgsfdg"})
        self.assertEqual(response.status_code, 404)

        # disabled
        inbox.flags.disabled = True
        inbox.save()
        response = self.client.post(url, {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 404)
