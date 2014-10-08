##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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

from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views import generic

from website import forms
from website.views.base import CommonContextMixin

class UserRegistrationView(CommonContextMixin, generic.CreateView):
    form_class = forms.PlaceHolderUserCreationForm
    success_url = reverse_lazy('user-success')
    headline = _("Register")
    template_name = "user/register/register.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse_lazy('user-home'))

        if not settings.ENABLE_REGISTRATION:
            # I think this should be a 403 
            return HttpResponseRedirect(reverse_lazy("index"))

        return super(UserRegistrationView, self).dispatch(request=request, *args, **kwargs)

