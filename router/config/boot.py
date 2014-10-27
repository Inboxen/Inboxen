import logging
import logging.config
import os
import sys

from salmon import queue
from salmon.routing import Router
from salmon.server import SMTPReceiver, LMTPReceiver

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

receiver_config = {'host': 'localhost', 'port': 8823, "type": "smtp"}
handlers = ['app.server']

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
if receiver_config["type"] == "lmtp":
    receiver = LMTPReceiver(socket=receiver_config['path'])
elif receiver_config["type"] == "smtp":
    receiver = SMTPReceiver(receiver_config['host'],
                                     receiver_config['port'])

Router.defaults(**router_defaults)
Router.load(handlers)
Router.RELOAD=False
Router.LOG_EXCEPTIONS=True
Router.UNDELIVERABLE_QUEUE=queue.Queue("run/undeliverable")
