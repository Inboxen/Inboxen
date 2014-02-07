##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen.
#
#    Inboxen front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

import smtplib

from django.core.management.base import BaseCommand, CommandError

from inboxen.models import Inbox

## Waiting on Inboxen/router#22
SERVER = {'host': 'localhost', 'port': 8823}

class Command(BaseCommand):
    args = "<path to mail box> [<inbox>]"
    help = "Feed emails into the system via SMTP, optionally specifying an inbox"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._server = None

    def handle(self, *args, **options):
        # look at the arg
        if not args:
            self.stdout.write(self.help)
            return
        elif len(args) == 2:
            try:
                Inbox.objects.from_string(email=arg[1])
                self.inbox = arg[1]
            except Inbox.DoesNotExist:
                raise CommandError("Address malformed")
        else:
            self.inbox = None

        self.mbox = mailbox.mbox(args[0])

        self.mbox.lock()
        self._iterate()
        self.mbox.unlock()

    def _iterate(self):
        for key in self.mbox.keys():
            server = self._get_server()
            message = self.mbox.get(key)
            if self.inbox:
               message['To'] = self.inbox
            server.sendmail(self._get_address(message['From']), self._get_address(message['To']), message)
            self.mbox.discard(key)

    def _get_address(self, address):
        # i have this awful feeling that i'm reimplementing something in the stdlib
        start = address.find("<")
        end = address.rfind(">")

        if start * end < 0:
            raise CommandError("One of your messages has malformed address, aborting")
        elif start < 0:
            address = "<{0}>".format(address)
        else:
            address = address[start:end]

        return address

    def _get_server(self):
        try:
            self._server.rset()
        except (smtplib.SMTPException, AttributeError):
            self._server = smtplib.SMTP(SERVER["host"], SERVER["port"])
            self._server.helo()

        return self._server
