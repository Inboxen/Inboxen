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
from inboxen.tickets.models import Question, Response
from inboxen.utils.tasks import chunk_queryset, create_queryset, task_group_skew

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

QUESTION_RESET_FIELDS = [
    "author",
    "subject",
    "body",
]

RESPONSE_RESET_FIELDS = [
    "author",
    "body",
]


def model_cleaner(instance, fields):
    """Resets model fields to their defaults"""
    for field_name in fields:
        field = instance._meta.get_field(field_name)
        setattr(instance, field_name, field.get_default())


@app.task
@transaction.atomic()
def clean_questions(user_id):
    for question in Question.objects.filter(author_id=user_id):
        model_cleaner(question, QUESTION_RESET_FIELDS)
        question.date = datetime.utcfromtimestamp(0).replace(tzinfo=utc)
        question.save()


@app.task
@transaction.atomic()
def clean_responses(user_id):
    for response in Response.objects.filter(author_id=user_id):
        model_cleaner(response, RESPONSE_RESET_FIELDS)
        response.save()


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
    model_cleaner(inbox, INBOX_RESET_FIELDS)

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
    inbox_tasks = [disown_inbox.s(inbox.id) for inbox in inboxes]
    question_tasks = [clean_questions.s(user_id), clean_responses.s(user_id)]
    delete_chord = chord(inbox_tasks + question_tasks, finish_delete_user.s(user_id))
    delete_chord.apply_async()

    log.info("Deletion tasks for %s sent off", user.username)


@app.task
def user_suspended():
    now = timezone.now()
    for delta_start, delta_end, function in settings.USER_SUSPEND_TASKS:
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
def user_suspended_disable_emails(kwargs):
    kwargs = {"user__%s" % k: v for k, v in kwargs.items()}
    items = create_queryset("userprofile", kwargs=kwargs)
    items.update(receiving_emails=False)


@app.task
def user_suspended_delete_emails(kwargs, batch_number=500, chunk_size=10000, delay=20):
    kwargs = {"inbox__user__%s" % k: v for k, v in kwargs.items()}
    emails = create_queryset("email", kwargs=kwargs)
    for idx, chunk in chunk_queryset(emails, chunk_size):
        email_tasks = delete_inboxen_item.chunks([("email", i) for i in chunk], batch_number).group()
        task_group_skew(email_tasks, start=(idx + 1) * delay, step=delay)
        email_tasks.delay()


@app.task
def user_suspended_delete_user(kwargs, batch_number=500, chunk_size=10000, delay=20):
    users = create_queryset(get_user_model(), kwargs=kwargs)
    for idx, chunk in chunk_queryset(users, chunk_size):
        user_tasks = delete_account.chunks([(i,) for i in chunk], batch_number).group()
        task_group_skew(user_tasks, start=idx + 1, step=delay)
        user_tasks.delay()


@app.task
def user_suspended_delete_user_never_logged_in(kwargs, batch_number=500, chunk_size=10000, delay=20):
    kwargs = {k.replace("last_login", "date_joined"): v for k, v in kwargs.items()}
    kwargs["last_login__isnull"] = True
    user_suspended_delete_user(kwargs, batch_number, chunk_size, delay)
