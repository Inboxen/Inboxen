import logging
import types
from datetime import datetime

from celery import chain, chord, group, task
from pytz import utc

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from inboxen.helper.user import null_user, user_profile
from inboxen.models import Attachment, Domain, Header, Email, Inbox, Tag

log = logging.getLogger(__name__)

@task(rate_limit="10/m", default_retry_delay=5 * 60) # 5 minutes
@transaction.atomic()
def delete_inbox(email, user=None):
    if type(email) in [types.StringType, types.UnicodeType]:
        if not user:
            raise Exception("Need to give username")
        inbox, domain = email.split("@", 1)
        try:
            inbox = Inbox.objects.get(inbox=inbox, domain__domain=domain, user=user)
        except Inbox.DoesNotExist:
            return False
    else:
        user = email.user
        inbox = email

    # delete emails in another task(s)
    emails = Email.objects.filter(inbox=inbox, user=user).only('id')

    # sending an ID over the wire and refetching the Django model on the side
    # is cheaper than serialising the Django model - this appears to be the
    # cause of our previous memory issues! - M
    emails = group([delete_email.s(email.id) for email in emails])
    try:
        emails.apply_async()
    except IndexError:
        # no emails in this inbox
        pass

    # okay now mark the inbox as deleted
    inbox.created = datetime.fromtimestamp(0, utc)
    inbox.save()

    return True

@task(rate_limit=200)
@transaction.atomic()
def delete_email(email_id):
    email = Email.objects.only('id').get(id=email_id)
    email.delete()

@task(rate_limit=200)
@transaction.atomic()
def delete_inboxen_item(model, item_id):
    _model = ContentType.objects.get(app_label="inboxen", model=model).model_class()

    item = _model.objects.only('id').get(id=item_id)
    item.delete()

@task()
@transaction.atomic()
def disown_inbox(result, inbox, futr_user=None):
    if not futr_user:
        futr_user = null_user()

    # delete tags
    tags = Tag.objects.filter(inbox=inbox).only('id')
    tags.delete()

    inbox.user = futr_user
    inbox.save()

@task()
@transaction.atomic()
def delete_user(result, user):
    inbox = Inbox.objects.filter(user=user).only('id').exists()
    if inbox:
        raise Exception("User {0}  still has inboxes!".format(user))
    else:
        log.debug("Deleting user %s" % user.username)
        user.delete()
    return True

@task()
@transaction.atomic()
def delete_account(user):
    # first we need to make sure the user can't login
    user.set_unusable_password()
    user.is_active = False
    user.save()

    # get ready to delete all inboxes
    inbox = Inbox.objects.filter(user=user).only('id')
    if len(inbox): # pull in all the data
        delete = chord([chain(delete_inbox.s(a), disown_inbox.s(a)) for a in inbox], delete_user.s(user))
        delete.apply_async()

    log.debug("Deletion tasks for %s sent off", user.username)

@task(rate_limit="1/m")
@transaction.atomic()
def major_cleanup_items(model, filter_args=None, filter_kwargs=None, batch_number=1000, count=0):
    """If something goes wrong and you've got a lot of orphaned entries in the
    database, then this is the task you want.

    * model is a string
    * filter_args and filter_kwargs should be obvious
    * batch_number is the number of delete tasks that get sent off in one go
    """
    _model = ContentType.objects.get(app_label="inboxen", model=model).model_class()

    if filter_args and filter_kwargs:
        items = _model.objects.only('id').filter(*filter_args, **filter_kwargs)
    elif filter_args:
        items = _model.objects.only('id').filter(*filter_args)
    elif filter_kwargs:
        items = _model.objects.only('id').filter(**filter_kwargs)
    else:
        raise Exception("You need to specify some filter options!")

    tasks = [delete_email_item.s(model, item.id) for item in items[:batch_number]]

    if len(tasks):
        tasks = chord(tasks, major_cleanup_items.si(model, filter_args, filter_kwargs, batch_number, count+1))
        tasks.apply_async()
        log.warning("%s deletes sent (overestimate), %s completed", batch_number, count*batch_number)
    else:
        log.warning("Batch deletes finished")
