import logging
from lamson.routing import route, stateless, nolocking
from config.settings import accepted_queue
from lamson import view


@route("(address)@(host)", address=".+")
@stateless
@nolocking
def START(message, address=None, host=None):
    accepted_queue.push(message)

