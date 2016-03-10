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

from django.apps import AppConfig
from django.db.models.signals import pre_save


class InboxenConfig(AppConfig):
    name = "inboxen"
    verbose_name = "Inboxen Core"

    def ready(self):
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in, user_logged_out
        from watson import search as watson_search

        from inboxen import checks, search, signals

        Inbox = self.get_model("Inbox")
        Email = self.get_model("Email")
        Request = self.get_model("Request")

        # Unregister update_last_login handler
        user_logged_in.disconnect(update_last_login)

        # Search
        watson_search.register(Email, search.EmailSearchAdapter)
        watson_search.register(Inbox, search.InboxSearchAdapter)

        pre_save.connect(signals.decided_checker, sender=Request, dispatch_uid="request_decided_checker")
        user_logged_out.connect(signals.logout_message)
