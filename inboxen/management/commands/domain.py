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

from inboxen.models import Domain

class Command(BaseCommand):
    args = "<add/list/re(move)> <domain>"
    help = "Allows management of domains"

    def handle(self, *args, **options):
        # look at the arg
        if not args:
            self.stdout.write(self.help)
            return

        # look for commands
        if "add" == args[0]:
            # adding?
            if len(args) <= 1:
                raise CommandError("You need to give a domain")
            d = Domain(
                domain=args[1]
            )
            d.save()
            self.stdout.write("%s has been added" % d)
        elif "list" == args[0]:
            domains = Domain.objects.all().iterator()
            for domain in domains:
                self.stdout.write("%s" % domain)
            return
        elif args[0] in ["rm", "remove"]:
            if len(args) <= 1:
                raise CommandError("You need to give a domain to remove")
            
            try:
                d = Domain.objects.get(domain=args[1])
                d.delete()
                self.stdout.write("%s has been removed" % d)
            except Domain.DoesNotExist:
                raise CommandError("Can't find domain '%s'" % args[1])
        else:
            raise CommandError("Can't find command %s" % args[0])
