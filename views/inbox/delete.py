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
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy

from inboxen import models
from queue.delete.tasks import delete_inbox
from website import forms
from website.views import base

class InboxDeletionView(base.CommonContextMixin, base.LoginRequiredMixin, generic.DeleteView):
    model = models.Inbox
    success_url = reverse_lazy('user-home')
    title = "Delete Inbox"
    template_name = "inbox/delete.html"

    def get_object(self, *args, **kwargs):
        return self.request.user.inbox_set.get(
            inbox=self.kwargs["inbox"],
            domain__domain=self.kwargs["domain"]
            )

    def delete(self, request,*args, **kawrgs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.deleted = True
        self.object.save()

        delete_inbox.delay(self.object.id, request.user.id)

        return HttpResponseRedirect(success_url)
