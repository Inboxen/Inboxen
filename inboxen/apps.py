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


class InboxenConfig(AppConfig):
    name = "inboxen"
    verbose_name = "Inboxen Core"

    def ready(self):
        from django.contrib.auth.signals import user_logged_in, user_logged_out

        from inboxen import checks  # noqa
        from inboxen import signals

        # Unregister update_last_login handler
        assert user_logged_in.disconnect(dispatch_uid='update_last_login'), "Last login not disconnected"

        user_logged_out.connect(signals.logout_message, dispatch_uid='inboxen_logout_message')
