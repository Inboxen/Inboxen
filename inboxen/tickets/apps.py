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
from django.db.models.signals import post_save

from inboxen.tickets import signals


class TicketConfig(AppConfig):
    name = "inboxen.tickets"
    label = "tickets"
    verbose_name = "Inboxen Tickets"

    def ready(self):
        Question = self.get_model("Question")
        post_save.connect(signals.new_question, sender=Question, dispatch_uid="question notifier")
