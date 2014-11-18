import logging
import logging.config
import os

from config import settings
from salmon import queue
from salmon.routing import Router

__all__ = ["settings"]

try:
    os.mkdir("logs", 0700)
except OSError:
    pass

try:
    os.mkdir("run", 0710)  # group can access files in "run"
except OSError:
    pass

if os.path.exists("config/logging.conf"):
    logging.config.fileConfig("config/logging.conf")
else:
    logging.config.fileConfig("config/logging.conf.default")

Router.load(['app.server'])
Router.RELOAD = False
Router.LOG_EXCEPTIONS = True
Router.UNDELIVERABLE_QUEUE = queue.Queue("run/undeliverable")
