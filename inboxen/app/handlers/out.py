import logging
from lamson.routing import route, stateless
from config.settings import database
from lamson import view


@route("(alias)@(domain)", alias=".+", domain=".+")
@stateless
def START(message, alias=None, domain=None):
    pass
    #split email into headers. body (if it exists), mime parts
    #push to db

