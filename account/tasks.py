import logging
from datetime import datetime

from celery import chord
from pytz import utc

from django.contrib.auth import get_user_model
from django.db import transaction

from inboxen.celery import app
from inboxen.models import Inbox
from inboxen.tasks import batch_delete_items

log = logging.getLogger(__name__)


@app.task(rate_limit="10/m", default_retry_delay=5 * 60)  # 5 minutes
@transaction.atomic()
def disown_inbox(inbox_id):
    try:
        inbox = Inbox.objects.get(id=inbox_id)
    except Inbox.DoesNotExist:
        return False

    # delete emails in another task(s)
    batch_delete_items.delay("email", kwargs={'inbox__id': inbox.pk})

    # okay now mark the inbox as deleted
    inbox.created = datetime.fromtimestamp(0, utc)
    inbox.flags.deleted = True
    inbox.description = ""
    inbox.user = None
    inbox.save()

    return True


@app.task(ignore_result=True)
@transaction.atomic()
def finish_delete_user(result, user_id):
    inbox = Inbox.objects.filter(user__id=user_id).only('id').exists()
    user = get_user_model().objects.get(id=user_id)
    if inbox:
        raise Exception("User {0} still has inboxes!".format(user.username))
    else:
        log.info("Deleting user %s", user.username)
        user.delete()


@app.task(ignore_result=True)
@transaction.atomic()
def delete_account(user_id):
    # first we need to make sure the user can't login
    user = get_user_model().objects.get(id=user_id)
    user.set_unusable_password()
    user.is_active = False
    user.save()

    # get ready to delete all inboxes
    inboxes = user.inbox_set.only('id')
    if len(inboxes):  # pull in all the data
        delete = chord([disown_inbox.s(inbox.id) for inbox in inboxes], finish_delete_user.s(user_id))
        delete.apply_async()

    log.info("Deletion tasks for %s sent off", user.username)
