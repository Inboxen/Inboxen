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

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views import generic

from inboxen import models
from inboxen.search.tasks import search_single_inbox, search_unified_inbox
from inboxen.search.utils import create_search_cache_key
from inboxen.search.views import SearchMixin
from inboxen.tasks import delete_inboxen_item, set_emails_to_seen
from inboxen.utils.tasks import task_group_skew


class InboxView(LoginRequiredMixin, SearchMixin, generic.ListView):
    """Base class for Inbox views"""
    model = models.Email
    paginate_by = settings.INBOX_PAGE_SIZE
    template_name = 'inboxen/inbox/inbox.html'

    def get_success_url(self):
        return self.request.path

    def get_queryset(self, *args, **kwargs):
        if self.query == "":
            qs = super().get_queryset().order_by("-important", "-received_date")
        else:
            qs = self.get_search_queryset().select_related("inbox", "inbox__domain")
        qs = qs.viewable(self.request.user)
        return qs

    def post(self, *args, **kwargs):
        qs = self.get_queryset()

        # this is kinda bad, but nested forms aren't supported in all browsers
        if "delete-single" in self.request.POST:
            try:
                email_id = int(self.request.POST["delete-single"], 16)
                email = qs.get(id=email_id)
            except (self.model.DoesNotExist, ValueError):
                raise Http404

            email.delete()

            return HttpResponseRedirect(self.get_success_url())
        elif "important-single" in self.request.POST:
            try:
                email_id = int(self.request.POST["important-single"], 16)
                email = qs.get(id=email_id)
            except (self.model.DoesNotExist, ValueError):
                raise Http404

            email.important = not email.important
            email.save(update_fields=["important"])

            return HttpResponseRedirect(self.get_success_url())

        emails = []
        for email in self.request.POST:
            if self.request.POST[email] == "email":
                try:
                    email_id = int(email, 16)
                    emails.append(email_id)
                except ValueError:
                    raise Http404

        if len(emails) == 0:
            # nothing was selected, return early
            return HttpResponseRedirect(self.get_success_url())

        qs = qs.filter(id__in=emails).order_by("id")
        if "unimportant" in self.request.POST:
            qs.update(important=False)
        elif "important" in self.request.POST:
            qs.update(important=True)
        elif "delete" in self.request.POST:
            email_ids = [("email", email.id) for email in qs]
            qs.update(deleted=True)
            delete_task = delete_inboxen_item.chunks(email_ids, 500).group()
            task_group_skew(delete_task, step=50)
            delete_task.apply_async()

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

        for email in object_list:
            header_set = headers[email.id]
            email.subject = header_set.get("Subject")
            email.sender = header_set["From"]

        inbox = getattr(self, 'inbox_obj', None)
        if inbox is not None:
            inbox = inbox.id

        set_emails_to_seen.delay(object_id_list, self.request.user.id, inbox)
        return context


class FormInboxView(InboxView):
    """POST-only view for JS stuff"""
    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed("Only POST requests please")

    def post(self, *args, **kwargs):
        response = super(FormInboxView, self).post(*args, **kwargs)

        # JS auto follows redirects, so change the response code
        # to allow us to detect success
        if response.status_code == 302:
            response.status_code = 204

        return response


class UnifiedInboxView(InboxView):
    """View all inboxes together"""
    def get_queryset(self):
        qs = super(UnifiedInboxView, self).get_queryset()
        qs = qs.filter(inbox__exclude_from_unified=False)
        return qs

    def get_context_data(self, *args, **kwargs):
        kwargs["headline"] = _("Inbox")
        profile = self.request.user.inboxenprofile
        if profile.unified_has_new_messages:
            profile.unified_has_new_messages = False
            profile.save(update_fields=["unified_has_new_messages"])

        kwargs["unified"] = True

        return super(UnifiedInboxView, self).get_context_data(*args, **kwargs)

    def post(self, *args, **kwargs):
        try:
            return super(UnifiedInboxView, self).post(*args, **kwargs)
        except Http404:
            return HttpResponseRedirect(self.get_success_url())

    def search_task(self):
        kwargs = {
            "user_id": self.request.user.id,
            "search_term": self.query,
            "before": self.first_item,
            "after": self.last_item,
        }

        return search_unified_inbox.apply_async(kwargs=kwargs)

    def get_cache_key(self):
        return create_search_cache_key(
            self.request.user.id,
            self.query,
            "inbox:unified",
            self.first_item,
            self.last_item,
        )


class SingleInboxView(InboxView):
    """View a single inbox"""
    def get_queryset(self):
        try:
            self.inbox_obj = models.Inbox.objects.viewable(self.request.user)
            self.inbox_obj = self.inbox_obj.get(inbox=self.kwargs["inbox"], domain__domain=self.kwargs["domain"])
        except models.Inbox.DoesNotExist:
            raise Http404(_("No Inbox found matching the query."))
        qs = super(SingleInboxView, self).get_queryset()
        qs = qs.filter(inbox=self.inbox_obj)
        return qs

    def get_context_data(self, *args, **kwargs):
        kwargs["headline"] = u"{0}@{1}".format(self.kwargs["inbox"], self.kwargs["domain"])
        context = super(SingleInboxView, self).get_context_data(*args, **kwargs)
        context.update({"inbox": self.kwargs["inbox"], "domain": self.kwargs["domain"], "inbox_obj": self.inbox_obj})

        if self.inbox_obj.new:
            self.inbox_obj.new = False
            self.inbox_obj.save(update_fields=["new"])

        return context

    def post(self, *args, **kwargs):
        try:
            return super(SingleInboxView, self).post(*args, **kwargs)
        except Http404:
            return HttpResponseRedirect(self.get_success_url())

    def search_task(self):
        kwargs = {
            "user_id": self.request.user.id,
            "search_term": self.query,
            "inbox": str(self.inbox_obj),
            "before": self.first_item,
            "after": self.last_item,
        }

        return search_single_inbox.apply_async(kwargs=kwargs)

    def get_cache_key(self):
        return create_search_cache_key(
            self.request.user.id,
            self.query,
            "inbox:{}".format(self.inbox_obj),
            self.first_item,
            self.last_item,
        )
