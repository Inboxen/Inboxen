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

import logging
from datetime import datetime

from celery import chord
from django.contrib.auth import get_user_model
from django.db import transaction
from pytz import utc

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

    # remove identifying data from inbox
    inbox.deleted = True
    inbox.description = ""
    inbox.user = None
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

    log.info("Deletion tasks for %s sent off", user.username)
