##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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


from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.views import generic

from braces.views import LoginRequiredMixin
from watson import search

from inboxen import models

__all__ = ["UserHomeView", "FormHomeView"]


class UserHomeView(LoginRequiredMixin, generic.ListView):
    """ The user's home which lists the inboxes """
    allow_empty = True
    model = models.Inbox
    paginate_by = 100
    template_name = "inboxen/user/home.html"

    def get_queryset(self):
        qs = self.model.objects.viewable(self.request.user)
        qs = qs.select_related("domain")

        # ugly!
        # see https://code.djangoproject.com/ticket/19513
        # tl;dr Django uses a subquery when doing an `update` on a queryset,
        # but it doesn't strip out annotations
        # q?: does this still apply?
        if self.request.method != "POST":
            qs = qs.add_last_activity()
            qs = qs.order_by("-pinned", "disabled", "-last_activity").select_related("domain")
        return qs

    @search.skip_index_update()
    def post(self, *args, **kwargs):
        qs = self.get_queryset().filter(disabled=False)
        try:
            inbox = qs.from_string(email=self.request.POST["pin-inbox"], user=self.request.user)
        except (self.model.DoesNotExist, ValueError, KeyError):
            raise Http404

        inbox.pinned = not inbox.pinned
        inbox.save(update_fields=["pinned"])

        return HttpResponseRedirect(self.request.path)


class FormHomeView(UserHomeView):
    """POST-only view for JS stuff"""
    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed("Only POST requests please")

    def post(self, *args, **kwargs):
        response = super(FormHomeView, self).post(*args, **kwargs)

        # JS auto follows redirects, so change the response code
        # to allow us to detect success
        if response.status_code == 302:
            response.status_code = 204

        return response
