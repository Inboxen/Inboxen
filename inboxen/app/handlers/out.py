from lamson.routing import route, stateless
from config.settings import datetime_format
from datetime import datetime

@route("(alias)@(domain)", alias=".+", domain=".+")
@stateless
def START(message, alias=None, domain=None):
    pass
    #split email into headers. body (if it exists), mime parts
    #push to db

