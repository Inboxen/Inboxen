from config import settings
from lamson.routing import Router
from lamson.server import SMTPReceiver
from lamson import view, queue
import logging
import logging.config
import jinja2

logging.config.fileConfig("config/logging.conf")

settings.accepted_queue = queue.Queue(settings.accepted_queue_dir,
                            **settings.accepted_queue_opts)

##
# TODO: add something to dump messages into db
##

Router.defaults(**settings.router_defaults)
Router.load(settings.out_handlers)
Router.RELOAD=True
Router.UNDELIVERABLE_QUEUE=queue.Queue("run/undeliverable")

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'], 
                                settings.template_config['module']))

