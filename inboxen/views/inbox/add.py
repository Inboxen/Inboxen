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

from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages

from braces.views import LoginRequiredMixin

from inboxen.models import Inbox

from inboxen import forms

__all__ = ["InboxAddView"]


class InboxAddView(LoginRequiredMixin, generic.CreateView):
    success_url = reverse_lazy('user-home')
    form_class = forms.InboxAddForm
    model = Inbox
    template_name = "inboxen/inbox/add.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            if request.user.userprofile.available_inboxes() <= 0:
                messages.error(request, _("You have too many Inboxes."))
                return HttpResponseRedirect(self.success_url)
        except AttributeError:
            pass

        return super(InboxAddView, self).dispatch(request=request, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(InboxAddView, self).get_form_kwargs(*args, **kwargs)
        kwargs.setdefault("request", self.request)
        return kwargs
