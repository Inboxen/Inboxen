##
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django.views import generic
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod

class CommonContextMixin(object):
    """Common items that our templates need, including title"""
    title = ""

    def get_context_data(self, *args, **kwargs):
        if self.title == "":
            raise AttributeError("Blank titles not supported")

        context = super(CommonContextMixin, self).get_context_data(*args, **kwargs)
        context.setdefault("page", _(self.title))
        context.setdefault("request", self.request)
        return context

class TemplateView(CommonContextMixin, generic.TemplateView):
    """ django's templateview with some commonly needed context data """
    pass

class LoginRequiredMixin(object):
    @classonlymethod
    def as_view(cls, **initkwargs):
        return login_required(super(LoginRequiredMixin, cls).as_view(**initkwargs))
