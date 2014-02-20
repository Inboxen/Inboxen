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
from email.message import Message
from shutil import rmtree

from celery import task, chain, group, chord
from pytz import utc

from django.conf import settings
from django.db import transaction

from inboxen.models import Domain, Email, Inbox, PartList, Tag, User

log = logging.getLogger(__name__)

for setting_name in ('LIBERATION_BODY', 'LIBERATION_SUBJECT', 'LIBERATION_PATH'):
    assert hasattr(settings, setting_name), "%s has not been set" % setting_name

TAR_TYPES = {
    'tar.gz': {'writer': 'w:gz', 'mime-type': 'application/x-gzip'},
    'tar.bz2': {'writer': 'w:bz2', 'mime-type': 'application/x-bzip2'},
    'tar': {'writer': 'w:', 'mime-type': 'application/x-tar'}
    }

@task(rate_limit='4/h')
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

@task(rate_limit='10/m')
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

def make_message(message):
    """ Make a Python  email.message.Message from our models """
    parents = {}
    part_list = message.parts.all()
    first = None

    for part in part_list:
        msg = Message()

        header_set = part.header_set.order_by("ordinal").select_related("name__name", "data__data")
        for header in header_set:
            msg[header.name.name] = header.data.data

        if msg.is_multipart():
            parents[part.id] = msg
        else:
            msg.set_payload(part.body.data)

        if first is None:
            first = msg
        else:
            parents[part.parent_id].attach(msg)

    return first

@task(rate_limit='1000/m')
@transaction.atomic()
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

    maildir.add(msg)

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
@transaction.atomic()
def liberation_finish(result, options):
    """ Create email to send to user """
    tags = liberate_inbox_tags(options['user'], result['date'])
    profile = liberate_user_profile(options['user'], result['results'], result['date'])

    inbox_tags = ["Inboxen", "data", "liberation"]
    inbox = Inbox.objects
    for tag in inbox_tags:
        inbox = inbox.filter(tag__tag=tag)

    try:
        inbox = inbox.get(user__id=options["user"])
    except Inbox.MultipleObjectsReturned:
        inbox = inbox.filter(user__id=options["user"])[0]
    except Inbox.DoesNotExist:
        domain = random.choice(Domain.objects.all())
        inbox = Inbox.objects.create(domain=domain, user_id=options["user"])
        for tag in inbox_tags:
            tag = Tag(tag=tag, inbox=inbox)
            tag.save()

    email = Email(inbox=inbox reveived_date=datetime.now())
    main_body = Body.objects.get_or_create(data="")
    main_part = PartList(body=main_body, email=email)
    main_part.save()

    main_headers = main_part.header_set
    main_headers.get_or_create(name="From", data="support@inboxen.org", ordinal=0)
    main_headers.get_or_create(name="Subject", data=settings.LIBERATION_SUBJECT, ordinal=1)
    main_headers.get_or_create(name="Content-Type", data="multipart/mixed; boundary=\"InboxenIsTheBest\"")

    msg_body = Body.objects.get_or_create(data=settings.LIBERATION_BODY)
    msg_part = PartList(body=msg_body, email=email, parent=main_part)
    msg_part.save()
    msg_part.headers_set.get_or_create(name="Content-Type", data="text/plain")

    if not options.get("noEmail", False):
        archive_body = Body.objects.get_or_create(path=result["path"])[0]
        archive_part = PartList(body=archive_body, email=email, parent=main_part)
        archive_part.save()
        archive_headers = archive.header_set
        cont_dispos = "attachment; filename=\"emails-{0}.{1}\"".format(result['date'], options.get('compressType', 'tar.gz'))
        archive_headers.get_or_create(name="Content-Type", data=result['mime-type'], ordinal=0)
        archive_headers.get_or_create(name="Content-Disposition", data=cont_dispos, ordinal=1)

    profile_body = Body.objects.get_or_create(data=profile['data'])[0]
    profile_part = PartList(body=profile_body, email=email, parent=main_part)
    profile_part.save()
    profile_headers = profile_part.header_set
    cont_dispos = "attachment; filename=\"{0}\"".format(profile['name'])
    profile_headers.get_or_create(name="Content-Type", data=profile['type'], ordinal=0)
    profile_headers.get_or_create(name="Content-Disposition", data=cont_dispos, ordinal=1)

    tags_body = Body.objects.get_or_create(data=tags['data'])[0]
    tags_part = PartList(body=tags_body, email=email, partent=main_part)
    tags_part.save()
    tags_headers = tags_part.header_set
    cont_dispos = "attachment; filename=\"{0}\"".format(tags['name'])
    tags_headers.get_or_create(name="Content-Type", data=tags['type'], ordinal=0)
    tags_headers.get_or_create(name="Content-Disposition", data=cont_dispos, ordinal=1)

    log.debug("Finished liberation for %s", user.username)

def liberate_user_profile(user_id, email_results, date):
    """ User profile data """
    data = {
        'preferences':{}
    }
    user = User.objects.get(id=user_id)


    # user's preferences
    profile = user.userprofile
    if profile.html_preference == 1:
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

