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

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q

from termsofservice import models

class StaffProfileAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs["initial"] = request.user.id
            kwargs["queryset"] = get_user_model().objects.filter(Q(is_staff=True)|Q(is_superuser=True))

        return super(StaffProfileAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(models.StaffProfile, StaffProfileAdmin)
