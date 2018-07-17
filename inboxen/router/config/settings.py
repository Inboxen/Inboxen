import os

from salmon.server import SMTPReceiver, LMTPReceiver

os.environ['DJANGO_SETTINGS_MODULE'] = 'inboxen.settings'

from django.conf import settings  # noqa
import django  # noqa
django.setup()

# where to listen for incoming messages
if settings.SALMON_SERVER["type"] == "lmtp":
    receiver = LMTPReceiver(socket=settings.SALMON_SERVER["path"])
elif settings.SALMON_SERVER["type"] == "smtp":
    receiver = SMTPReceiver(settings.SALMON_SERVER['host'],
                            settings.SALMON_SERVER['port'])
