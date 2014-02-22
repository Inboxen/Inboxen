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
from django.utils import decorators
from django.contrib.auth import decorators as auth_decorators
from django.views import generic

from inboxen.helper.paginator import page as page_paginator
from inboxen.models import Inbox, Tag, Email
from website.views.base import CommonContextMixin

class UserHomeView(CommonContextMixin, generic.ListView):
    """ The user's home which lists the inboxes """
    allow_empty = True
    paginate_by = 50
    template_name = "user/home.html"
    title = "Home"

    @decorators.method_decorator(auth_decorators.login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserHomeView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = self.request.user.inbox_set.all()
        queryset = queryset.filter(deleted=False)
        return queryset.order_by("-created")

    def get_flags(self):
        return ~(Email.flags.deleted | Email.flags.read)

    def process_messages(self, inboxes):
        """ Get tags and message counts """
        flags = self.get_flags()
        self.unread_email_count = 0
        for inbox in inboxes:
            # Add the tags for the email to enable inbox.tags to produce tag1, tag2...
            try:
                tags = inbox.tag_set.all()
                inbox.tags = ", ".join([tag.tag for tag in tags])
            except Tag.DoesNotExist:
                inbox.tags = ""

            # Add the number of emails with given flags
            inbox.email_count = inbox.email_set.filter(flags=flags).count()
            self.unread_email_count += inbox.email_count

        return inboxes

    def get_context_data(self, *args, **kwargs):
        self.object_list = self.process_messages(self.object_list)
        context = super(UserHomeView, self).get_context_data(*args, **kwargs)
        context.setdefault("unread_email_count", self.unread_email_count)
        context.setdefault("user")
        context.setdefault("pages", page_paginator(context['page_obj']))
        return context
