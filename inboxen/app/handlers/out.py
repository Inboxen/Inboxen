from lamson.routing import route, stateless
from app.model.email import make_email

@route("(alias)@(domain)", alias=".+", domain=".+")
@stateless
def START(message, alias=None, domain=None):
    make_email(message, alias, domain)
