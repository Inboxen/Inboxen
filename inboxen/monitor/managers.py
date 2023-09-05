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

from datetime import timedelta

from django.db.models.query import QuerySet
from django.utils import timezone


class CheckQuerySet(QuerySet):
    def check_ok(self, check, days=1):
        return self.filter(good=True, check_type=check, when__gte=timezone.now() - timedelta(days=days)).exists()

    def create_check(self, check):
        if check not in [c[0] for c in self.model.CHECKS]:
            raise ValueError("Not a valid check")
        return self.create(good=True, check_type=check)
