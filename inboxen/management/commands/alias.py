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
from website.tasks import delete_alias

class Command(BaseCommand):
    args = "<info/tags/delete/resurrect> <alias> [<tag1>, <tag2>, etc...]"
    help = "Management of everything relating to aliases and their data"

    def handle(self, *args, **options):
        if not args:
            self.stdout.write(self.help)
        
        if len(args) >= 2 and args[0] != "list":
            alias, domain = args[1].split("@", 1)
            try:
                alias = Alias.objects.get(alias=alias, domain__domain=domain)
            except Alias.DoesNotExist:
                raise CommandError("Can't find alias %s" % args[1])
        else:
            if args[0] == "list" and len(args) <= 1:
                written = False
                for alias in Alias.objects.all():
                    written = True
                    self.stdout.write(str(alias))
                if not written:
                    self.stdout.write("Can't find any aliases")
            elif args[0] == "list":
                written = False
                self.stdout.write("Searching for %s (could take a while):" % args[1])
                term = args[1].lower()
                # args[1] is a search term
                for user in User.objects.all():
                    if term in user.username.lower():
                        for alias in Alias.objects.filter(user=user):
                            written = True
                            self.stdout.write(str(alias))
                for alias in Alias.objects.all():
                    if term in alias.alias.lower():
                        written = True
                        self.stdout.write(str(alias))
                    elif term in alias.domain.domain.lower():
                        written = True
                        self.stdout.write(str(alias))
                if not written:
                    self.stdout.write("No aliases found")
            else:
                raise CommandError("You need to enter an alias")
            return
        # look for commands
        if "tags" == args[0] and len(args) <= 2:
            # wants a list of tags
            tags = []
            for tag in Tag.objects.filter(alias=alias):
                tags.append(str(tag))
            self.stdout.write("%s: %s" % (alias, ", ".join(tags)))
        
        elif "tags" == args[0]:
            if "--delete-current" in args:
                Tags.objects.filter(alias=alias).delete()

            # wants to set them.
            tags = [tag for tag in args[2:]]

            for i, tag in enumerate(tags):
                tags[i] = Tag(tag=tag, alias=alias)
                tags[i].save()

            self.stdout.write("Tags have been saved for %s" % alias)

        elif "delete" == args[0]:
            alias.deleted = True
            alias.save()
            delete_alias.delay(alias)
            self.stdout.write("%s has been queued for deletion" % alias)
        elif "resurrect" == args[0]:
            if alias.deleted:
                alias.deleted = False
                alias.save()
                self.stdout.write("%s has been resurrected" % alias)
            else:
                raise CommandError("%s has not been deleted" % alias)
        elif "info" == args[0]:
            self.stdout.write("This information could be potentially sensative, please do not share it with anyone.")
            self.stdout.write("[%s] -" % alias)
            self.stdout.write("User: %s" % alias.user.username)
            self.stdout.write("Created: %s" % alias.created)
            tags = Tag.objects.filter(alias=alias)
            if tags:
                self.stdout.write("Tags: %s" % ", ".join(tags))
            else:
                self.stdout.write("Tags: No tags")
            email_count = Email.objects.filter(inbox=alias).count()
            self.stdout.write("Emails: %s" % email_count)
        else:
            raise CommandError("%s not found" % args[0])
