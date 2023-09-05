##
#    Copyright (C) 2020 Jessica Tallon & Matthew Molyneaux
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

from django.db import models

from inboxen.monitor.managers import CheckQuerySet


class CheckItem(models.Model):
    SALMON = 0
    CELERY = 1

    CHECKS = (
        (SALMON, "Salmon"),
        (CELERY, "Celery"),
    )
    when = models.DateTimeField(auto_now_add=True)
    check_type = models.SmallIntegerField(choices=CHECKS)
    good = models.BooleanField(default=True)

    objects = CheckQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["check_type", "when"])]
