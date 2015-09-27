import logging
from datetime import datetime

from celery import chain, chord
from pytz import utc

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.apps import apps

from inboxen.models import Inbox
from inboxen.celery import app

log = logging.getLogger(__name__)


@app.task(rate_limit="10/m", default_retry_delay=5*60)  # 5 minutes
@transaction.atomic()
def delete_inbox(inbox_id):
    inbox = Inbox.objects

    try:
        inbox = inbox.get(id=inbox_id)
    except Inbox.DoesNotExist:
        return False

    # delete emails in another task(s)
    batch_delete_items.delay("email", kwargs={'inbox__id': inbox.pk})

    # okay now mark the inbox as deleted
    inbox.created = datetime.fromtimestamp(0, utc)
    inbox.flags.deleted = True
    inbox.description = ""
    inbox.save()

    return True


@app.task()
@transaction.atomic()
def disown_inbox(result, inbox_id):
    inbox = Inbox.objects.get(id=inbox_id)
    inbox.user = None
    inbox.save()


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
        delete = chord([chain(delete_inbox.s(inbox.id), disown_inbox.s(inbox.id)) for inbox in inboxes], finish_delete_user.s(user_id))
        delete.apply_async()

    log.info("Deletion tasks for %s sent off", user.username)


@app.task(rate_limit=500)
@transaction.atomic()
def delete_inboxen_item(model, item_pk):
    _model = apps.get_app_config("inboxen").get_model(model)
    try:
        item = _model.objects.only('pk').get(pk=item_pk)
        item.delete()
    except (IntegrityError, _model.DoesNotExist):
        pass


@app.task(rate_limit="1/m")
@transaction.atomic()
def batch_delete_items(model, args=None, kwargs=None, batch_number=500):
    """If something goes wrong and you've got a lot of orphaned entries in the
    database, then this is the task you want.

    Be aware: this task pulls a list of PKs from the database which may cause
    increased memory use in the short term.

    * model is a string
    * args and kwargs should be obvious
    * batch_number is the number of delete tasks that get sent off in one go
    """
    _model = apps.get_app_config("inboxen").get_model(model)

    if args is None and kwargs is None:
        raise Exception("You need to specify some filter options!")
    elif args is None:
        args = []
    elif kwargs is None:
        kwargs = {}

    items = _model.objects.only('pk').filter(*args, **kwargs)
    items = [(model, item.pk) for item in items.iterator()]
    if len(items) == 0:
        return

    items = delete_inboxen_item.chunks(items, batch_number).group()
    items.skew(step=batch_number/10.0)
    items.apply_async()


@app.task(rate_limit="1/h")
def clean_orphan_models():
    # Body
    batch_delete_items.delay("body", kwargs={"partlist__isnull": True})

    # HeaderName
    batch_delete_items.delay("headername", kwargs={"header__isnull": True})

    # HeaderData
    batch_delete_items.delay("headerdata", kwargs={"header__isnull": True})
