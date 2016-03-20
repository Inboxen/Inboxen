##
#    Copyright (C) 2013, 2015 Jessica Tallon & Matt Molyneaux
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

from email.utils import parseaddr
import mailbox
import os
import smtplib

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from progress import bar

from inboxen.models import Inbox


class Command(BaseCommand):
    help = "Feed emails into the system via SMTP, optionally specifying an inbox"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._server = None

    def add_arguments(self, parser):
        parser.add_argument("mailbox", help="path to mailbox")
        parser.add_argument("--inbox")

    def handle(self, **options):
        # look at the arg
        if options["inbox"]:
            try:
                Inbox.objects.from_string(email=options["inbox"])
                self.inbox = options["inbox"]
            except Inbox.DoesNotExist:
                raise CommandError("Address malformed")
        else:
            self.inbox = None

        if not os.path.exists(options["mailbox"]):
            raise CommandError("No such path: %s" % options["mailbox"])

        self.mbox = mailbox.mbox(options["mailbox"])
        self.msg_count = len(self.mbox)

        if self.msg_count == 0:
            raise CommandError("Your mbox is empty!")

        self.mbox.lock()
        try:
            self._iterate()
        finally:
            self.mbox.close()

        self.stdout.write("\nDone!")
        self.stdout.flush()

    def _iterate(self):
        for key in bar.ShadyBar("Feeding").iter(self.mbox.keys()):
            server = self._get_server()
            message = self.mbox.get(key)

            if self.inbox:
                try:
                    message.replace_header("To", str(self.inbox))
                except KeyError:
                    message["To"] = str(self.inbox)

            server.sendmail(self._get_address(message['From']), self._get_address(message['To']), message.as_string())
            self.mbox.remove(key)

    def _get_address(self, address):
        name, email = parseaddr(address)

        if email == "":
            raise CommandError("Address malformed, aborting: %s" % address)

        return "<{0}>".format(email)

    def _get_server(self):
        try:
            self._server.rset()
        except (smtplib.SMTPException, AttributeError):
            if settings.SALMON_SERVER["type"] == "smtp":
                self._server = smtplib.SMTP(settings.SALMON_SERVER["host"], settings.SALMON_SERVER["port"])
            elif settings.SALMON_SERVER["type"] == "lmtp":
                self._server = smtplib.LMTP(settings.SALMON_SERVER["path"])
            self._server.ehlo_or_helo_if_needed()  # will "lhlo" for lmtp

        return self._server
