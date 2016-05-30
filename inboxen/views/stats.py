##
#    Copyright (C) 2014, 2016 Jessica Tallon & Matthew Molyneaux
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

from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.utils import timezone

from inboxen import models


def stats(request):
    try:
        stat = models.Statistic.objects.latest("date")
    except models.Statistic.DoesNotExist:
        stat = None

    return TemplateResponse(request, "inboxen/stats.html", {"object": stat})


def stats_recent(request):
    objects = reversed(models.Statistic.objects.order_by("-date")[:90])
    dates = []
    users = []
    active_users = []
    inboxes = []
    active_inboxes = []
    emails = []
    read_emails = []

    for stat in objects:
        dates.append(stat.date)

        users.append(stat.users.get("count"))
        active_users.append(stat.users.get("with_inboxes"))

        inboxes.append(stat.inboxes.get("inbox_count__sum"))
        active_inboxes.append(stat.inboxes.get("with_emails"))

        emails.append(stat.emails.get("email_count__sum"))
        read_emails.append(stat.emails.get("emails_read"))

    return JsonResponse({
        "dates": dates,
        "users": users,
        "active_users": active_users,
        "inboxes": inboxes,
        "active_inboxes": active_inboxes,
        "emails": emails,
        "read_emails": read_emails,
        "now": timezone.now()
    })
