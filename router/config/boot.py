import logging
import logging.config
import os
import sys

from salmon import queue
from salmon.routing import Router
from salmon.server import SMTPReceiver, LMTPReceiver

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings

try:
    os.mkdir("logs", 0700)
except OSError:
    pass

try:
    os.mkdir("run", 0710)  # group can access files in "run"
except OSError:
    pass

if os.path.exists("config/logging.conf"):
    logging.config.fileConfig("config/logging.conf.default")
else:
    logging.config.fileConfig("config/logging.conf")

# where to listen for incoming messages
if settings.SALMON_SERVER["type"] == "lmtp":
    receiver = LMTPReceiver(socket=settings.SALMON_SERVER["path"])
elif settings.SALMON_SERVER["type"] == "smtp":
    receiver = SMTPReceiver(settings.SALMON_SERVER['host'],
                            settings.SALMON_SERVER['port'])

Router.load(['app.server'])
Router.RELOAD=False
Router.LOG_EXCEPTIONS=True
Router.UNDELIVERABLE_QUEUE=queue.Queue("run/undeliverable")
