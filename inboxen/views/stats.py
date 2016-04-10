##
#    Copyright (C) 2014 Jessica Tallon & Matthew Molyneaux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views import generic
from django.views.decorators.cache import cache_page

from inboxen import models
from inboxen.views import base


class StatsView(base.CommonContextMixin, generic.DetailView):
    template_name = "inboxen/stats.html"
    headline = _("Server Statistics")
    model = models.Statistic

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()

        try:
            return queryset.latest("date")
        except models.Statistic.DoesNotExist:
            return None


@cache_page(1800)
def stats_recent(request):
    objects = models.Statistic.objects.order_by("date")
    dates = []
    users = []
    inboxes = []
    emails = []

    for stat in objects:
        dates.append(stat.date)
        users.append(stat.users.get("count"))
        inboxes.append(stat.inboxes.get("inbox_count__sum"))
        emails.append(stat.emails.get("email_count__sum"))

    return JsonResponse({"dates": dates, "users": users, "inboxes": inboxes, "emails": emails, "now": timezone.now()})
