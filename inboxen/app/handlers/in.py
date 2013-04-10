from lamson.routing import route
from lamson.queue import Queue
from config.settings import accepted_queue_dir, accepted_queue_opts
from app.model.alias import alias_exists

@route("(alias)@(domain)", alias=".+", domain=".+")
def START(message, alias=None, domain=None):
    if alias_exists(alias, domain):
        return ACCEPT_MSG

@route(".+")
def ACCEPT_MSG(message):
    accept_queue = Queue(accepted_queue_dir, **accepted_queue_opts)
    accept_queue.push(message)
