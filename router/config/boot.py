import logging
import logging.config
import os

from django.conf import settings as dj_settings
from salmon import queue
from salmon.routing import Router

from config import settings

__all__ = ["settings"]

try:
    os.mkdir("logs", 0700)
except OSError:
    pass

try:
    os.mkdir("run", 0710)  # group can access files in "run"
except OSError:
    pass

logconfig_path = os.path.join(dj_settings.BASE_DIR, "router", "config", "logging.conf")
if not os.path.exists(logconfig_path):
    logconfig_path = os.path.join(dj_settings.BASE_DIR, "router", "config", "logging.conf.default")

logging.config.fileConfig(logconfig_path)

Router.load(['app.server'])
Router.RELOAD = False
Router.LOG_EXCEPTIONS = True
Router.UNDELIVERABLE_QUEUE = queue.Queue("run/undeliverable")
