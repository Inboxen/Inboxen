from config import settings
from lamson.routing import Router
from lamson.server import SMTPReceiver
from lamson import queue
import logging
import logging.config

logging.config.fileConfig("config/logging.conf")

# where to listen for incoming messages
settings.receiver = SMTPReceiver(settings.receiver_config['host'],
                                 settings.receiver_config['port'])

Router.defaults(**settings.router_defaults)
Router.load(settings.in_handlers)
Router.RELOAD=False
Router.LOG_EXCEPTIONS=True
Router.UNDELIVERABLE_QUEUE=queue.Queue("run/undeliverable")
