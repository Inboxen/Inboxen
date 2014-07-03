
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

from django.utils.translation import ugettext as _

from two_factor.views import core
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm

from website.forms import PlaceHolderAuthenticationForm
from website.views.base import CommonContextMixin

__all__ = ["LoginView"]

class LoginView(CommonContextMixin, core.LoginView):
    template_name = "user/login.html"
    headline = _("Login")

    form_list = (
        ('auth', PlaceHolderAuthenticationForm),
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
        )

    def get_form_kwargs(self, step):
        if step == "auth":
            return {"request": self.request}
        else:
            return super(LoginView, self).get_form_kwargs(step)
