##
#    Copyright (C) 2020 Jessica Tallon & Matt Molyneaux
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

from django.core.management.base import BaseCommand

from inboxen.models import Inbox


class Command(BaseCommand):
    help = "Print a list of disowned Inboxes. For use with Internet facing mail servers."

    def add_arguments(self, parser):
        parser.add_argument("--postfix", action="store_true", help="Format output for use with Postfix")

    def handle(self, **options):
        tmpl = "{}\n"
        if options["postfix"]:
            tmpl = "{}\t501 5.1.1 Address no longer in use\n"

        for inbox in Inbox.objects.disowned().order_by("id"):
            self.stdout.write(tmpl.format(str(inbox)))

        self.stdout.flush()
