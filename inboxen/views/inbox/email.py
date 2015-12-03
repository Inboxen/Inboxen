##
#    Copyright (C) 2013-2015 Jessica Tallon & Matt Molyneaux
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

import logging

from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views import generic

from csp.decorators import csp_replace
from watson import search

from inboxen import models
from inboxen.utils.email import find_bodies
from inboxen.views import base

__all__ = ["EmailView"]

_log = logging.getLogger(__name__)


class EmailView(base.CommonContextMixin, base.LoginRequiredMixin, generic.DetailView):
    model = models.Email
    pk_url_kwarg = "id"
    template_name = 'inbox/email.html'

    @csp_replace(STYLE_SRC=["'self'", "'unsafe-inline'"])
    def get(self, *args, **kwargs):

        with search.skip_index_update():
            out = super(EmailView, self).get(*args, **kwargs)
            if "all-headers" in self.request.GET:
                self.object.flags.view_all_headers = bool(int(self.request.GET["all-headers"]))

            self.object.flags.read = True
            self.object.flags.seen = True
            self.object.save(update_fields=["flags"])
        return out

    def get_object(self, *args, **kwargs):
        # Convert the id from base 16 to 10
        self.kwargs[self.pk_url_kwarg] = int(self.kwargs[self.pk_url_kwarg], 16)
        return super(EmailView, self).get_object(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        queryset = super(EmailView, self).get_queryset(*args, **kwargs)
        queryset = queryset.viewable(self.request.user)
        queryset = queryset.filter(
            inbox__inbox=self.kwargs["inbox"],
            inbox__domain__domain=self.kwargs["domain"],
        ).select_related("inbox", "inbox__domain")
        return queryset

    def get_success_url(self):
        return self.request.path

    def post(self, *args, **kwargs):
        obj = self.get_object()

        if "important-toggle" in self.request.POST:
            with search.skip_index_update():
                obj.flags.important = not bool(obj.flags.important)
                obj.save(update_fields=["flags"])

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        if "all-headers" in self.request.GET:
            headers = None
            headers_fetch_all = bool(int(self.request.GET["all-headers"]))
        else:
            headers = cache.get(self.object.id, version="email-header")
            headers_fetch_all = bool(self.object.flags.view_all_headers)

        if headers is None:
            headers = models.Header.objects.filter(part__email=self.object, part__parent=None)
            if headers_fetch_all:
                headers = headers.get_many()
            else:
                headers = headers.get_many("Subject", "From")

        email_dict = {}
        email_dict["headers"] = headers
        email_dict["date"] = self.object.received_date
        email_dict["inbox"] = self.object.inbox
        email_dict["eid"] = self.object.eid

        # GET params for users with `ask_image` set in their profile
        if "imgDisplay" in self.request.GET and int(self.request.GET["imgDisplay"]) == 1:
            email_dict["display_images"] = True
            email_dict["ask_images"] = False
        elif self.request.user.userprofile.flags.ask_images:
            email_dict["display_images"] = False
            email_dict["ask_images"] = True
        else:
            email_dict["display_images"] = self.request.user.userprofile.flags.display_images
            email_dict["ask_images"] = False

        # iterate over MIME parts
        attachments = self.object.get_parts()

        email_dict["bodies"] = []
        email_dict["has_images"] = False

        find_bodies(self.request, email_dict, attachments[:1])

        self.headline = email_dict["headers"].get("Subject", _("No Subject"))

        for body in email_dict["bodies"]:
            assert isinstance(body, unicode), "body is %r" % type(body)

        context = super(EmailView, self).get_context_data(**kwargs)
        context.update({
            "email": email_dict,
            "attachments": attachments,
            "headersfetchall": headers_fetch_all,
        })

        return context
