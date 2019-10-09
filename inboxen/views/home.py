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


from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.views import generic

from inboxen import models
from inboxen.search.tasks import search_home_page
from inboxen.search.utils import create_search_cache_key
from inboxen.search.views import SearchMixin

__all__ = ["UserHomeView", "FormHomeView"]


class UserHomeView(LoginRequiredMixin, SearchMixin, generic.ListView):
    """ The user's home which lists the inboxes """
    allow_empty = True
    model = models.Inbox
    paginate_by = 25
    template_name = "inboxen/home.html"

    def get_queryset(self):
        if self.query == "":
            qs = self.model.objects.order_by("-pinned", "disabled", "-last_activity")
        else:
            qs = self.get_search_queryset()
        qs = qs.viewable(self.request.user).add_last_activity().select_related("domain")
        return qs

    def post(self, *args, **kwargs):
        qs = self.get_queryset().filter(disabled=False)
        try:
            inbox = qs.from_string(email=self.request.POST["pin-inbox"], user=self.request.user)
        except (self.model.DoesNotExist, ValueError, KeyError):
            raise Http404

        inbox.pinned = not inbox.pinned
        inbox.save(update_fields=["pinned"])

        return HttpResponseRedirect(self.request.path)

    def search_task(self):
        kwargs = {
            "user_id": self.request.user.id,
            "search_term": self.query,
            "before": self.first_item,
            "after": self.last_item,
        }

        return search_home_page.apply_async(kwargs=kwargs)

    def get_cache_key(self):
        return create_search_cache_key(
            self.request.user.id,
            self.query,
            "home",
            self.first_item,
            self.last_item,
        )


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
