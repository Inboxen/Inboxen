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
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views import generic

from inboxen.account import forms, utils


class UserRegistrationView(generic.CreateView):
    form_class = forms.PlaceHolderUserCreationForm
    success_url = reverse_lazy('user-success')
    template_name = "account/register/register.html"

    def dispatch(self, request, *args, **kwargs):
        if not settings.ENABLE_REGISTRATION:
            # I think this should be a 403
            return HttpResponseRedirect(reverse_lazy("index"))

        return super(UserRegistrationView, self).dispatch(request=request, *args, **kwargs)

    def post(self, *args, **kwargs):
        if utils.register_counter_full(self.request):
            messages.warning(self.request, _("Too many signups, further attempts will be ignored."))
            return HttpResponseRedirect(reverse_lazy("user-registration"))

        return super(UserRegistrationView, self).post(*args, **kwargs)

    def form_valid(self, form):
        utils.register_counter_increase(self.request)
        return super(UserRegistrationView, self).form_valid(form)
