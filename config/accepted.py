from config import settings
from salmon.routing import Router
from salmon.server import QueueReceiver
from salmon import queue
import logging
import logging.config

logging.config.fileConfig("config/logging.conf")

settings.receiver = QueueReceiver(settings.accepted_queue_dir,
                            **settings.accepted_queue_opts_out)

Router.defaults(**settings.router_defaults)
Router.load(settings.out_handlers)
Router.RELOAD=False
Router.LOG_EXCEPTIONS=True
Router.UNDELIVERABLE_QUEUE=queue.Queue("run/undeliverable")
