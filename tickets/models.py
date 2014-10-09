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

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Question(models.Model):
    # status contants
    NEW = 0
    IN_PROGRESS = 1
    NEED_INFO = 2
    RESOLVED = 3

    # status choices
    STATUS_CHOICES = (
        (NEW, _("New")),
        (IN_PROGRESS, _("In progress")),
        (NEED_INFO, _("Need more info")),
        (RESOLVED, _("Resolved")),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    subject = models.CharField(max_length=512)
    body = models.TextField()

    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=NEW, db_index=True)

    @property
    def last_activity(self):
        """Return the lastest activity of this Question

        Expects the attribute "last_response_date" to be annotated
        """
        if not self.last_response_date is None and self.last_response_date > self.last_modified:
            return self.last_response_date
        else:
            return self.last_modified

    class Meta:
        ordering = ["-date"]

class Response(models.Model):
    question = models.ForeignKey(Question)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(auto_now_add=True)

    body = models.TextField()

    class Meta:
        ordering = ["date"]
