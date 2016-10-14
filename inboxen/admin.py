##
#    Copyright (C) 2014, 2016 Jessica Tallon & Matt Molyneaux
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

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy

from inboxen import models


class DomainAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("domain", "owner", "enabled")

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + ("domain", )
        return self.readonly_fields


class RequestAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("requester", "date", "amount", "succeeded")
    readonly_fields = ("requester", "amount", "date", "date_decided")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'authorizer':
            kwargs["initial"] = request.user.id
            kwargs["queryset"] = get_user_model().objects.filter(Q(is_staff=True) | Q(is_superuser=True))

        return super(RequestAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class InboxenAdmin(admin.AdminSite):
    site_header = ugettext_lazy("{site_name} Admin").format(site_name=settings.SITE_NAME)
    site_title = ugettext_lazy("{site_name} Admin").format(site_name=settings.SITE_NAME)
    index_title = ugettext_lazy("Instance Administration")

    def has_permission(self, request):
        has_perm = super(InboxenAdmin, self).has_permission(request)
        if has_perm and not request.user.is_verified():
            raise PermissionDenied("Admins must have Two Factor authentication enabled")
        return has_perm

    def login(self, request, extra_context=None):
        if REDIRECT_FIELD_NAME in request.GET:
            url = request.GET[REDIRECT_FIELD_NAME]
        else:
            url = request.get_full_path()
        return redirect('%s?%s' % (
            reverse('user-login'),
            urlencode({REDIRECT_FIELD_NAME: url})
        ))

    def logout(self, *args, **kwargs):
        return redirect(reverse("user-logout"))

    def password_change(self, *args, **kwargs):
        return redirect(reverse("user-password"))

    def password_change_done(self, *args, **kwargs):
        return redirect(reverse('admin:index', current_app=self.name))

    def admin_view(self, view, cacheable=False):
        view = super(InboxenAdmin, self).admin_view(view, cacheable)
        return csp_replace(SCRIPT_SRC=("'self'", "'unsafe-inline'"))(view)


site = InboxenAdmin()
site.register(models.Domain, DomainAdmin)
site.register(models.Request, RequestAdmin)
