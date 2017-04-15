##
#    Copyright (C) 2013, 2014, 2015, 2016, 2017 Jessica Tallon & Matt Molyneaux
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

from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from inboxen import models


class RequestPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False


class DomainAdmin(ModelAdmin):
    model = models.Domain
    menu_icon = 'snippet'
    list_display = ("domain", "owner", "enabled")


class RequestAdmin(ModelAdmin):
    model = models.Request
    menu_icon = 'arrow-up-big'
    list_display = ("requester", "date", "amount", "succeeded")
    permission_helper_class = RequestPermissionHelper


modeladmin_register(DomainAdmin)
modeladmin_register(RequestAdmin)
