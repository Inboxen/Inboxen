import logging
from lamson.routing import route, route_like, stateless
from config.settings import database
from lamson import view


@route("(address)@(host)", address=".+")
@stateless
@nolocking
def START(message, address=None, host=None):
    database.push(message)

