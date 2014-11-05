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

from django.utils.translation import ugettext as _
from django.views import generic

from inboxen import models
from website.views import base


class StatsView(base.CommonContextMixin, generic.DetailView):
    template_name = "stats.html"
    headline = _("Server Statistics")
    model = models.Statistic

    # mostly lies, but this is for "coolness" not "factualness"
    report = {
        "users": {
            "new_0": _("We've had no new users today."),
            "new<10": _("We've had a few new users today!"),
            "new>=10": _("I think we've had a mention on a podcast - we've had a lot of new users today."),
            "new>users/2": _("It's still early days - most of our users joined in the last 24 hours."),
            "users>0": _("We have more users than people who've left the solar system."),
            "users>12": _("We have more users than people who've walked on the moon."),
            "users>24": _("We have more users than people who've travelled to the moon."),
            "users>600": _("We have more users than people who've flown in space!"),
            },
        "inboxes": {
            "max==0": _("No one has created any Inboxes yet."),
            "min==max,!=0": _("Only one user has created an Inbox."),
            "zscore_max>10": _("It looks like most of our Inboxes belong to one user."),
            "stddev<10": _("Users tend to have a similar number of Inboxes."),
            "stddev>=10": _("Some users have quite a few more Inboxes than others."),
            },
        "emails": {
            "max==0": _("We haven't received any emails yet, which is a bit odd."),
            "min==max,!=0": _("Only one Inbox has received any emails."),
            "zscore_max>10": _("It looks like most emails are going to one Inbox!"),
            "zscore_max>20": _("I think someone has signed themselves up to every mailing list they could find."),
            "zscore_min<1": _("Most Inboxes on this server are empty."),
            "stddev<10": _("We keep things fair and have an equal number of emails in each Inbox. Some are more equal than others."),
            },
        }

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()

        try:
            return queryset.latest("date")
        except models.Statistic.DoesNotExist:
            return None
