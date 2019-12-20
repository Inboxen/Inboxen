##
#    Copyright (C) 2014, 2018 Jessica Tallon & Matt Molyneaux
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

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext as _

from inboxen.account.utils import login_ratelimit


class CaseInsensitiveMixin:
    def authenticate(self, request, username=None, password=None, **kwargs):
        # we're also case insensitive
        user_model = get_user_model()
        username_field = user_model.USERNAME_FIELD
        if username is None:
            username = kwargs.get(username_field)
        try:
            user = user_model.objects.get(**{"{0}__iexact".format(username_field): username})
            if user.check_password(password):
                return user
        except user_model.DoesNotExist:
            # do like the default backend does, slow down return on non-existence
            user_model().set_password(password)


class RateLimitMixin:
    def authenticate(self, request, *args, **kwargs):
        if login_ratelimit.counter_full(request):
            messages.warning(request, _("Too many login attempts, further login attempts will be ignored."))
            return

        user = super().authenticate(request, *args, **kwargs)

        if user is None:
            login_ratelimit.counter_increase(request)
        return user


class RateLimitWithSettings(RateLimitMixin, CaseInsensitiveMixin, ModelBackend):
    pass
