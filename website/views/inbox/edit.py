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

from django.views import generic
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy

from website import forms
from website.views import base
from inboxen.models import Inbox

__all__ = ["InboxEditView", "InboxRestoreView"]

class InboxEditView(base.CommonContextMixin, base.LoginRequiredMixin, generic.UpdateView):
    form_class = forms.InboxEditForm
    template_name = "inbox/edit.html"
    success_url = reverse_lazy('user-home')

    def get_headline(self):
        return _("{inbox}@{domain} Options").format(inbox=self.kwargs["inbox"], domain=self.kwargs["domain"])

    def get_object(self, *args, **kwargs):
        inbox = self.request.user.inbox_set.select_related("domain")
        return inbox.get(inbox=self.kwargs["inbox"], domain__domain=self.kwargs["domain"], flags=~Inbox.flags.deleted)


class InboxRestoreView(InboxEditView):
    form_class = forms.InboxRestoreForm
    template_name = "inbox/restore.html"

    def get_object(self, *args, **kwargs):
        inbox = self.request.user.inbox_set.select_related("domain")
        return inbox.get(inbox=self.kwargs["inbox"], domain__domain=self.kwargs["domain"], flags=Inbox.flags.deleted)
