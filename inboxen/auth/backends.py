##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen.
#
#    Inboxen front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django.contrib.auth.backends import ModelBackend

from inboxen.models import User, TOTPAuth

import onetimepass as otp

class TOTPBackend(ModelBackend):
    """
    Replaces django.contrib.auth.backends.ModelBackend and allows TOTP
    tokens
    """

    def authenticate(self, username=None, password=None, token=None):
        user = super(TOTPBackend, self).authenticate(username, password)
        try:
            secret = TOTPAuth.objects.get(user=user)
        except TOTPAuth.DoesNotExist:
            if token == None:
                return user
            else:
                return None

        is_valid = otp.valid_totp(token=token, secret=secret)

        if is_valid:
            return user
