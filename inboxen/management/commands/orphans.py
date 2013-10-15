from celery import group
from django.core.management.base import BaseCommand

from inboxen.models import Attachment, Header
from queue.delete.tasks import delete_email_item

class Command(BaseCommand):
    args = "[--clean]"
    help = "List orphaned Header and Attachment objects"

    def handle(self, *args, **options):
        if "clean" in args:
            headers = Header.objects.only('id').filter(email=None)
            attachments = Attachment.objects.only('id').filter(email=None)

            self.stdout.write("Sending off cleanup tasks...")

            if len(headers) > 0:
                headers = group([delete_email_item.s('header', header.id) for header in headers])
                headers = headers.apply_async()
                self.stdout.write("Header task id: %s" % headers.id)
            if len(attachments) > 0:
                attachments = group([delete_email_item.s('attachment', attachment.id) for attachment in attachments])
                attachments = attachments.apply_async()
                self.stdout.write("Attachment task id: %s" % attachments.id)

        else:
            self.stdout.write("Fetching data...")

            headers = Header.objects.filter(email=None).count()
            self.stdout.write("Orphaned headers: %s" % headers)

            attachments = Attachment.objects.filter(email=None).count()
            self.stdout.write("Orphaned attachments: %s" % attachments)
