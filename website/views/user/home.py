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


from django.utils.translation import ugettext as _
from django.views import generic

from inboxen import models
from website.views import base

__all__ = ["UserHomeView"]


class UserHomeView(base.CommonContextMixin, base.LoginRequiredMixin, generic.ListView):
    """ The user's home which lists the inboxes """
    allow_empty = True
    paginate_by = 100
    template_name = "user/home.html"
    headline = _("Home")

    def get_queryset(self):
        queryset = models.Inbox.objects.viewable(self.request.user)
        queryset = queryset.select_related("domain")
        return queryset.add_last_activity().order_by("-last_activity")

    def get_context_data(self, **kwargs):
        context = super(UserHomeView, self).get_context_data(**kwargs)
        return context
