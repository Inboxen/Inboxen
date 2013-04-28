from lamson.routing import route, stateless, nolocking
from lamson.queue import Queue
from config.settings import accepted_queue_dir, accepted_queue_opts_in, datetime_format, recieved_header_name
from app.model.alias import alias_exists
from datetime import datetime

# We don't change state based on who the sender is, so we're stateless and
# don't return any other state. Locking is done by the queue (on the filesystem
# at the time of writing)
@route("(alias)@(domain)", alias=".+", domain=".+")
@stateless
@nolocking
def START(message, alias=None, domain=None):
    """Does this alias exist? If yes, queue it. If no, drop it."""
    if alias_exists(alias, domain):
        message[recieved_header_name] = datetime.utcnow().strftime(datetime_format)
        #if spam filtering is enabled, do so

        #if not spam, or not filter:
        accept_queue = Queue(accepted_queue_dir, **accepted_queue_opts_in)
        accept_queue.push(message)

