##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
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

from django.views import generic
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy

from website import forms
from website.views import base
from inboxen.models import Inbox

__all__ = ["FormInboxEditView"]


class FormInboxEditView(base.LoginRequiredMixin, generic.UpdateView):
    form_class = forms.InboxEditForm
    template_name = "forms/inbox/edit.html"
    success_url = reverse_lazy('user-home')

    def get_form_kwargs(self):
        kwargs = super(FormInboxEditView, self).get_form_kwargs()
        kwargs.setdefault("request", self.request)
        return kwargs

    def get_object(self, *args, **kwargs):
        inbox = self.request.user.inbox_set.select_related("domain")
        return inbox.get(inbox=self.kwargs["inbox"], domain__domain=self.kwargs["domain"], flags=~Inbox.flags.deleted)
