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

import sys
from subprocess import check_output, CalledProcessError

from django.core.management.base import BaseCommand, CommandError
from inboxen.models import User, Email, Alias, Tag
from queue.tasks import delete_alias

class Command(BaseCommand):
    args = "<start/stop/status>"
    help = "Start and stop Salmon router"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # these need to be ordered from smtp in to database out
        self.salmon_options = [
                {'pid': 'run/in.pid', 'boot': 'config.boot'},
                {'pid': 'run/out.pid', 'boot': 'config.accepted'}
                ]

    def handle(self, *args, **options):
        if not args:
            self.stdout.write(self.help)
            return
        elif not self.can_import_settings:
            raise CommandError("I can't work under these conditions! Where is settings.py?!")

        try:
            if args[0] == "start":
                output = self.salmon_start()
            elif args[0] == "stop":
                output = self.salmon_stop()
            elif args[0] == "status":
                output = self.salmon_status()
            else:
                raise CommandError("No such command, %s" % args[0])
        except OSError:
            raise Exception("OSError from subprocess, salmon is probably not in your path.")

        self.stdout.write("".join(output))

    def salmon_start(self):
        name = "Starting Salmon handler: %s\n"
        output = []
        for handler in self.salmon_options:
            try:
                check_output(['salmon', 'start', '-pid', handler['pid'], '-boot', handler['boot']], cwd='router')
                output.append(name % handler['boot'][7:])
            except CalledProcessError as error:
                output.append("Exit code %d: %s" % (error.returncode, error.output))

        return output

    def salmon_stop(self):
        output = []
        for handler in self.salmon_options:
            try:
                output.append(check_output(['salmon', 'stop', '-pid', handler['pid']], cwd='router'))
            except CalledProcessError as error:
                output.append("Exit code %d: %s" % (error.returncode, error.output))

        return output

    def salmon_status(self):
        output = []
        for handler in self.salmon_options:
            try:
                output.append(check_output(['salmon', 'status', '-pid', handler['pid']], cwd='router'))
            except CalledProcessError as error:
                output.append("Exit code %d: %s" % (error.returncode, error.output))

        return output
