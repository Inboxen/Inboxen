##
#    Copyright (C) 2018 Jessica Tallon & Matt Molyneaux
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

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from inboxen.models import Domain


class Command(BaseCommand):
    help = "Create a domain"

    def add_arguments(self, parser):
        parser.add_argument("domain", help="domain to be created")

    def handle(self, **options):
        domain = options["domain"]
        try:
            Domain.objects.create(domain=domain)
        except IntegrityError:
            raise CommandError("Domain already exists.")
        else:
            self.stdout.write("%s created!\n" % domain)
            self.stdout.flush()
