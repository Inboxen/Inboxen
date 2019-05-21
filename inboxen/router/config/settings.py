import os

from django.conf import settings  # noqa
from salmon.server import LMTPReceiver, SMTPReceiver
import django  # noqa

os.environ['DJANGO_SETTINGS_MODULE'] = 'inboxen.settings'

django.setup()

# where to listen for incoming messages
if settings.SALMON_SERVER["type"] == "lmtp":
    receiver = LMTPReceiver(socket=settings.SALMON_SERVER["path"])
elif settings.SALMON_SERVER["type"] == "smtp":
    receiver = SMTPReceiver(settings.SALMON_SERVER['host'],
                            settings.SALMON_SERVER['port'])
