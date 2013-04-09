import logging
from lamson.routing import route, stateless, nolocking
from config.settings import accepted_queue_dir, accepted_queue_opts
from app.model import alias

@route(".+")
def ACCEPT_MSG(message):
    accept_queue = queue.Queue(accepted_queue_dir, **accepted_queue_opts)
    accept_queue.push(message)
    return START

@route("(address)@(host)", address=".+")
def START(message, address=None, host=None):
    return START

