from config import settings
from lamson.routing import Router
from lamson.server import QueueReceiver
from lamson import view, queue
import logging
import logging.config
import jinja2

logging.config.fileConfig("config/logging.conf")

settings.receiver = QueueReceiver(settings.accepted_queue_dir,
                            **settings.accepted_queue_opts)

Router.defaults(**settings.router_defaults)
Router.load(settings.out_handlers)
Router.RELOAD=True
Router.UNDELIVERABLE_QUEUE=queue.Queue("run/undeliverable")

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'], 
                                settings.template_config['module']))

