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

from shutil import rmtree
import hashlib
import json
import logging
import mailbox
import os
import string
import tarfile
import time

from celery import chain, chord, Task
from django import urls
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import safestring, timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _

from inboxen import tasks
from inboxen.async_messages import message_user
from inboxen.celery import app
from inboxen.liberation import utils
from inboxen.liberation.models import Liberation
from inboxen.models import Email, Inbox
from inboxen.utils.tasks import task_group_skew

log = logging.getLogger(__name__)


FILE_NAME_TEMPLATE = "liberation_{id}_{created}"
TMP_SUBDIR = "tmp"


class LiberationTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if not isinstance(exc, Liberation.DoesNotExist):
            Liberation.objects.filter(id=kwargs["liberation_id"]).update(
                errored=True,
                error_message=str(exc),
                error_traceback=str(einfo),
                finished=timezone.now(),
            )


@transaction.atomic
@app.task(base=LiberationTask, rate_limit='4/h')
def liberate(*, liberation_id):
    lib_status = Liberation.objects.pending().select_for_update(skip_locked=True).get(id=liberation_id)
    try:
        lib_status.tmp_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    except (IOError, OSError) as error:
        log.info("Couldn't create dir at %s", lib_status.tmp_dir)
        raise liberate.retry(exc=error)

    lib_status.started = timezone.now()
    lib_status.save()
    inbox_tasks = [liberate_inbox.s(liberation_id, inbox) for inbox in
                   Inbox.objects.filter(user=user, deleted=False).values_list("id", flat=True)]
    chord(
        inbox_tasks,
        liberate_collect_emails.s(liberation_id=liberation_id)
    ).apply_async()


@app.task(rate_limit='100/m')
def liberate_inbox(*, liberation_id, inbox_id):
    """ Gather email IDs """
    lib_status = Liberation.objects.pending().get(id=liberation_id)
    inbox = Inbox.objects.get(id=inbox_id, deleted=False, user=lib_status.user_id)
    lib_status.maildir.add_folder(str(inbox))

    return {
        'folder': str(inbox),
        'ids': list(Email.objects.filter(inbox=inbox, deleted=False).values_list('id', flat=True)),
        "created": inbox.created.isoformat(),
        "description": inbox.description,
        "flags": {
            "deleted": inbox.deleted,
            "new": inbox.new,
            "exclude_from_unified": inbox.exclude_from_unified,
            "disabled": inbox.disabled,
            "pinned": inbox.pinned,
        },
    }


@app.task(base=LiberationTask)
def liberate_collect_emails(results, *, liberation_id):
    """ Send off data mining tasks """
    lib_status = Liberation.objects.pending().select_for_update(skip_locked=True).get(id=liberation_id)
    msg_tasks = []
    results = results or []
    inbox_data = {}
    for result in results:
        for email_id in result["ids"]:
            msg_tasks.append((liberation_id, result['folder'], email_id))
        inbox = result["folder"]
        result["email_count"] = len(result["ids"])
        del result["ids"]
        del result["folder"]

    msg_tasks = liberate_message.chunks(msg_tasks, 100).group()
    task_group_skew(msg_tasks, step=10)
    chain(
        msg_tasks,
        liberate_convert_box.s(liberation_id),
        liberate_fetch_info.s(liberation_id, results),
        liberate_tarball.s(liberation_id),
        liberation_finish.s(liberation_id)
    ).apply_async()


@app.task(rate_limit='1000/m')
@transaction.atomic()
def liberate_message(mail_path, inbox, email_id):
    """ Take email from database and put on filesystem """
    lib_status = Liberation.objects.pending().get(id=liberation_id)

    try:
        msg = Email.objects.get(id=email_id, deleted=False)
        msg = utils.make_message(msg)
        maildir.add(msg.as_bytes())
    except Exception as exc:
        msg_id = hex(int(email_id))[2:]
        log.warning("Exception processing %s", msg_id, exc_info=exc)
        return msg_id


@app.task(base=LiberationTask)
def liberate_convert_box(result, *, liberation_id):
    """ Convert maildir to mbox if needed """
    lib_status = Liberation.objects.pending().select_for_update(skip_locked=True).select_related("user").get(id=liberation_id)
    if lib_status.storage_type == Liberation.MAILBOX:
        maildir = lib_status.maildir
        mbox = mailbox.mbox(mail_path + '.mbox')
        mbox.lock()

        for inbox in maildir.list_folders():
            folder = maildir.get_folder(inbox)

            for key in folder.keys():
                msg = folder.pop(key)
                mbox.add(msg)
            maildir.remove_folder(inbox)

        rmtree(mail_path)
        mbox.close()

    return result


@app.task(base=LiberationTask)
def liberate_fetch_info(result, *, liberation_idi, inbox_results):
    """Fetch user info and dump json to files"""
    lib_status = Liberation.objects.pending().select_for_update(skip_locked=True).select_related("user").get(id=liberation_id)
    profile_json = get_user_profile(lib_status.user, result or [])
    inbox_json = json.dumps(inbox_results)

    with open(os.path.join(lib_status.tmp_dir, "profile.json"), "w") as profile:
        profile.write(profile_json)
    with open(os.path.join(lib_status.tmp_dir, "inbox.json"), "w") as inbox:
        inbox.write(inbox_json)


@app.task(base=LiberationTask, default_retry_delay=600)
def liberate_tarball(result, *, liberation_id):
    """ Tar up and delete the dir """
    lib_status = Liberation.objects.pending().select_for_update(skip_locked=True).get(id=liberation_id)
    tar_type = Liberation.ARCHIVE_TYPES[lib_status.compression_type]

    try:
        tar = tarfile.open(lib_status.path, tar_type['writer'])
    except (IOError, OSError) as error:
        log.debug("Couldn't open tarfile at %s", lib_status.path)
        raise liberate_tarball.retry(exc=error)

    date = str(lib_status.started)
    dir_name = "inboxen-%s" % date

    try:
        # directories are added recursively by default
        tar.add("%s/" % lib_status.tmp_dir, dir_name)
    finally:
        tar.close()
    rmtree(lib_status.tmp_dir, ignore_errors=True)


@app.task(base=LiberationTask, ignore_result=True)
@transaction.atomic()
def liberation_finish(result, *, liberation_id):
    """ Create email to send to user """
    lib_status = Liberation.objects.pending().select_for_update(skip_locked=True).select_related("user").get(id=liberation_id)
    lib_status.finished = timezone.now()
    lib_status.save()

    message = _("Your request for your personal data has been completed. Click "
                "<a class=\"alert-link\" href=\"%s\">here</a> to download your archive.")
    message_user(lib_status.user, safestring.mark_safe(message % urls.reverse("user-liberate-get")))

    log.info("Finished liberation for %s", options['user'])

    # run a garbage collection on all workers - liberation is leaky
    tasks.force_garbage_collection.delay()


def get_user_profile(user, email_results):
    """User profile data"""
    data = {}

    # user's preferences
    data["preferences"] = user.inboxenprofile.get_liberation_data()

    # user data
    data["id"] = user.id
    data["username"] = user.username
    data["is_active"] = user.is_active
    data["join_date"] = user.date_joined.isoformat()

    data["errors"] = []
    email_results = email_results or []
    for result in email_results:
        if result:
            data["errors"].append(str(result))

    return json.dumps(data)
