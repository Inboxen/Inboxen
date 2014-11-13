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

from urllib import urlencode

from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect

from inboxen import models


class RequestAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("requester", "date", "amount", "succeeded")
    readonly_fields = ("requester", "amount", "date", "date_decided")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'authorizer':
            kwargs["initial"] = request.user.id
            kwargs["queryset"] = get_user_model().objects.filter(Q(is_staff=True) | Q(is_superuser=True))

        return super(RequestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class DomainAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("domain", "owner", "enabled")

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + ("domain", )
        return self.readonly_fields


class UserAdmin(OriginalUserAdmin):
    actions = None

    def user_change_password(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super(UserAdmin, self).user_change_password(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(is_staff=True) | Q(is_superuser=True))

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return self.readonly_fields + (
            "date_joined", "last_login", "groups", "is_active", "is_staff",
            "is_superuser", "password", "user_permissions", "username",
        )


def login(self, request, extra_context=None):
    if REDIRECT_FIELD_NAME in request.GET:
        url = request.GET[REDIRECT_FIELD_NAME]
    else:
        url = request.get_full_path()
    return redirect('%s?%s' % (
        reverse('user-login'),
        urlencode({REDIRECT_FIELD_NAME: url})
    ))

admin.AdminSite.login = login
admin.site.register(models.Request, RequestAdmin)
admin.site.register(models.Domain, DomainAdmin)

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
