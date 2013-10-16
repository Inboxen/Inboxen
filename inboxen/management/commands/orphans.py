from celery import group
from django.core.management.base import BaseCommand

from inboxen.models import Attachment, Header
from queue.delete.tasks import major_cleanup_items

class Command(BaseCommand):
    args = "[clean]"
    help = "List orphaned Header and Attachment objects"

    def handle(self, *args, **options):
        if "clean" in args:
            headers = Header.objects.only('id').filter(email=None).exists()
            attachments = Attachment.objects.only('id').filter(email=None.exists())

            self.stdout.write("Sending off cleanup tasks...")

            if headers:
                header_task = major_cleanup_items.si('header', filter_kwargs={'email':None})
                header_task.apply_async()
            if attachments:
                attachment_task = major_cleanup_items.si('attachment', filter_kwargs={'email':None})
                attachment_task.apply_async()

        else:
            self.stdout.write("Fetching data...")

            headers = Header.objects.filter(email=None).count()
            self.stdout.write("Orphaned headers: %s" % headers)

            attachments = Attachment.objects.filter(email=None).count()
            self.stdout.write("Orphaned attachments: %s" % attachments)
