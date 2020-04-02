##
#    Copyright (C) 2013, 2014, 2015, 2016, 2017 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from datetime import datetime
import logging

from celery import chord
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from pytz import utc

from inboxen.celery import app
from inboxen.models import Inbox
from inboxen.tasks import batch_delete_items, delete_inboxen_item
from inboxen.utils.tasks import create_queryset, task_group_skew

log = logging.getLogger(__name__)

INBOX_RESET_FIELDS = [
    "description",
    "disabled",
    "exclude_from_unified",
    "new",
    "pinned",
    "search_tsv",
    "user",
]


@app.task(rate_limit="10/m", default_retry_delay=5 * 60)  # 5 minutes
@transaction.atomic()
def disown_inbox(inbox_id):
    try:
        inbox = Inbox.objects.get(id=inbox_id)
    except Inbox.DoesNotExist:
        return False

    # delete emails in another task(s)
    batch_delete_items.delay("email", kwargs={'inbox__id': inbox.pk})

    # remove data from inbox
    for field_name in INBOX_RESET_FIELDS:
        field = Inbox._meta.get_field(field_name)
        setattr(inbox, field_name, field.get_default())

    inbox.deleted = True
    inbox.created = datetime.utcfromtimestamp(0).replace(tzinfo=utc)

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
    else:
        finish_delete_user.apply_async(args=[None, user_id])

    log.info("Deletion tasks for %s sent off", user.username)


@app.task
def user_ice():
    now = timezone.now()
    for delta_start, delta_end, function in settings.USER_ICE_TASKS:
        kwargs = {}
        if delta_start is None:
            kwargs["last_login__gt"] = now - delta_end
        elif delta_end is None:
            kwargs["last_login__lt"] = now - delta_start
        else:
            kwargs["last_login__range"] = (now - delta_end, now - delta_start)
        task = app.tasks[function]
        task.apply_async(kwargs={"kwargs": kwargs})


@app.task
def user_ice_disable_emails(kwargs, batch_number=500):
    kwargs = {"user__%s" % k: v for k, v in kwargs.items()}
    items = create_queryset("userprofile", kwargs=kwargs)
    items.update(receiving_emails=False)


@app.task
def user_ice_delete_emails(kwargs, batch_number=500):
    kwargs = {"inbox__user__%s" % k: v for k, v in kwargs.items()}
    emails = create_queryset("email", kwargs=kwargs)
    email_tasks = delete_inboxen_item.chunks([("email", i.pk,) for i in emails.iterator()], batch_number).group()
    if len(email_tasks) == 0:
        return

    task_group_skew(email_tasks, step=batch_number/10.0)
    email_tasks.delay()


@app.task
def user_ice_delete_user(kwargs, batch_number=500):
    users = create_queryset(get_user_model(), kwargs=kwargs)
    user_tasks = delete_account.chunks([(i.pk,) for i in users.iterator()], batch_number).group()
    if len(user_tasks) == 0:
        return

    task_group_skew(user_tasks, step=batch_number/10.0)
    user_tasks.delay()


@app.task
def user_ice_delete_user_never_logged_in(kwargs, batch_number=500):
    kwargs = {k.replace("last_login", "date_joined"): v for k, v in kwargs.items()}
    kwargs["last_login__isnull"] = True
    user_ice_delete_user(kwargs, batch_number)
