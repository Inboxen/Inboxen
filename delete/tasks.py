import logging
from datetime import datetime
from itertools import izip_longest

from celery import chain, chord, group, task
from pytz import utc

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction

from inboxen.models import Email, Inbox, Tag, User

log = logging.getLogger(__name__)

@task(rate_limit="10/m", default_retry_delay=5*60) # 5 minutes
@transaction.atomic()
def delete_inbox(inbox_id, user_id=None):
    inbox = Inbox.objects

    if user_id is not None:
        inbox = Inbox.objects.filter(user__id=user_id)

    try:
        inbox = inbox.get(id=inbox_id)
    except Inbox.DoesNotExist:
        return False

    # delete emails in another task(s)
    batch_delete_items.delay("inbox", kwargs={'inbox_id': inbox.pk})

    # delete tags
    tags = Tag.objects.filter(inbox__id=inbox_id).only('id')
    tags.delete()

    # okay now mark the inbox as deleted
    inbox.created = datetime.fromtimestamp(0, utc)
    inbox.flags.deleted = True
    inbox.save()

    return True

@task(rate_limit=200)
@transaction.atomic()
def delete_email(email_id):
    email = Email.objects.only('id').get(id=email_id)
    email.delete()

@task()
@transaction.atomic()
def disown_inbox(result, inbox_id):
    inbox = Inbox.objects.get(id=inbox_id)
    inbox.user = None
    inbox.save()

@task(ignore_result=True)
@transaction.atomic()
def finish_delete_user(result, user_id):
    inbox = Inbox.objects.filter(user__id=user_id).only('id').exists()
    user = User.objects.get(id=user_id)
    if inbox:
        raise Exception("User {0} still has inboxes!".format(user.username))
    else:
        log.info("Deleting user %s", user.username)
        user.delete()

@task(ignore_result=True)
@transaction.atomic()
def delete_account(user_id):
    # first we need to make sure the user can't login
    user = User.objects.get(id=user_id)
    user.set_unusable_password()
    user.is_active = False
    user.save()

    # get ready to delete all inboxes
    inboxes = user.inbox_set.only('id')
    if len(inboxes): # pull in all the data
        delete = chord([chain(delete_inbox.s(inbox.id), disown_inbox.s(inbox.id)) for inbox in inboxes], finish_delete_user.s(user_id))
        delete.apply_async()

    log.info("Deletion tasks for %s sent off", user.username)

@task(rate_limit=200)
@transaction.atomic()
def delete_inboxen_item(model, item_pk):
    _model = ContentType.objects.get(app_label="inboxen", model=model).model_class()
    try:
        item = _model.objects.only('pk').get(pk=item_id)
        item.delete()
    except (IntegrityError, _model.DoesNotExist):
        pass

@task(rate_limit="1/m")
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
    _model = ContentType.objects.get(app_label="inboxen", model=model).model_class()

    if args is None and kwargs is None:
        raise Exception("You need to specify some filter options!")
    elif args is None:
        args = []
    elif kwargs is None:
        kwargs = {}

    items = _model.objects.only('pk').filter(*args, **kwargs)
    items = [(model, item.pk) for item in items]
    items = delete_inboxen_item.chunk(items, batch_number)
    items.apply_async()

@task(rate_limit="1/h")
def clean_orphan_models():
    # Body
    batch_delete_items.delay("body", kwargs={"partlist__isnull": True})

    # HeaderName
    batch_delete_items.delay("headername", kwargs={"header__isnull": True})

    # HeaderData
    batch_delete_items.delay("headerdata", kwargs={"header__isnull": True})
