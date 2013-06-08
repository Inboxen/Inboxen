##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen front-end.
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
#    along with Inboxen front-end.  If not, see <http://www.gnu.org/licenses/>.
##

from django.core.management.base import BaseCommand, CommandError

from inboxen.models import User, Email, Alias, Tag
from queue.tasks import delete_alias

from salmon.commands import start_command, stop_command, status_command

class Command(BaseCommand):
    args = "<start/stop/status>"
    help = "Start and stop Salmon router"

    # this needs moving somewhere else
    salmon_dir = './router/'
    # these need to be ordered from smtp in to database out
    salmon_options = [
            {'chdir': salmon_dir, 'pid': salmon_dir + 'run/in.pid', 'boot': 'config.boot'},
            {'chdir': salmon_dir, 'pid': salmon_dir + 'run/out.pid', 'boot': 'config.accepted'}
            ]

    def handle(self, *args, **options):
        if not args:
            self.stdout.write(self.help)
            return
        elif not self.can_import_setting:
            raise CommandError("I can't work under these conditions! Where is settings.py?!")

        if args[0] == "start":
            self.salmon_start()
        elif args[0] == "stop":
            self.salmon_stop()
        elif args[0] == "status":
            self.salmon_status()
        else:
            raise CommandError("No such command, %s" % args[0])

    def salmon_start(self):
        for handler in salmon_options:
            start_command(**handler)

    def salmon_stop(self):
        for handler in salmon_options:
            stop_command(pid=handler['pid'])

    def salmon_status(self):
        for handler in salmon_options:
            status_command(pid=handler['pid'])
