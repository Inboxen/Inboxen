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

from django.http import Http404
from django.views import generic
from django.utils.translation import ugettext as _

from termsofservice import models


class TOSView(generic.DetailView):
    model = models.TOS
    template_name = "termsofservice/tos.html"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.filter(published=True).latest()
        except self.model.DoesNotExist:
            raise Http404


class WhoView(generic.ListView):
    model = models.StaffProfile
    template_name = "termsofservice/who.html"

    def get_queryset(self):
        qs = super(WhoView, self).get_queryset()
        return qs.filter(user__is_staff=True).select_related("user")


class HelpView(generic.TemplateView):
    template_name = "termsofservice/index.html"

    def get_context_data(self, **kwargs):
        kwargs["tos_exists"] = models.TOS.objects.filter(published=True).exists()
        kwargs["who_exists"] = models.StaffProfile.objects.filter(user__is_staff=True).exists()
        return super(HelpView, self).get_context_data(**kwargs)
