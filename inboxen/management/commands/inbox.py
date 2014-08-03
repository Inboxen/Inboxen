##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from inboxen.models import Inbox
from queue.delete.tasks import delete_inbox

class Command(BaseCommand):
    args = "<info/tags/delete/resurrect> <inbox> [<tag1>, <tag2>, etc...]"
    help = "Management of everything relating to inboxes and their data"

    def handle(self, *args, **options):
        if not args:
            self.stdout.write(self.help)
            return
        
        if len(args) >= 2 and args[0] != "list":
            inbox, domain = args[1].split("@", 1)
            try:
                inbox = Inbox.objects.get(inbox=inbox, domain__domain=domain)
            except Inbox.DoesNotExist:
                raise CommandError("Can't find inbox %s" % args[1])
        else:
            if args[0] == "list" and len(args) <= 1:
                written = False
                for inbox in Inbox.objects.all():
                    written = True
                    self.stdout.write(str(inbox))
                if not written:
                    self.stdout.write("Can't find any inboxes")
            elif args[0] == "list":
                written = False
                self.stdout.write("Searching for %s (could take a while):" % args[1])
                term = args[1].lower()
                # args[1] is a search term
                for user in get_user_model().objects.all():
                    if term in user.username.lower():
                        for inbox in Inbox.objects.filter(user=user):
                            written = True
                            self.stdout.write(str(inbox))
                for inbox in Inbox.objects.all():
                    if term in inbox.inbox.lower():
                        written = True
                        self.stdout.write(str(inbox))
                    elif term in inbox.domain.domain.lower():
                        written = True
                        self.stdout.write(str(inbox))
                if not written:
                    self.stdout.write("No inboxes found")
            else:
                raise CommandError("You need to enter an inbox")
            return
        # look for commands
        if args[0] == "tags" and len(args) <= 2:
            # wants a list of tags
            tags = []
            for tag in Tag.objects.filter(inbox=inbox):
                tags.append(str(tag))
            self.stdout.write("%s: %s" % (inbox, ", ".join(tags)))
        
        elif args[0] == "tags":
            inbox.tags = ", ".join(args[2:])
            inbox.save()
            self.stdout.write("Tags have been saved for %s" % inbox)

        elif args[0] == "delete":
            inbox.flags.deleted = True
            inbox.save()
            delete_inbox.delay(inbox)
            self.stdout.write("%s has been queued for deletion" % inbox)
        elif args[0] == "resurrect":
            if inbox.flags.deleted:
                inbox.flags.deleted = False
                inbox.save()
                self.stdout.write("%s has been resurrected" % inbox)
            else:
                raise CommandError("%s has not been deleted" % inbox)
        elif args[0] == "info":
            self.stdout.write("This information could be potentially sensative, please do not share it with anyone.")
            self.stdout.write("[%s] -" % inbox)
            self.stdout.write("User: %s" % inbox.user.username)
            self.stdout.write("Created: %s" % inbox.created)
            tags = inbox.tags
            if tags:
                self.stdout.write("Tags: %s" % ", ".join(tags))
            else:
                self.stdout.write("Tags: No tags")
            email_count = inbox.email_set.count()
            self.stdout.write("Emails: %s" % email_count)
        else:
            raise CommandError("%s not found" % args[0])
