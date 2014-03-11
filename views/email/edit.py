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

from website import forms
from inboxen.models import Tag

class EmailEditView(generic.UpdateView):
    form_class = forms.InboxEditForm
    template_name = "email/edit.html"
    title = "Edit inbox"
    success_url = "/user/home/"

    def get_object(self, *args, **kwargs):
        inbox = self.request.user.inbox_set.select_related("domain")
        return inbox.filter(inbox=self.kwargs["inbox"], domain__domain=self.kwargs["domain"], deleted=False)
