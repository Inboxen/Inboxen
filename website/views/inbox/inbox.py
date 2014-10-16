##
#    Copyright (C) 2013-2014 Jessica Tallon & Matt Molyneaux
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

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import F, Q
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.utils.timesince import timesince
from django.views import generic

from aggregate_if import Count as ConditionalCount
import watson

from inboxen import models
from queue.delete.tasks import delete_inboxen_item
from queue.tasks import deal_with_flags
from website.views import base

__all__ = ["UnifiedInboxView", "SingleInboxView"]

class InboxView(
                base.CommonContextMixin,
                base.LoginRequiredMixin,
                generic.ListView
                ):
    """Base class for Inbox views"""
    model = models.Email
    paginate_by = 100
    template_name = 'inbox/inbox.html'

    def get_success_url(self):
        """Override this method to return the URL to return the user to"""
        raise NotImplementedError

    def get_queryset(self, *args, **kwargs):
        qs = super(InboxView, self).get_queryset(*args, **kwargs).distinct()
        qs = qs.filter(inbox__user=self.request.user, flags=F('flags').bitand(~models.Email.flags.deleted))
        qs = qs.filter(inbox__flags=F('inbox__flags').bitand(~models.Inbox.flags.deleted))
        qs = qs.annotate(important=ConditionalCount('id', only=Q(flags=models.Email.flags.important)))
        qs = qs.order_by("-important", "-received_date").select_related("inbox", "inbox__domain")
        return qs

    def post(self, *args, **kwargs):
        qs = self.get_queryset()

        # this is kinda bad, but nested forms aren't supported in all browsers
        if "delete-single" in self.request.POST:
            email_id = int(self.request.POST["delete-single"], 16)
            email = qs.get(id=email_id)
            email.delete()
            return HttpResponseRedirect(self.get_success_url())
        elif "important-single" in self.request.POST:
            with watson.skip_index_update():
                email_id = int(self.request.POST["important-single"], 16)
                email = qs.get(id=email_id)
                email.flags.important = not email.flags.important
                email.save(update_fields=["flags"])
                return HttpResponseRedirect(self.get_success_url())

        emails = []
        for email in self.request.POST:
            if self.request.POST[email] == "email":
                try:
                    email_id = int(email, 16)
                    emails.append(email_id)
                except ValueError:
                    return HttpResponseRedirect(self.get_success_url())

        if len(emails) == 0:
            # nothing was selected, return early
            return HttpResponseRedirect(self.get_success_url())

        # Something between Bitfield and Django's ORM doesn't like out complex queries
        emails = qs.filter(id__in=emails).order_by("id").only("id")
        email_ids = list(emails.values_list('id', flat=True))
        emails = self.model.objects.filter(id__in=email_ids).only("id")

        with watson.skip_index_update():
            if "unimportant" in self.request.POST:
                emails.update(flags=F('flags').bitand(~self.model.flags.important))
            elif "important" in self.request.POST:
                emails.update(flags=F('flags').bitor(self.model.flags.important))
            elif "delete" in self.request.POST:
                emails.update(flags=F('flags').bitor(self.model.flags.deleted))
                emails = delete_inboxen_item.chunks(emails, 500).group()
                emails.skew(step=50)
                emails.apply_async()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super(InboxView, self).get_context_data(*args, **kwargs)

        object_list = []
        object_id_list = []
        for email in context["page_obj"].object_list:
            object_list.append(email)
            object_id_list.append(email.id)

        if len(object_id_list) == 0:
            return context

        headers = cache.get_many(object_id_list, version="email-header")

        missing_list = set(object_id_list) - set(headers.keys())
        if len(missing_list) > 0:
            missing_headers = models.Header.objects.filter(part__parent=None, part__email__in=missing_list)
            missing_headers = missing_headers.get_many("Subject", "From", group_by="part__email_id")
            headers.update(missing_headers)
            cache.set_many(missing_headers, version="email-header", timeout=None)

        timesinces = cache.get_many(object_id_list, version="email-timesince")
        timesince_cache_miss = {}

        for email in object_list:
            header_set = headers[email.id]
            email.subject = header_set.get("Subject")
            email.sender = header_set["From"]

            if email.id in timesinces:
                email.timesince = timesinces[email.id]
            else:
                # cache miss
                since = timesince(email.received_date)
                email.timesince = since
                timesince_cache_miss[email.id] = since

        cache.set_many(timesince_cache_miss, version="email-timesince")

        inbox = getattr(self, 'inbox_obj', None)
        if inbox is not None:
            inbox = inbox.id

        deal_with_flags.delay(object_id_list, self.request.user.id, inbox)
        return context

class UnifiedInboxView(InboxView):
    """View all inboxes together"""
    def get_success_url(self):
        return reverse('unified-inbox')

    def get_queryset(self, *args, **kwargs):
        qs = super(UnifiedInboxView, self).get_queryset(*args, **kwargs)
        qs = qs.filter(inbox__flags=~models.Inbox.flags.exclude_from_unified)
        return qs

    def get_context_data(self, *args, **kwargs):
        self.headline = _("Inbox")
        profile = self.request.user.userprofile
        if profile.flags.unified_has_new_messages:
            profile.flags.unified_has_new_messages = False
            profile.save(update_fields=["flags"])

        return super(UnifiedInboxView, self).get_context_data(*args, **kwargs)

class SingleInboxView(InboxView):
    """View a single inbox"""
    def get_success_url(self):
        return reverse('single-inbox', kwargs={"inbox": self.kwargs["inbox"], "domain": self.kwargs["domain"]})

    def get_queryset(self, *args, **kwargs):
        try:
            self.inbox_obj = models.Inbox.objects.get(inbox=self.kwargs["inbox"], domain__domain=self.kwargs["domain"])
        except models.Inbox.DoesNotExist:
            raise Http404(_("No Inbox found matching the query."))
        qs = super(SingleInboxView, self).get_queryset(*args, **kwargs)
        qs = qs.filter(inbox=self.inbox_obj)
        return qs

    def get_context_data(self, *args, **kwargs):
        self.headline = "{0}@{1}".format(self.kwargs["inbox"], self.kwargs["domain"])
        context = super(SingleInboxView, self).get_context_data(*args, **kwargs)
        context.update({"inbox":self.kwargs["inbox"], "domain":self.kwargs["domain"]})

        if self.inbox_obj.flags.new:
            with watson.skip_index_update():
                self.inbox_obj.flags.new = False
                self.inbox_obj.save(update_fields=["flags"])

        return context
