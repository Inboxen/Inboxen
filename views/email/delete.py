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

from inboxen import models
from website import forms
from website.views.base import CommonContextMixin

class EmailDeletionView(generic.DeleteView):
    model = models.Inbox
    success_url = "/user/home/"
    title = "Delete Inbox"
    template_name = "email/delete/confirm.html"

    def get_object(self, *args, **kwargs):
        inbox, domain = self.kwargs["email"].split("@", 1)
        return self.request.user.inbox_set.get(
            inbox=inbox,
            domain__domain=domain
        )
