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
