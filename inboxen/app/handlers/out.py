from lamson.routing import route, stateless, nolocking
from app.model.email import make_email

@route("(alias)@(domain)", alias=".+", domain=".+")
@nolocking
@stateless
def START(message, alias=None, domain=None):

    # alias should have already have been checked before the email entered the
    # queue
    make_email(message, alias, domain)
