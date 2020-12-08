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

from csp.decorators import csp_replace
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone

from inboxen import models


@csp_replace(STYLE_SRC=["'self'", "'unsafe-inline'"])
def stats(request):
    try:
        stat = models.Statistic.objects.latest("date")
        first_stat = models.Statistic.objects.earliest("date")
    except models.Statistic.DoesNotExist:
        stat = None
        first_stat = None

    return TemplateResponse(request, "inboxen/stats.html", {"object": stat, "first_stat": first_stat})


def stats_recent(request):
    objects = reversed(models.Statistic.objects.order_by("-date")[:30])
    dates = []

    users = {
        "total": [],
        "active": [],
        "with_inboxes": [],
    }

    inboxes = {
        "total": [],
        "active": [],
        "disowned": [],
    }

    emails = {
        "total": [],
        "read": [],
    }

    for stat in objects:
        dates.append(stat.date)

        users["total"].append(stat.users.get("count", 0))
        users["active"].append(stat.users.get("active", 0))
        users["with_inboxes"].append(stat.users.get("with_inboxes", 0))

        # we might not have a total number here, so let's calculate it
        inbox_disowned = stat.inboxes.get("disowned", 0)
        inbox_total = stat.inboxes.get("total", stat.inboxes.get("inbox_count__sum", 0) + inbox_disowned)
        inboxes["total"].append(inbox_total)
        inboxes["active"].append(stat.inboxes.get("with_emails", 0))
        inboxes["disowned"].append(inbox_disowned)

        emails["total"].append(stat.emails.get("email_count__sum", 0))
        emails["read"].append(stat.emails.get("emails_read", 0))

    return JsonResponse({
        "dates": dates,
        "users": users,
        "inboxes": inboxes,
        "emails": emails,
        "now": timezone.now()
    })
