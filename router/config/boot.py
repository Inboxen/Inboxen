import os
import logging
import logging.config

from config import settings
from salmon import queue
from salmon.routing import Router
from salmon.server import SMTPReceiver, LMTPReceiver

logging.config.fileConfig("config/logging.conf.default")
logging.config.fileConfig("config/logging.conf")

try:
    os.mkdir("logs", 0700)
except OSError:
    pass

try:
    os.mkdir("run", 0710)  # group can access files in "run"
except OSError:
    pass

# where to listen for incoming messages
if settings.receiver_config["type"] == "lmtp":
    settings.receiver = LMTPReceiver(socket=settings.receiver_config['path'])
elif settings.receiver_config["type"] == "smtp":
    settings.receiver = SMTPReceiver(settings.receiver_config['host'],
                                     settings.receiver_config['port'])

Router.defaults(**settings.router_defaults)
Router.load(settings.handlers)
Router.RELOAD=False
Router.LOG_EXCEPTIONS=True
Router.UNDELIVERABLE_QUEUE=queue.Queue("run/undeliverable")
