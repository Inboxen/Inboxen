from lamson.routing import route, stateless, nolocking
from lamson.queue import Queue
from config.settings import accepted_queue_dir, accepted_queue_opts, datetime_format
from app.model.alias import alias_exists
from datetime import datetime

@route("(alias)@(domain)", alias=".+", domain=".+")
@stateless
@nolocking
def START(message, alias=None, domain=None):
    """Does this alias exist? If yes, queue it. If no, drop it."""
    if alias_exists(alias, domain):
        message.base.['x-lamson-recieve'] = datetime.strftime(datetime_format)
        #if spam filtering is enabled, do so

        #if not spam, or not filter:
        accept_queue = Queue(accepted_queue_dir, **accepted_queue_opts)
        accept_queue.push(message)

