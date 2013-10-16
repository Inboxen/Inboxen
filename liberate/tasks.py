import json
import hashlib
import logging
import mailbox
import os
import random
import string
import tarfile
import time
from datetime import datetime
from shutil import rmtree

from celery import task, chain, group, chord
from pytz import utc

from django.conf import settings
from django.db import transaction

from inboxen.helper.inbox import gen_inbox
from inboxen.helper.mail import send_email, make_message
from inboxen.helper.user import user_profile
from inboxen.models import Attachment, Domain, Email, Inbox, Tag, User

log = logging.getLogger(__name__)

for setting_name in ('LIBERATION_BODY', 'LIBERATION_SUBJECT', 'LIBERATION_PATH'):
    assert hasattr(settings, setting_name), "%s has not been set" % setting_name

TAR_TYPES = {
    'tar.gz': {'writer': 'w:gz', 'mime-type': 'application/x-gzip'},
    'tar.bz2': {'writer': 'w:bz2', 'mime-type': 'application/x-bzip2'},
    'tar': {'writer': 'w:', 'mime-type': 'application/x-tar'}
    }

@task(rate_limit='2/h')
def liberate(user, options=None):
    """ Get set for liberation, expects User object """

    if options == None:
        options = {}

    options['user'] = user.id

    rstr = ""
    for i in range(7):
        rstr += string.ascii_letters[random.randint(0, 50)]
    mail_path = "%s/%s_%s_%s_%s" % (settings.LIBERATION_PATH, time.time(), os.getpid(), rstr, hashlib.sha256(user.username + rstr).hexdigest()[:50])

    # make maildir
    mailbox.Maildir(mail_path)

    tasks = chord(
                [liberate_inbox.s(mail_path, inbox.id) for inbox in Inbox.objects.filter(user=user, deleted=False).only('id')],
                liberate_collect_emails.s(mail_path, options)
                )
    tasks.apply_async()

@task(rate_limit='100/h')
def liberate_inbox(mail_path, inbox_id):
    """ Gather email IDs """

    inbox = Inbox.objects.get(id=inbox_id, deleted=False)
    maildir = mailbox.Maildir(mail_path)
    maildir.add_folder(str(inbox))

    return {
            'folder': str(inbox),
            'ids': [email.id for email in Email.objects.filter(inbox=inbox, deleted=False).only('id')]
            }

@task()
def liberate_collect_emails(results, mail_path, options):
    """ Send off data mining tasks """

    msg_tasks = []
    for result in results:
        inbox = [liberate_message.s(mail_path, result['folder'], email_id) for email_id in result['ids']]
        msg_tasks.extend(inbox)
    if len(msg_tasks) > 0:
        msg_tasks = chain(
                        group(msg_tasks),
                        liberate_convert_box.s(mail_path, options),
                        liberate_tarball.s(mail_path, options),
                        liberation_finish.s(options)
                        )
    else:
        options["noEmails"] = True
        msg_tasks = liberation_finish.s(options)

    msg_tasks.apply_async()

@task(rate_limit='1000/m')
def liberate_message(mail_path, inbox, email_id):
    """ Take email from database and put on filesystem """
    maildir = mailbox.Maildir(mail_path).get_folder(inbox)

    try:
        msg = Email.objects.get(id=email_id, deleted=False)
        msg = make_message(msg)
    except Exception, exc:
        msg_id = hex(int(email_id))[2:]
        log.debug("Exception processing %s", msg_id, exc_info=exc)
        raise Exception(msg_id)

    maildir.add(str(msg))

@task()
def liberate_convert_box(result, mail_path, options):
    """ Convert maildir to mbox if needed """
    if options['mailType'] == 'maildir':
        pass

    elif options['mailType'] == 'mailbox':

        maildir = mailbox.Maildir(mail_path)
        mbox = mailbox.mbox(mail_path + '.mbox')
        mbox.lock()

        for inbox in maildir.list_folders():
            folder = maildir.get_folder(inbox)

            for key in folder.iterkeys():
                msg = str(folder.pop(key))
                mbox.add(msg)
            maildir.remove_folder(inbox)

        rmtree(mail_path)
        mbox.close()

    return result

@task(default_retry_delay=600)
def liberate_tarball(result, mail_path, options):
    """ Tar up and delete the maildir """

    tar_type = TAR_TYPES[options.get('compressType', 'tar.gz')]
    tar_name = "%s.%s" % (mail_path, options.get('compressType', 'tar.gz'))

    try:
        tar = tarfile.open(tar_name, tar_type['writer'])
    except (IOError, OSError), error:
        log.debug("Couldn't open tarfile at %s", tar_name)
        raise liberate_tarball.retry(exc=error)

    date = str(datetime.now(utc).date())
    dir_name = "inboxen-%s" % date

    if options['mailType'] == 'maildir':
        try:
            tar.add("%s/" % mail_path, dir_name) # directories are added recursively by default
        finally:
            tar.close()
        rmtree(mail_path)

    elif options['mailType'] == 'mailbox':
        try:
            tar.add("%s.mbox" % mail_path, dir_name)
        finally:
            tar.close()
        os.remove("%s.mbox" % mail_path)

    return {'path': tar_name, 'mime-type': tar_type['mime-type'], 'date': date, 'results': result}

@task()
@transaction.commit_on_success
def liberation_finish(result, options):
    """ Create email to send to user """

    if not options.get("noEmail", False):
        archive = Attachment(
                    path=result['path'],
                    content_type=result['mime-type'],
                    content_disposition="emails-%s.%s" % (result['date'], options.get('compressType', 'tar.gz'))
                    )
        archive.save()

    profile = liberate_user_profile(options['user'], result['results'], result['date'])
    profile = Attachment(
                data=profile['data'],
                content_type=profile['type'],
                content_disposition=profile['name']
                )
    profile.save()

    inbox_tags = liberate_inbox_tags(options['user'], result['date'])
    inbox_tags = Attachment(
                data=inbox_tags['data'],
                content_type=inbox_tags['type'],
                content_disposition=inbox_tags['name']
                )
    inbox_tags.save()

    inbox = Inbox.objects.filter(tag__tag="Inboxen")
    inbox = inbox.filter(tag__tag="data")
    inbox = inbox.filter(tag__tag="liberation")

    user = User.objects.get(id=options['user'])
    try:
        inbox = inbox.get(user=user)
    except Inbox.MultipleObjectsReturned:
        inbox = inbox.filter(user=user)[0]
    except Inbox.DoesNotExist:
        inbox = Inbox(
                inbox=gen_inbox(5),
                domain=random.choice(Domain.objects.all()),
                user=user,
                created=datetime.now(utc),
                deleted=False
            )
        inbox.save()
        tags = ["Inboxen", "data", "liberation"]
        for i, tag in enumerate(tags):
            tags[i] = Tag(tag=tag, inbox=inbox)
            tags[i].save()


    send_email(
        inbox=inbox,
        sender="support@inboxen.org",
        subject=settings.LIBERATION_SUBJECT,
        body=settings.LIBERATION_BODY,
        attachments=[archive, profile, inbox_tags]
        )
    log.debug("Finished liberation for %s", user.username)

def liberate_user_profile(user_id, email_results, date):
    """ User profile data """
    data = {
        'preferences':{}
    }
    user = User.objects.get(id=user_id)


    # user's preferences
    profile = user_profile(user)
    if profile.html_preference == 0:
        data['preferences']['html_preference'] = 'Reject HTML'
    elif profile.html_preference == 1:
        data['preferences']['html_preference'] = 'Prefer plain-text'
    else:
        data['preferences']['html_preference'] = 'Prefer HTML'

    data['preferences']['pool_amount'] = profile.pool_amount

    # user data
    data["id"] = user.id
    data['username'] = user.username
    data['is_staff'] = user.is_staff
    data['is_superuser'] = user.is_superuser
    data["is_active"] = user.is_active
    data['last_login'] = user.last_login.isoformat()
    data['join_date'] = user.date_joined.isoformat()
    data['groups'] = [str(groups) for groups in user.groups.all()]

    data['errors'] = []
    for result in email_results:
        if result != None:
            data['errors'].append(str(result))

    data = json.dumps(data)

    return {
        'data':data,
        'type':'application/json',
        'name':"user-%s.json" % date
    }

def liberate_inbox_tags(user_id, date):
    """ Grab tags from inboxes """
    data = {}

    inboxes = Inbox.objects.filter(user__id=user_id)
    for inbox in inboxes:
        email = "%s@%s" % (inbox.inbox, inbox.domain)
        tags = [tag.tag for tag in Tag.objects.filter(inbox=inbox)]
        data[email] = {
            "created":inbox.created.isoformat(),
            "deleted":inbox.deleted,
            "tags":tags,
        }

    data = json.dumps(data)

    return {
        "data":data,
        "type":"application/json",
        "name":"inboxes-%s.json" % date
    }

