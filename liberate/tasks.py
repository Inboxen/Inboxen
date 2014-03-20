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

from inboxen.models import Body, Domain, Email, Header, Inbox, PartList, Tag, User
from queue.liberate import utils

log = logging.getLogger(__name__)

for setting_name in ('LIBERATION_BODY', 'LIBERATION_SUBJECT', 'LIBERATION_PATH'):
    assert hasattr(settings, setting_name), "%s has not been set" % setting_name

TAR_TYPES = {
    '0': {'ext': 'tar.gz', 'writer': 'w:gz', 'mime-type': 'application/x-gzip'},
    '1': {'ext': 'tar.bz2', 'writer': 'w:bz2', 'mime-type': 'application/x-bzip2'},
    '2': {'ext': 'tar', 'writer': 'w:', 'mime-type': 'application/x-tar'}
    }

@task(rate_limit='4/h')
def liberate(user_id, options=None):
    """ Get set for liberation, expects User object """

    if options == None:
        options = {}

    options['user'] = user_id
    user =  User.objects.get(id=user_id)

    rstr = ""
    for i in range(7):
        rstr += string.ascii_letters[random.randint(0, 50)]
    mail_path = "%s/%s_%s_%s_%s" % (settings.LIBERATION_PATH, time.time(), os.getpid(), rstr, hashlib.sha256(user.username + rstr).hexdigest()[:50])

    # make maildir
    mailbox.Maildir(mail_path)

    tasks = chord(
                [liberate_inbox.s(mail_path, inbox.id) for inbox in Inbox.objects.filter(user=user, flags=~Inbox.flags.deleted).only('id')],
                liberate_collect_emails.s(mail_path, options)
                )
    tasks.apply_async()

@task(rate_limit='100/m')
def liberate_inbox(mail_path, inbox_id):
    """ Gather email IDs """

    inbox = Inbox.objects.get(id=inbox_id, flags=~Inbox.flags.deleted)
    maildir = mailbox.Maildir(mail_path)
    maildir.add_folder(str(inbox))

    return {
            'folder': str(inbox),
            'ids': [email.id for email in Email.objects.filter(inbox=inbox, flags=~Email.flags.deleted).only('id')]
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
@transaction.atomic()
def liberate_message(mail_path, inbox, email_id):
    """ Take email from database and put on filesystem """
    maildir = mailbox.Maildir(mail_path).get_folder(inbox)

    try:
        msg = Email.objects.get(id=email_id, flags=~Email.flags.deleted)
        msg = utils.make_message(msg)
        maildir.add(msg.as_string())
    except Exception, exc:
        msg_id = hex(int(email_id))[2:]
        log.debug("Exception processing %s", msg_id, exc_info=exc)
        raise Exception(msg_id)


@task()
def liberate_convert_box(result, mail_path, options):
    """ Convert maildir to mbox if needed """
    if options['storage_type'] == '0':
        pass

    elif options['storage_type'] == '1':
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

    tar_type = TAR_TYPES[options.get('compression_type', '0')]
    tar_name = "%s.%s" % (mail_path, tar_type["ext"])

    try:
        tar = tarfile.open(tar_name, tar_type['writer'])
    except (IOError, OSError), error:
        log.debug("Couldn't open tarfile at %s", tar_name)
        raise liberate_tarball.retry(exc=error)

    date = str(datetime.now(utc).date())
    dir_name = "inboxen-%s" % date

    if options['storage_type'] == '0': #MAILDIR
        try:
            tar.add("%s/" % mail_path, dir_name) # directories are added recursively by default
        finally:
            tar.close()
        rmtree(mail_path)

    elif options['storage_type'] == '1': #MBOX
        try:
            tar.add("%s.mbox" % mail_path, dir_name)
        finally:
            tar.close()
        os.remove("%s.mbox" % mail_path)

    return {'path': tar_name, 'mime-type': tar_type['mime-type'], 'date': date, 'results': result}

@task(ignore_result=True)
@transaction.atomic()
def liberation_finish(result, options):
    """ Create email to send to user """
    tags = liberate_inbox_tags(options['user'], result['date'])
    profile = liberate_user_profile(options['user'], result['results'], result['date'])

    inbox_tags = ["Inboxen", "data", "liberation"]
    inbox = Inbox.objects.filter(flags=~Inbox.flags.deleted)
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

    email = Email(inbox=inbox, received_date=datetime.now(utc))
    email.save()

    main_body = Body.objects.get_or_create(data="")[0]
    main_part = PartList(body=main_body, email=email)
    main_part.save()

    Header.objects.create(part=main_part, name="From", data="support@inboxen.org", ordinal=0)
    Header.objects.create(part=main_part, name="Subject", data=settings.LIBERATION_SUBJECT, ordinal=1)
    Header.objects.create(part=main_part, name="Content-Type", data="multipart/mixed; boundary=\"InboxenIsTheBest\"", ordinal=2)

    msg_body = Body.objects.get_or_create(data=settings.LIBERATION_BODY)[0]
    msg_part = PartList(body=msg_body, email=email, parent=main_part)
    msg_part.save()
    Header.objects.create(part=msg_part, name="Content-Type", data="text/plain", ordinal=0)

    if not options.get("noEmail", False):
        archive_body = Body.objects.get_or_create(path=result["path"])[0]
        archive_part = PartList(body=archive_body, email=email, parent=main_part)
        archive_part.save()

        cont_dispos = "attachment; filename=\"emails-{0}.{1}\"".format(result['date'], options.get('compressType', 'tar.gz'))
        Header.objects.create(part=archive_part, name="Content-Type", data=result['mime-type'], ordinal=0)
        Header.objects.create(part=archive_part, name="Content-Disposition", data=cont_dispos, ordinal=1)

    profile_body = Body.objects.get_or_create(data=profile['data'])[0]
    profile_part = PartList(body=profile_body, email=email, parent=main_part)
    profile_part.save()

    cont_dispos = "attachment; filename=\"{0}\"".format(profile['name'])
    Header.objects.create(part=profile_part, name="Content-Type", data=profile['type'], ordinal=0)
    Header.objects.create(part=profile_part, name="Content-Disposition", data=cont_dispos, ordinal=1)

    tags_body = Body.objects.get_or_create(data=tags['data'])[0]
    tags_part = PartList(body=tags_body, email=email, parent=main_part)
    tags_part.save()

    cont_dispos = "attachment; filename=\"{0}\"".format(tags['name'])
    Header.objects.create(part=tags_part, name="Content-Type", data=tags['type'], ordinal=0)
    Header.objects.create(part=tags_part, name="Content-Disposition", data=cont_dispos, ordinal=1)
    Header.objects.create(part=tags_part, name="Content-Transfer-Encoding", data="base64", ordinal=2)

    log.info("Finished liberation for %s", options['user'])

def liberate_user_profile(user_id, email_results, date):
    """ User profile data """
    data = {
        'preferences':{}
    }
    user = User.objects.get(id=user_id)


    # user's preferences
    profile = user.userprofile
    if profile.flags.prefer_html_email:
        data['preferences']['html_preference'] = 'Prefer HTML'
    else:
        data['preferences']['html_preference'] = 'Prefer plain-text'

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
        if result is not None:
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
            "deleted":inbox.flags.deleted,
            "tags":tags,
        }

    data = json.dumps(data)

    return {
        "data":data,
        "type":"application/json",
        "name":"inboxes-%s.json" % date
    }

